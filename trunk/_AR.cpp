#include <assert.h>
#include <stdio.h>
#include <stdlib.h> // malloc(), free()
#include <string.h>
#include <math.h>

#include <string>
#include <vector>
#include <iostream>

#ifdef __APPLE__
#  include <GLUT/glut.h>
#  include <OpenGL/glext.h>
#else
#  include <GL/glut.h>
#  include <GL/glext.h>
#endif

#include <CXX/Objects.hxx>
#include <CXX/Extensions.hxx>

#include "opencv/cv.h"
#include "opencv/highgui.h"

#include "ARToolKitPlus/TrackerSingleMarkerImpl.h"
#include "ARToolKitPlus/TrackerMultiMarkerImpl.h"

using namespace Py;

static int verbosity;
static void setVerbosity(int v) {
  verbosity = v;
}
static int getVerbosity() {
  return verbosity;
}

static Tuple noarg(0);

static Dict Library;

static double identTrans[3][4] = { {1,0,0,0},
                                   {0,1,0,0},
                                   {0,0,1,0} };

static CvCapture* capture;
static int frameNumber;

#define MAXMULTI 100
static ARToolKitPlus::TrackerSingleMarker *singleTracker;
static ARToolKitPlus::TrackerMultiMarker *multiTracker[MAXMULTI];
static int numMultiModels;
static int lastMultiSet[MAXMULTI];
static ARFloat lastMultiProj[MAXMULTI][16];
static ARFloat lastMultiMV[MAXMULTI][16];
static int currentMultiSet[MAXMULTI];
static ARFloat currentMultiProj[MAXMULTI][16];
static ARFloat currentMultiMV[MAXMULTI][16];
static ARFloat bestMultiMV[16];
static int freshness[MAXMULTI];

static IplImage *frame;
static CvSize *frameSize;
  
static int getWidth() {
  return (int)((Int)Library["width"]);
}
static int getHeight() {
  return (int)((Int)Library["height"]);
}
static void setWidth(int width) {
  Library["width"] = Int(width);
}
static void setHeight(int height) {
  Library["height"] = Int(height);
}
static List getMultiFileList() {
  return (List)Library["multiFile"];
}
static void setLastMultiProj(int mindex, ARFloat *matrix) {
  int i;
  lastMultiSet[mindex] = 1;
  for(i=0;i<16;i++) {
    lastMultiProj[mindex][i] = matrix[i];
  }
}
static void setLastMultiMV(int mindex, ARFloat *matrix) {
  int i;
  lastMultiSet[mindex] = 1;
  for(i=0;i<16;i++) {
    lastMultiMV[mindex][i] = matrix[i];
  }
}
static void setCurrentMultiProj(int mindex, ARFloat *matrix) {
  int i;
  currentMultiSet[mindex] = 1;
  for(i=0;i<16;i++) {
    currentMultiProj[mindex][i] = matrix[i];
  }
}
static void setCurrentMultiMV(int mindex, ARFloat *matrix) {
  int i;
  currentMultiSet[mindex] = 1;
  for(i=0;i<16;i++) {
    currentMultiMV[mindex][i] = matrix[i];
  }
}

