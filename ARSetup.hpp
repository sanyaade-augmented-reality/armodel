#ifndef __arsetup_h__
#define __arsetup_h__

#include "framework.hpp"

class ARSetup {
public:
  ARSetup();
  ~ARSetup();
  float GetViewScaleFactor() {return view_scalefactor;}
  void SetViewScaleFactor(float val) {view_scalefactor=val;}

  float GetViewDistanceMin() {return view_distance_min;}
  void SetViewDistanceMin(float val) {view_distance_min=val;}

  float GetViewDistanceMax() {return view_distance_max;}
  void SetViewDistanceMax(float val) {view_distance_max=val;}

  int SetupWindow();
  int SetupCamera();
  int StartCamera() {
    if (arVideoCapStart() != 0) {
      fprintf(stderr, "setupCamera(): Unable to begin camera data capture.\n");
      return (FALSE);		
    }
    return (TRUE);
  }
  string GetCParamName() {return cparam_name;}
  ARParam *GetCParam() {return &cparam;}
  int IsInit() {return isInit;}

  void SetZoom(double val) { zoom = val; }
  double GetZoom() {return zoom;}
  void SetFullScreen(int val) { fullScreen=val; }
  int GetFullScreen() {return fullScreen;}
  void SetXWin(int xval) {xwin=xval;}
  int GetXWin() {return xwin;}
  void SetYWin(int yval) {ywin=yval;}
  int GetYWin() {return ywin;}
  int GetWinWidth() {return winWidth;}
  int GetWinHeight() {return winHeight;}
  void SetHMDFlag(int val) {hmdFlag=val;}
  int GetHMDFlag() {return hmdFlag;}
  void SetVconf(string val) { vconf = val; }
  string GetVconf() { return vconf; }

  ARGL_CONTEXT_SETTINGS_REF GetArglSettings() {return myArglSettings;}

  void CleanUp();

private:
  // 1.0 ARToolKit unit becomes 0.025 of my OpenGL units.
  float view_scalefactor;
  // Objects closer to the camera than this will not be displayed.
  float view_distance_min;
  // Objects further away from the camera than this will not be displayed.
  float view_distance_max;

  // Camera setup
  string cparam_name;
  string vconf;
  ARParam cparam;
  int isInit;

  // Window setup
  double zoom;
  int fullScreen;
  int xwin,ywin;
  int winWidth, winHeight;
  int hmdFlag;

  // ARGL info
  ARGL_CONTEXT_SETTINGS_REF myArglSettings;
};



#endif // __arsetup_h__
