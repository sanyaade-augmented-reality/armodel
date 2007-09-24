#include "ARSetup.hpp"

ARSetup::ARSetup() {
  view_scalefactor=0.025;
  view_distance_min=0.1; 
  view_distance_max=100.0;
  isInit = 0;
//   strcpy(cparam_name,"Data/camera_para.dat");
  cparam_name = "/Users/dogwynn/AR/Data/camera_para.dat";
#ifdef _WIN32
  vconf="Data\\WDM_camera_flipV.xml";
#else
  vconf="";
#endif

  zoom = 1.0;
  fullScreen = 0;
  xwin = 0; ywin = 0;
  hmdFlag = 0;
}

int ARSetup::SetupWindow() {
  argInit( &cparam, zoom, fullScreen, xwin, ywin, hmdFlag );

  if ((myArglSettings = arglSetupForCurrentContext()) == NULL) {
    fprintf(stderr, "main(): arglSetupForCurrentContext() returned error.\n");
    exit(-1);
  }
}

int ARSetup::SetupCamera() {
  ARParam			wparam;
  int				xsize, ysize;

  // Open the video path.
  if (arVideoOpen((char *)vconf.c_str()) < 0) {
    fprintf(stderr, "setupCamera(): Unable to open connection to camera.\n");
    return (FALSE);
  }
	
  // Find the size of the window.
  if (arVideoInqSize(&xsize, &ysize) < 0) return (FALSE);
  fprintf(stdout, "Camera image size (x,y) = (%d,%d)\n", xsize, ysize);
	
  // Load the camera parameters, resize for the window and init.
  if (arParamLoad(cparam_name.c_str(), 1, &wparam) < 0) {
    fprintf(stderr, "setupCamera(): Error loading parameter file %s for camera.\n", cparam_name.c_str());
    return (FALSE);
  }
  arParamChangeSize(&wparam, xsize, ysize, &cparam);
  fprintf(stdout, "*** Camera Parameter ***\n");
  arParamDisp(&cparam);
	
  arInitCparam(&cparam);

  isInit = 1;
  return (TRUE);
}

void ARSetup::CleanUp () {
  arglCleanup(myArglSettings);
  arVideoCapStop();
  arVideoClose();
}

void ARSetup::MainLoop () {
}