#define GETR(_R_,_I_,_J_) _R_[_I_+4*_J_]
static void mv2quat(ARFloat *mv, ARFloat *quat) {
  ARFloat a,b,c,d,oo4a,val,r01r02,r01r12,r02r12;
  
  a = sqrt(GETR(mv,0,0) + GETR(mv,1,1) + GETR(mv,2,2)+1)*.5;
  if (a != 0) {
    oo4a = 1/(4*a);
    b = (GETR(mv,2,1) - GETR(mv,1,2))*oo4a;
    c = (GETR(mv,0,2) - GETR(mv,2,0))*oo4a;
    d = (GETR(mv,1,0) - GETR(mv,0,1))*oo4a;
  } else {
    r01r02 = GETR(mv,0,1)*GETR(mv,0,1)*GETR(mv,0,2)*GETR(mv,0,2);
    r01r12 = GETR(mv,0,1)*GETR(mv,0,1)*GETR(mv,1,2)*GETR(mv,1,2);
    r02r12 = GETR(mv,0,2)*GETR(mv,0,2)*GETR(mv,1,2)*GETR(mv,1,2);
    //printf("%.2f %.2f %.2f \n",r01r02,r01r12,r02r12);
    val = 1/sqrt(r01r02+r01r12+r02r12);
    b = GETR(mv,0,2)*GETR(mv,0,1)*val;
    c = GETR(mv,0,1)*GETR(mv,1,2)*val;
    d = GETR(mv,0,2)*GETR(mv,1,2)*val;
  }
  quat[0] = a;
  quat[1] = b;
  quat[2] = c;
  quat[3] = d;
}
static ARFloat quatDist3(ARFloat *q0, ARFloat *q1) {
  ARFloat a,b,c,d;
  b = q0[0]-q1[0];
  c = q0[0]-q1[0];
  d = q0[0]-q1[0];
  return sqrt(b*b+c*c+d*d);
}
static ARFloat quatDist4(ARFloat *q0, ARFloat *q1) {
  ARFloat a,b,c,d;
  a = q0[0]-q1[0];
  b = q0[0]-q1[0];
  c = q0[0]-q1[0];
  d = q0[0]-q1[0];
  return sqrt(a*a+b*b+c*c+d*d);
}
static ARFloat getQuatAngleDistance(ARFloat *mv0, ARFloat *mv1) {
  ARFloat quat0[4],quat1[4],ds;
  mv2quat(mv0,quat0);
  mv2quat(mv1,quat1);
  ds = quat0[0]-quat1[0];
  return sqrt(ds*ds);
}
static ARFloat getQuatDistance3(ARFloat *mv0, ARFloat *mv1) {
  ARFloat quat0[4],quat1[4],ds3;
  mv2quat(mv0,quat0);
  mv2quat(mv1,quat1);
  return quatDist3(quat0,quat1);
}
static ARFloat getQuatDistance4(ARFloat *mv0, ARFloat *mv1) {
  ARFloat quat0[4],quat1[4],ds4;
  mv2quat(mv0,quat0);
  mv2quat(mv1,quat1);
  return quatDist4(quat0,quat1);
}
static ARFloat getFrobNormDistance(ARFloat *mv0, ARFloat *mv1) {
  ARFloat ret[16],ds=0;
  for(int i=0;i<16;i++) {
    ret[i] = mv0[i]-mv1[i];
    ds += ret[i]*ret[i];
  }
  return sqrt(ds);
}

static int testDistances(int index, ARFloat *mv, ARFloat *values) {
  ARFloat ad,q3d,q4d,fnd; 
  ARFloat *last;
  if (lastMultiSet[index]) {
    last = lastMultiMV[index];
    values[0] = getQuatAngleDistance(mv,last);
    values[1] = getQuatDistance3(mv,last);
    values[2] = getQuatDistance4(mv,last);
    values[3] = getFrobNormDistance(mv,last);
    if (0) {
      printf("%d %.5f %.5f %.5f %.5f \n",index,
             values[0],values[2],values[2],values[3]);
    }
    return 1;
  }
  return 0;
}

class _ARLogger : public ARToolKitPlus::Logger
{
  void artLog(const char* nStr)
  {
    printf(nStr);
  }
};

static _ARLogger logger;

class _AR_module : public ExtensionModule<_AR_module>
{
public:
  _AR_module()
    : ExtensionModule<_AR_module>( "_AR" )
  {
    add_varargs_method("Run",
                       &_AR_module::_AR_Run,
                       "Start AR mainloop");
    add_keyword_method("GetFrame",
                       &_AR_module::_AR_GetFrame,
                       "Get current camera frame");
    add_keyword_method("GetCapture",
                       &_AR_module::_AR_GetCapture,
                       "Get camera capture object");
    add_keyword_method("GetMultiMV",
                       &_AR_module::_AR_GetMultiMV,
                       "Get multi-marker modelview matrix");
    add_keyword_method("GetSingleMV",
                       &_AR_module::_AR_GetSingleMV,
                       "Get single-marker modelview matrix");
    add_keyword_method("Init",
                       &_AR_module::_AR_Init,
                       "Initialize the AR module");
    add_varargs_method("SetSingleLoop",
                       &_AR_module::_AR_SetSingleLoop,
                       "Set the main loop for drawing single-marker objects");
    add_varargs_method("SetMultiLoop",
                       &_AR_module::_AR_SetMultiLoop,
                       "Set the main loop for drawing multi-marker objects");
    add_varargs_method("SetMultiMV",
                       &_AR_module::_AR_SetMultiMV,
                       "Set the modelview matrix for multi-marker mat");
    add_varargs_method("GetFound",
                       &_AR_module::_AR_GetFound,
                       "Returns list of markers found in the video stream");
    add_varargs_method("GetMulti",
                       &_AR_module::_AR_GetMulti,
                       "Returns info on multi-mat found in the video stream");

    initialize( "Python interface for marker-based AR system \n"
                "  Usage: ");

    Dict d( moduleDictionary() );

    d["frameCount"] = Int(0);

    // Initialized library dictionary
    Library["singleLoops"] = List();
    Library["multiLoops"] = List();

    std::cout << "AR module started" << std::endl;
  }

