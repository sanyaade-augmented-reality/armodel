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
static ARToolKitPlus::TrackerSingleMarker *singleTracker;
static ARToolKitPlus::TrackerMultiMarker *multiTracker[100];
static IplImage *frame;
static IplImage *grayFrame;
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
    add_keyword_method("GetImage",
                       &_AR_module::_AR_GetImage,
                       "Get current camera frame");
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
  Object _AR_GetImage(const Tuple &a, const Dict &kws) {
    return (Int)((int)frame);
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
    Library["multiDisplayDict"] = Dict();
    if (kws.hasKey("multiDisplayDict")) {
      if (!kws["multiDisplayDict"].isDict())
        throw Exception("multiDisplayDict must be a dictionary");
      Dict multiDisplayDict(*kws["multiDisplayDict"]);
      Library["multiDisplayDict"] = multiDisplayDict;
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
    frameSize = new CvSize();
    frameSize->width = getWidth();
    frameSize->height = getHeight();
    printf ("Width: %d Height: %d\n",frameSize->width,frameSize->height);
    grayFrame = cvCreateImage(*frameSize,IPL_DEPTH_8U, 1);
    //////////////////////////////////////////////////////////////
    

    //////////////////////////////////////////////////////////////
    // Initialize trackers
    //////////////////////////////////////////////////////////////
    // single-marker
    singleTracker = new ARToolKitPlus::TrackerSingleMarkerImpl<6,6,6,\
      ARToolKitPlus::PIXEL_FORMAT_RGB,16>(getWidth(),getHeight());
    // Setup tracker
    singleTracker->setLogger(&logger);
    singleTracker->init("Data/LogitechPro4000.dat", 1.0f, 1000.0f);
    singleTracker->setPatternWidth(60);
    singleTracker->setBorderWidth(0.125f);
    singleTracker->setThreshold((int)((Int)Library["threshold"]));
    singleTracker->setUndistortionMode(ARToolKitPlus::UNDIST_LUT);
    singleTracker->setPoseEstimator(ARToolKitPlus::POSE_ESTIMATOR_RPP);
    singleTracker->setMarkerMode(ARToolKitPlus::MARKER_ID_BCH);
    // multi-marker
    Dict multiDisplayDict(*Library.getItem("multiDisplayDict"));
    List mddKeys(multiDisplayDict.keys());
    for(int i=0;i<mddKeys.length();i++) {
      String file(mddKeys[i]);
      std::cout << "Initializing multi tracker: " << i
                << " for file: " << file.as_string() 
                << std::endl;
      multiTracker[i] = new ARToolKitPlus::TrackerMultiMarkerImpl<6,6,6, \
        ARToolKitPlus::PIXEL_FORMAT_RGB, 16>(getWidth(),getHeight());
      multiTracker[i]->init("data/LogitechPro4000.dat",
                            file.as_string().c_str(), 1.0f, 1000.0f);
      //multiTracker[i]->setPatternWidth(60);
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

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    ///////////////////////////////
    // Image preprocessing
    
    //cvCvtColor(frame, grayFrame, CV_RGBA2GRAY);

    // Call python-specified pre-render function if it exists    
    if (Library.hasKey("preRender")) {
      if (getVerbosity()>0) {
        std::cout << "Calling python init func" << std::endl;
      }
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
      if (getVerbosity()>0) {
        std::cout << "Calling python init func" << std::endl;
      }
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
    List mddKeys(multiDisplayDict.keys());
    for (int i=0; i<mddKeys.length(); i++) {
      std::cout << "here2" << std::endl;
      int num = multiTracker[i]->calc((unsigned char *)(frame->imageData));
      std::cout << "here3" << std::endl;
      if (num) {
        glMatrixMode(GL_PROJECTION);
        glLoadMatrixf(multiTracker[i]->getProjectionMatrix());
        if (0) {
          printf("\n%d good Markers found and used for pose estimation.\nPose-Matrix:\n  ", num);
          for(int j=0; j<16; j++)
            printf("%.2f  %s", multiTracker[i]->getModelViewMatrix()[j],
                   (j%4==3)?"\n  " : "");
        }
        glMatrixMode(GL_MODELVIEW);
        glLoadMatrixf(multiTracker[i]->getModelViewMatrix());
        Callable displayFunc(multiDisplayDict[mddKeys[i]]);
        displayFunc.apply(noarg);
      }
      std::cout << "here4" << std::endl;
      
      // Call python-specified pre-render function if it exists    
      if (Library.hasKey("postRender")) {
        if (getVerbosity()>0) {
          std::cout << "Calling python init func" << std::endl;
        }
        Callable postRender(Library["postRender"]);
        try {
          postRender.apply(noarg);
        } catch  (Exception &e){
          std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
          PyErr_Print();
          //e.clear();
        }
        std::cout << "here5" << std::endl;
      }
      std::cout << "here6" << std::endl;
    }
    
    // --------------------------------
    

    ///////////////////////////////
    // OpenGL prep
    glClearDepth( 1.0 );
    glClear(GL_DEPTH_BUFFER_BIT);

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    // If we can't see the multi-marker palette, just draw the found
    // single-marker wand
    /*
      if ((tracker.GetMultiErr() < 0) || (tracker.GetMultiErr() > 100.0 )) {
      drawSingle();
      argSwapBuffers();
      return;
      }
    */

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
