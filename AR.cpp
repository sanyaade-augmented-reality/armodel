#include "framework.hpp"

#include <CXX/Objects.hxx>
#include <CXX/Extensions.hxx>

using namespace Py;

static ARSetup setup = ARSetup();
static MarkerTracker tracker = MarkerTracker();
static ARUint8 *imageData = NULL;
static Tuple noarg(0);

static int foundIds[100];

static Dict Library;

static double identTrans[3][4] = { {1,0,0,0},
                                   {0,1,0,0},
                                   {0,0,1,0} };

static void draw( double trans1[3][4], double trans2[3][4], int mode )
{
    double    gl_para[16];
    GLfloat   mat_ambient[]     = {0.0, 0.0, 1.0, 1.0};
    GLfloat   mat_ambient1[]    = {1.0, 0.0, 0.0, 1.0};
    GLfloat   mat_flash[]       = {0.0, 0.0, 1.0, 1.0};
    GLfloat   mat_flash1[]      = {1.0, 0.0, 0.0, 1.0};
    GLfloat   mat_flash_shiny[] = {50.0};
    GLfloat   mat_flash_shiny1[]= {50.0};
    GLfloat   light_position[]  = {100.0,-200.0,200.0,0.0};
    GLfloat   ambi[]            = {0.1, 0.1, 0.1, 0.1};
    GLfloat   lightZeroColor[]  = {0.9, 0.9, 0.9, 0.1};
    
    argDrawMode3D();
    argDraw3dCamera( 0, 0 );
//     glEnable(GL_DEPTH_TEST);
//     glDepthFunc(GL_LEQUAL);
    
    /* load the camera transformation matrix */
    glMatrixMode(GL_MODELVIEW);
    argConvGlpara(trans1, gl_para);
    glLoadMatrixd( gl_para );
    argConvGlpara(trans2, gl_para);
    glMultMatrixd( gl_para );

    if( mode == 0 ) {
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_POSITION, light_position);
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambi);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor);
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_flash);
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_flash_shiny);	
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
    }
    else {
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_POSITION, light_position);
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambi);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor);
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_flash1);
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_flash_shiny1);	
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient1);
    }
    glMatrixMode(GL_MODELVIEW);
    //glTranslatef( 0.0, 0.0, 25.0 );
    //glutSolidCube(50.0);
    glBegin(GL_POLYGON);
    glVertex3f(-25,-25,0);
    glVertex3f(-25,25,0);
    glVertex3f(25,25,0);
    glVertex3f(25,-25,0);
    glEnd();
    glTranslatef( 0.0, 0.0, 0.0 );
    glutSolidCone(10,50,20,20);
    glDisable( GL_LIGHTING );

//     glDisable( GL_DEPTH_TEST );
}

class AR_module : public ExtensionModule<AR_module>
{
public:
  AR_module()
    : ExtensionModule<AR_module>( "AR" )
  {
    add_varargs_method("Run",
                       &AR_module::AR_Run,
                       "Start AR mainloop");
    add_keyword_method("Init",
                       &AR_module::AR_Init,
                       "Initialize the AR module");
    add_varargs_method("SetSingleLoop",
                       &AR_module::AR_SetSingleLoop,
                       "Set the main loop for drawing single-marker objects");
    add_varargs_method("SetMultiLoop",
                       &AR_module::AR_SetMultiLoop,
                       "Set the main loop for drawing multi-marker objects");
    add_varargs_method("SetMultiMV",
                       &AR_module::AR_SetMultiMV,
                       "Set the modelview matrix for multi-marker mat");
    add_varargs_method("GetFound",
                       &AR_module::AR_GetFound,
                       "Returns list of markers found in the video stream");
    add_varargs_method("GetMulti",
                       &AR_module::AR_GetMulti,
                       "Returns info on multi-mat found in the video stream");

    add_varargs_method("argDrawMode3D",
                       &AR_module::AR_argDrawMode3D,
                       "Wrap of argDrawMode3D");
    add_varargs_method("argDraw3dCamera",
                       &AR_module::AR_argDraw3dCamera,
                       "Wrap of argDraw3dCamera");
    add_varargs_method("argConvGlpara",
                       &AR_module::AR_argConvGlpara,
                       "Wrap of argConvGlpara");
    add_varargs_method("Draw",
                       &AR_module::AR_Draw,
                       "Start AR mainloop");
    
    initialize( "Python interface for marker-based AR system \n"
                "  Usage: ");

    Dict d( moduleDictionary() );

    d["frameCount"] = Int(0);

    // Initialized library dictionary
    Library["singleLoops"] = List();
    Library["multiLoops"] = List();

    std::cout << "AR module started" << endl;
  }