  virtual ~_AR_module()
  {
    std::cout << "Cleaned up AR module" << std::endl;
  }

private:
  Object _AR_GetFrame(const Tuple &a, const Dict &kws) {
    return (Int)((int)frame);
  }
  
  Object _AR_GetCapture(const Tuple &a, const Dict &kws) {
    return (Int)((int)capture);
  }
  
  Object _AR_GetSingleMV(const Tuple &a, const Dict &kws) {
    return (Int)((int)capture);
  }
  
  Object _AR_GetMultiMV(const Tuple &a, const Dict &kws) {
    int index = -1;
    List mvs = List();
    String file(a[0]);
    Dict multiDisplayDict(*Library.getItem("multiDisplayDict"));
    List mddKeys(multiDisplayDict.keys());
    for (int i=0; i<mddKeys.length(); i++) {
      String f(mddKeys[i]);
      if (f.as_string().compare(file.as_string())==0) {
        index = i;
        break;
      }
    }
    if (lastMultiSet[index]) {
      List mv = List();
      for (int i=0; i<16; i++) {
        Float val(lastMultiMV[index][i]);
        mv.append(val);
      }
      mvs.append(mv);
    } else mvs.append(Int(0));

    if (currentMultiSet[index]) {
      List mv = List();
      for (int i=0; i<16; i++) {
        Float val(currentMultiMV[index][i]);
        mv.append(val);
      } 
      mvs.append(mv);
    } else mvs.append(Int(0));
    
    return mvs;
  }
  
  
  Object _AR_Init(const Tuple &a, const Dict &kws) {
    //////////////////////////////////////////////////////////////
    // Parse arguments for Init function
    //////////////////////////////////////////////////////////////
    
    //------------------------------------------------------------
    // Verbosity
    verbosity = 0;
    if (kws.hasKey("verbosity")) {
      if (!kws["verbosity"].isNumeric())
        throw Exception("verbosity must be an integer");
      setVerbosity((int)((Int)kws["verbosity"]));
    }
    // Python initializer function that the user wants
    if(kws.hasKey("initFunc")) {
      if (!kws["initFunc"].isCallable()) {
        throw Exception("initFunc must be a callable object");
      }
      Callable initFunc(kws["initFunc"]);
      Library["initFunc"] = initFunc;
    }
    // Pre-rendering python function to be called before rendering
    // happens
    if(kws.hasKey("preRender")) {
      if (!kws["preRender"].isCallable()) {
        throw Exception("preRender must be a callable object");
      }
      Callable preRender(kws["preRender"]);
      Library["preRender"] = preRender;
    }
    // Rendering python function to be called instead of the default
    // renderFrame function
    if(kws.hasKey("render")) {
      if (!kws["render"].isCallable()) {
        throw Exception("render must be a callable object");
      }
      Callable render(kws["render"]);
      Library["render"] = render;
    }
    // Pre-drawing python function to be called before drawing
    // of markers
    if(kws.hasKey("preDraw")) {
      if (!kws["preDraw"].isCallable()) {
        throw Exception("preDraw must be a callable object");
      }
      Callable preDraw(kws["preDraw"]);
      Library["preDraw"] = preDraw;
    }
    // Post-rendering python function to be called before rendering
    // happens
    if(kws.hasKey("postRender")) {
      if (!kws["postRender"].isCallable()) {
        throw Exception("postRender must be a callable object");
      }
      Callable postRender(kws["postRender"]);
      Library["postRender"] = postRender;
    }
    //------------------------------------------------------------

    
    //------------------------------------------------------------
    // Tracker settings
    //
    // Single-marker display dictionary
    //    dictionary of integer id keys corresponding to display
    //    functions for those markers
    Library["singleDisplayDict"] = Dict();
    if (kws.hasKey("singleDisplayDict")) {
      if (!kws["singleDisplayDict"].isDict())
        throw Exception("singleDisplayDict must be a dictionary");
      Dict singleDisplayDict(*kws["singleDisplayDict"]);
      Library["singleDisplayDict"] = singleDisplayDict;
    }
    // Multi-marker configuration file(s)
    numMultiModels = 0;
    Library["multiDisplayDict"] = Dict();
    Library["mddKeys"] = List();
    if (kws.hasKey("multiDisplayDict")) {
      if (!kws["multiDisplayDict"].isDict())
        throw Exception("multiDisplayDict must be a dictionary");
      Dict multiDisplayDict(*kws["multiDisplayDict"]);
      Library["multiDisplayDict"] = multiDisplayDict;
      List mddKeys(multiDisplayDict.keys());
      Library["mddKeys"] = mddKeys;
      numMultiModels = mddKeys.length();
    }
    // Threshold
    Int threshold(80);
    Library["threshold"] = threshold;
    if (kws.hasKey("threshold")) {
      threshold = kws["threshold"];
      std::cout << "Setting threshold to: " << (int)threshold << std::endl;
      Library["threshold"] = threshold;
    }
    //------------------------------------------------------------
    //////////////////////////////////////////////////////////////
    
    //////////////////////////////////////////////////////////////
    // Window settings 
    //////////////////////////////////////////////////////////////
    Library["width"] = Int(640);
    if (kws.hasKey("width")) {
      Library["width"] = Int(kws["width"]);
    }
    Library["height"] = Int(480);
    if (kws.hasKey("height")) {
      Library["height"] = Int(kws["height"]);
    }
    //////////////////////////////////////////////////////////////


    //////////////////////////////////////////////////////////////
    // Initialize camera
    //////////////////////////////////////////////////////////////
    capture = cvCaptureFromCAM( 0 );
    if( !capture ) {
      throw Exception("Init: Unable to set up AR camera.");
    }
    frameNumber = 0;
    frameSize = new CvSize();
    frameSize->width = getWidth();
    frameSize->height = getHeight();
    printf ("Width: %d Height: %d\n",frameSize->width,frameSize->height);
    //////////////////////////////////////////////////////////////
    

    //////////////////////////////////////////////////////////////
    // Initialize trackers
    //////////////////////////////////////////////////////////////
    // single-marker
    printf("Initializing ARToolKitPlus markers\n");
    singleTracker = new ARToolKitPlus::TrackerSingleMarkerImpl<6,6,6,\
      ARToolKitPlus::PIXEL_FORMAT_RGB,16>(getWidth(),getHeight());
    // Setup tracker
    singleTracker->setLogger(&logger);
    singleTracker->init("data/LogitechPro4000.dat", 1.0f, 10000.0f);
    singleTracker->setPatternWidth(60);
    singleTracker->setBorderWidth(0.125f);
    singleTracker->setThreshold((int)((Int)Library["threshold"]));
    singleTracker->setUndistortionMode(ARToolKitPlus::UNDIST_LUT);
    singleTracker->setPoseEstimator(ARToolKitPlus::POSE_ESTIMATOR_RPP);
    singleTracker->setMarkerMode(ARToolKitPlus::MARKER_ID_BCH);
    // multi-marker
    Dict multiDisplayDict(*Library.getItem("multiDisplayDict"));
    List mddKeys(Library["mddKeys"]);
    for(int i=0;i<mddKeys.length();i++) {
      String file(mddKeys[i]);
      int w=getWidth(), h=getHeight();
      std::cout << "Initializing multi tracker: " << i
                << " for file: " << file.as_string() 
                << std::endl;
      multiTracker[i] = new ARToolKitPlus::TrackerMultiMarkerImpl<6,6,6, ARToolKitPlus::PIXEL_FORMAT_RGB, 16>(w,h);
      multiTracker[i]->setLogger(&logger);
      const char* description = multiTracker[i]->getDescription();
      printf("ARToolKitPlus compile-time information:\n%s\n\n", description);
      int initVal = multiTracker[i]->init("data/LogitechPro4000.dat",
                            file.as_string().c_str(), 1.0f, 10000.0f);
      printf("Init return value: %d\n",initVal); 
      multiTracker[i]->setBorderWidth(0.125f);
      multiTracker[i]->setThreshold((int)((Int)Library["threshold"]));
      multiTracker[i]->setPoseEstimator(ARToolKitPlus::POSE_ESTIMATOR_RPP);
      multiTracker[i]->setMarkerMode(ARToolKitPlus::MARKER_ID_BCH);
    }
    //////////////////////////////////////////////////////////////

    int argc = 0;
    char **argv = NULL;
    glutInit(&argc, argv);
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH);
    glutInitWindowSize(getWidth(), getHeight());

    return Int(0);
  }

  Object _AR_Run(const Tuple &a) {

    glutCreateWindow("ADVANCE");
    glutDisplayFunc(display);
    glutIdleFunc(display);
    glutReshapeFunc(reshape);

    //glutKeyboardFunc(keyboard);
    //glutSpecialFunc(special);

    GLuint mTexture;
    glGenTextures(1, &mTexture);
    glBindTexture(GL_TEXTURE_2D, mTexture);
    glEnable(GL_TEXTURE_2D);
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP);	
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP);

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL);

    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
    glColor3f(1,1,1);

    // Call python-specified init function if it exists    
    if (Library.hasKey("initFunc")) {
      if (Library["initFunc"].isCallable()) {
        std::cout << "Calling python init func" << std::endl;
        Callable initFunc(Library["initFunc"]);
        initFunc.apply(noarg);
      }
    } else 
      std::cout << "DEAD INIT FUNC!!!!" << std::endl;
    
    glViewport(0, 0, getWidth(), getHeight());

    glutMainLoop();
    std::cout << "Done with GUI... exiting\n";
    return Int(0);
  }

  static void reshape(int w, int h) {
    setWidth(w);
    setHeight(h);
    glViewport(0, 0, w, h);
    
  }

  static void renderFrame( IplImage *frame ) {
    glEnable(GL_TEXTURE_2D);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB,getWidth(),getHeight(),0,
                 GL_BGR,GL_UNSIGNED_BYTE, frame->imageData);

    float z = 0;

    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();

    glMatrixMode(GL_MODELVIEW);
    glPushMatrix();
    glLoadIdentity();
    glBegin(GL_POLYGON);
    glTexCoord2f(0.0f, 1.0f); glVertex3f(-1.0f, -1.0f, z);
    glTexCoord2f(1.0f, 1.0f); glVertex3f( 1.0f, -1.0f, z);
    glTexCoord2f(1.0f, 0.0f); glVertex3f( 1.0f,  1.0f, z);
    glTexCoord2f(0.0f, 0.0f); glVertex3f(-1.0f,  1.0f, z);
    /*
      glTexCoord2f(0.0f, 0.0f); glVertex2f(-1.0f, -1.0f);
      glTexCoord2f(1.0f, 0.0f); glVertex2f( 1.0f, -1.0f);
      glTexCoord2f(1.0f, 1.0f); glVertex2f( 1.0f,  1.0f);
      glTexCoord2f(0.0f, 1.0f); glVertex2f(-1.0f,  1.0f);
    */
    glEnd();
    glPopMatrix();
	
    glFlush();
    glDisable(GL_TEXTURE_2D);
  }

  static void display() {
    int i,j,k;

    frame = cvQueryFrame( capture );
    if( !frame ) {
      throw Exception("Camera frame is null..");
    }
    frameNumber += 1;
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    ///////////////////////////////
    // Image preprocessing
    
    // Call python-specified pre-render function if it exists    
    if (Library.hasKey("preRender")) {
      Callable preRender(Library["preRender"]);
      try {
        preRender.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
      }
    }

    ///////////////////////////////
    // Draw Image
    // Call python-specified pre-render function if it exists    
    if (Library.hasKey("render")) {
      Callable render(Library["render"]);
      try {
        render.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
      }
    } else {
      renderFrame(frame);
    }

    ///////////////////////////////
    // Tracking

    // --------------------------------
    // Single-marker tracking
    Dict singleDisplayDict(*Library.getItem("singleDisplayDict"));
    List sddKeys(singleDisplayDict.keys());
    for (i=0;i<sddKeys.length();i++) {
      int mId = (int)((Int)sddKeys[i]);
      int markerId = singleTracker->calc((unsigned char *)(frame->imageData),
                                         mId);
      float conf = singleTracker->getConfidence();
      if (conf>0) {
        // We've found a marker
        glMatrixMode(GL_PROJECTION);
        glLoadMatrixf(singleTracker->getProjectionMatrix());

        if (0) {
          printf("\n\nFound marker %d  (confidence %d%%)\n\nPose-Matrix:\n  ",
                 markerId, (int(conf*100.0f)));

          for(int i=0; i<16; i++) {
            printf("%.2f  %s",
                   singleTracker->getModelViewMatrix()[i],
                   (i%4==3)?"\n  " : "");
          }
        }
        
        glMatrixMode(GL_MODELVIEW);
        glLoadMatrixf(singleTracker->getModelViewMatrix());
        Callable displayFunc(singleDisplayDict[sddKeys[i]]);
        displayFunc.apply(noarg);
      }
    }
    // --------------------------------

    // --------------------------------
    // Multi-marker tracking
    Dict multiDisplayDict(*Library.getItem("multiDisplayDict"));
    List mddKeys(Library["mddKeys"]);
    ARFloat quat[4],lquat[4],qds;
    for (int i=0; i<mddKeys.length(); i++) {
      int num = 0;
      num = multiTracker[i]->calc((unsigned char *)(frame->imageData));
      ARFloat *proj,*model;
      if (num) {
        proj = (ARFloat *)multiTracker[i]->getProjectionMatrix();
        setCurrentMultiProj(i,proj);
        if (getVerbosity()>1) {
          printf("\n%d good Markers found and used for pose estimation."
                 "\nPose-Matrix:\n  ", num);
          for(int j=0; j<16; j++)
            printf("%.2f  %s", multiTracker[i]->getModelViewMatrix()[j],
                   (j%4==3)?"\n  " : "");
        }
        model = (ARFloat *)multiTracker[i]->getModelViewMatrix();
        
        //testDistances(i,model);

        setCurrentMultiMV(i,model);

        freshness[i] = frameNumber;
      }
      
    }

    // Call python-specified pre-draw function if it exists    
    if (Library.hasKey("preDraw")) {
      Callable preDraw(Library["preDraw"]);
      try {
        preDraw.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
      }
    }

    for (int i=0;i<mddKeys.length();i++) {
      Callable displayFunc(multiDisplayDict[mddKeys[i]]);
      if (currentMultiSet[i]) {
        if ((frameNumber - freshness[i]) < 8) {
          glMatrixMode(GL_PROJECTION);
          glLoadMatrixf(currentMultiProj[i]);
        
          //glMatrixMode(GL_MODELVIEW);
          //glLoadMatrixf(currentMultiMV[i]);
          displayFunc.apply(noarg);
        } else {
          currentMultiSet[i] = 0;
          lastMultiSet[i] = 0;
        }
      }
    }
    
    // Call python-specified pre-render function if it exists    
    if (Library.hasKey("postRender")) {
      Callable postRender(Library["postRender"]);
      try {
        postRender.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
      }
    }
    // --------------------------------

    // Set last multi MV
    for (int i=0;i<mddKeys.length();i++) {
      if (currentMultiSet[i]) {
        setLastMultiMV(i,currentMultiMV[i]);
        setLastMultiProj(i,currentMultiProj[i]);
      }
    }

    ///////////////////////////////
    // OpenGL prep
    glClearDepth( 1.0 );
    glClear(GL_DEPTH_BUFFER_BIT);

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    drawMulti();
    drawSingle();

    glDisable(GL_DEPTH_TEST);

    glutSwapBuffers();

  }

  Tuple pytrans(double trans[3][4]) {
    Tuple ptrans(3);
    int i,j;
    for (i=0;i<3;i++) {
      Tuple inner(4);
      for (j=0;j<4;j++)
        inner[j] = Float(trans[i][j]);
      ptrans[i] = inner;
    }
    return ptrans;
  }

  Object _AR_GetFound(const Tuple &a) {
    /*
      typedef struct {
      char   name[256];
      int    id;
      int    visible;
      int	 collide;
      double pos[2];
      double marker_coord[4][2];
      double trans[3][4];
      double marker_width;
      double marker_center[2];
      } ObjectData_T;
    */
    int i,j,k;
    if (a.size() > 0) 
      throw Exception("No arguments");

    int nFound,mid;
    List markers;
    double gl_para[16];
    /*
      if ((nFound=tracker.GetFound(foundIds)) > 0) {
      for (i=0;i<nFound;i++) {
      mid = foundIds[i];
      marker = tracker.GetFound(mid);
      Dict mdict;
      mdict["id"] = Int(mid);
      mdict["name"] = String(marker.name);
      Tuple pos(2);
      pos[0] = Float(marker.pos[0]);
      pos[1] = Float(marker.pos[1]);
      mdict["pos"] = pos;
      mdict["trans"] = pytrans(marker.trans);
      argConvGlpara(marker.trans, gl_para);
      Tuple mvmat(16);
      for(j=0;j<16;j++){
      mvmat[j] = Float(gl_para[j]);
      }
      mdict["mvmat"] = mvmat;
      Tuple xyz(3);
      for(j=0;j<3;j++) {
      xyz[j]=Float(gl_para[12+j]);
      }
      mdict["xyz"] = xyz;
      markers.append(mdict);
      }
      }
    */
    return (Object) markers;
  }

  Object _AR_GetMulti(const Tuple &a) {
    int i,j,k;
    if (a.size() > 0) 
      throw Exception("No arguments");

    Dict pymulti;

    /*
      ARMultiMarkerInfoT *multi = tracker.GetMulti();
      pymulti["err"] = Float(tracker.GetMultiErr());
      pymulti["trans"] = pytrans(multi->trans);

      double gl_para[16];
      Tuple mvmat(16);
      argConvGlpara(multi->trans, gl_para);
      for(i=0;i<16;i++){
      mvmat[i] = Float(gl_para[i]);
      }
      pymulti["mvmat"] = mvmat;
    */
    
    return (Object) pymulti;
  }

  Object _AR_SetMultiLoop(const Tuple &a) {
    if (! (a[0].isCallable()) )
      throw Exception("Single argument must be a function");
    
    Callable f(a[0]);
    //f.apply(Tuple(0));
    List multi(Library["multiLoops"]);
    multi.append(f);
    
    return Int(0);
  }

  Object _AR_SetSingleLoop(const Tuple &a) {
    if (! (a[0].isCallable()) )
      throw Exception("Single argument must be a function");
    
    Callable f(a[0]);
    List single(Library["singleLoops"]);
    single.append(f);
    
    return Int(0);
  }

  Object _AR_SetMultiMV(const Tuple &a) {
    /*
      argDrawMode3D();
      argDraw3dCamera( 0, 0 );
      glMatrixMode(GL_MODELVIEW);
      double    gl_para[16];
      argConvGlpara(multi->trans, gl_para);
      glLoadMatrixd( gl_para );
    */
    
    return Int(0);
  }

  static void takeCvNormalScreenCap() {
    /*
      IplImage *normal = arcv.GetOriginal();
      std::cout << normal << std::endl;
      std::cout << cvSaveImage("cvScreenCapNormal.jpg",normal) << std::endl;
    */
  }
  static void takeCvGrayScreenCap() {
    /*
      IplImage *gray = arcv.GetGrayscale();
      std::cout << gray << std::endl;
      std::cout << cvSaveImage("cvScreenCapGray.jpg",gray) << std::endl;
    */
  }
  
  static void Keyboard(unsigned char key, int x, int y) {
    switch (key) {
      /*
        case 'c':
        takeCvNormalScreenCap();
        break;
        case 'g':
        takeCvGrayScreenCap();
        break;
      */
    case 0x1B:  // Quit.
    case 'Q':
    case 'q':
      /*
        arcv.CleanUp();
        setup.CleanUp();
      */
      exit(0);
      break;
    default:
      break;
    }
  }

  static int drawSingle() {
    // Draw Python single marker loops
    List single(Library["singleLoops"]);
    for(int i=0;i<single.size();i++) {
      Callable f(single[i]);
      try {
        f.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
        return 0;
      }
    }
    return 1;
  }

  static int drawMulti() {
    // Draw Python multi loop
    List mloop(Library["multiLoops"]);
    for(int i=0;i<mloop.size();i++) {
      Callable f(mloop[i]);
      try{
        f.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
        return 0;
      }
    }
    return 1;
  }

  
};

extern "C" void init_AR()
{
#if defined(PY_WIN32_DELAYLOAD_PYTHON_DLL)
  InitialisePythonIndirectPy::Interface();
#endif

  static _AR_module* _AR = new _AR_module;
}

// symbol required for the debug version
extern "C" void init_AR_d()
{ init_AR(); }