  virtual ~AR_module()
  {
    std::cout << "Cleaned up AR module" << endl;
  }

private:

  Object AR_Init(const Tuple &a, const Dict &kws) {
    // Python Initializer
    if(kws.hasKey("initFunc")) {
      Callable initFunc(kws["initFunc"]);
      Library["initFunc"] = initFunc;
    }
    
    // Setup settings
    if(kws.hasKey("vconf")) {
      String vconf = String(kws["vconf"]);
      std::string vc = vconf.as_std_string();
      std::cout << vc << endl;
      setup.SetVconf(vc);
    }
    if (kws.hasKey("zoom")) {
      Float zoom = Float(kws["zoom"]);
      setup.SetZoom((double)zoom);
    }
    if (kws.hasKey("fullScreen")) {
      Int fs = Int(kws["fullScreen"]);
      setup.SetFullScreen((int)fs);
    }

    // Tracker settings
    if (kws.hasKey("modelName")) {
      String val(kws["modelName"]);
      tracker.SetModelName(val.as_string());
    }
    if (kws.hasKey("multiModelName")) {
      String val(kws["multiModelName"]);
      tracker.SetMultiModelName(val.as_string());
    }
    if (kws.hasKey("threshold")) {
      Int val(kws["threshold"]);
      tracker.SetThreshold((int) val);
    }

    int argc = 0;
    char **argv = NULL;
    glutInit(&argc, argv);
    if (!(setup.SetupCamera())) {
      throw Exception("Init: Unable to set up AR camera.");
    }
    if (!(tracker.InitTracker())) {
      std::cout << "Problem with init tracker!" << endl;
      setup.CleanUp();
      throw Exception("Init: Unable to set up MarkerTracker.");
    }
    tracker.SetThreshold(85);

    return Int(0);
  }

  Object AR_Draw(const Tuple &a) {
    int index,i,j;
    Int pyindex;
    double trans[3][4];
    
    pyindex = a[0];
    index = pyindex;

    argDrawMode3D();
    argDraw3dCamera( 0, 0 );
//     glClearDepth( 1.0 );
//     glClear(GL_DEPTH_BUFFER_BIT);
    tracker.GetTrans(index,trans);
    draw(trans,identTrans,0);
    
    return Int(0);
  }

  Object AR_argDrawMode3D(const Tuple &a) {
    argDrawMode3D();
    return Int(0);
  }

  Object AR_argDraw3dCamera(const Tuple &a) {
    Int a1(a[0]),a2(a[1]);
    argDraw3dCamera((int)a1,(int)a2);
    return Int(0);
  }

  Object AR_argConvGlpara(const Tuple &a) {
    Tuple trans(a[0]),glpara(16);
    double gl_para[16],ctrans[3][4];
    int i,j;
    for(i=0;i<3;i++) {
      Tuple inner(trans[i]);
      for(j=0;j<4;j++) {
        Float val(inner[j]);
        ctrans[i][j] = (double) val;
      }
    }
    argConvGlpara(ctrans, gl_para);
    for(i=0;i<16;i++)
      glpara[i] = Float(gl_para[i]);
    return (Object) glpara;
  }

  Object AR_SetMarkerMV(const Tuple &a) {
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
  Object AR_GetFound(const Tuple &a) {
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
    ObjectData_T marker;
    double gl_para[16];
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
    return markers;
  }

  Object AR_GetMulti(const Tuple &a) {
    int i,j,k;
    if (a.size() > 0) 
      throw Exception("No arguments");

    Dict pymulti;
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
    
    return (Object) pymulti;
  }

  Object AR_Run(const Tuple &a) {
    setup.SetupWindow();

    if (!(setup.StartCamera())) {
      throw Exception("Init: Unable to start AR camera.");
    }

    if (Library.hasKey("initFunc")) {
      std::cout << "INIT FUNC!!!!\n";
      if (Library["initFunc"].isCallable()) {
        Callable initFunc(Library["initFunc"]);
        initFunc.apply(noarg);
      }
    } else 
      std::cout << "DEAD INIT FUNC!!!!\n";
    
    argMainLoop( NULL, Keyboard, MainLoop );
    return Int(0);
  }

  Object AR_SetMultiLoop(const Tuple &a) {
    if (! (a[0].isCallable()) )
      throw Exception("Single argument must be a function");
    
    Callable f(a[0]);
    //f.apply(Tuple(0));
    List multi(Library["multiLoops"]);
    multi.append(f);
    
    return Int(0);
  }

  Object AR_SetSingleLoop(const Tuple &a) {
    if (! (a[0].isCallable()) )
      throw Exception("Single argument must be a function");
    
    Callable f(a[0]);
    List single(Library["singleLoops"]);
    single.append(f);
    
    return Int(0);
  }

  Object AR_SetMultiMV(const Tuple &a) {
    ARMultiMarkerInfoT *multi = tracker.GetMulti();
    
    argDrawMode3D();
    argDraw3dCamera( 0, 0 );
    glMatrixMode(GL_MODELVIEW);
    double    gl_para[16];
    argConvGlpara(multi->trans, gl_para);
    glLoadMatrixd( gl_para );
    
    return Int(0);
  }

  static void Keyboard(unsigned char key, int x, int y) {
    switch (key) {
    case 0x1B:  // Quit.
    case 'Q':
    case 'q':
      setup.CleanUp();
      exit(0);
      break;
    default:
      break;
    }
  }

  static void MainLoop() {
    int i,j,k;
    if( (imageData = (ARUint8 *)arVideoGetImage()) == NULL ) {
      arUtilSleep(2);
      return;
    }

    // Tracking
    tracker.Track(imageData);
    int nFound,foundIds[10];
    if ((nFound=tracker.GetFound(foundIds)) > 0) {
      for (i=0;i<nFound;i++) {
      }
    }

    // Draw Image
    ARParam *cparam = setup.GetCParam();
    argDrawMode2D();
    arglDispImage( imageData,cparam,1.0,setup.GetArglSettings());

    arVideoCapNext();
    // Image data is no longer valid after calling arVideoCapNext().
    imageData = NULL;

    glClearDepth( 1.0 );
    glClear(GL_DEPTH_BUFFER_BIT);

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    ARMultiMarkerInfoT *multi = tracker.GetMulti();
    if (tracker.GetMultiErr() < 0) {
      argSwapBuffers();
      return;
    }
    if(tracker.GetMultiErr() > 100.0 ) {
      argSwapBuffers();
      return;
    }

    // Draw Python multi loop
    List mloop(Library["multiLoops"]);
    for(i=0;i<mloop.size();i++) {
      Callable f(mloop[i]);
      try{
        f.apply(noarg);
      } catch  (Exception &e){
        std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
        PyErr_Print();
        //e.clear();
        return;
      }
    }

    // Draw Python single marker loops
    List single(Library["singleLoops"]);
    for(i=0;i<single.size();i++) {
      Callable f(single[i]);
       try {
        f.apply(noarg);
       } catch  (Exception &e){
         std::cout << std::endl << "!!!!!!!ERROR!!!!!!!! " << std::endl;
         PyErr_Print();
         //e.clear();
         return;
       }
    }
      

    glDisable(GL_DEPTH_TEST);
    argSwapBuffers();
  }
  
};

extern "C" void initAR()
{
#if defined(PY_WIN32_DELAYLOAD_PYTHON_DLL)
  InitialisePythonIndirectPy::Interface();
#endif

  static AR_module* AR = new AR_module;
}

// symbol required for the debug version
extern "C" void initAR_d()
{ initAR(); }
