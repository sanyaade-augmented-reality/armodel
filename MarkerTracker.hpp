#ifndef __markertracker_h__
#define __markertracker_h__

#include "framework.hpp"

class MarkerTracker {
public:
  MarkerTracker();
  int Track(ARUint8 *dataPtr);
  int MarkerFound();
  int MarkerFound(string name);
  int InitTracker();
  string GetModelName() {return modelName;}
  void SetModelName(string val) {modelName = val;}
  string GetMultiModelName() {return multiModelName;}
  void SetMultiModelName(string val) {multiModelName = val;}
  int GetFound(int *foundIds);
  ObjectData_T GetFound(int index) {
    return markers[index];
  }
  int GetTrans(int index, double mtrans[3][4]) {
    int i,j;
    for (i=0;i<3;i++)
      for(j=0;j<4;j++)
        mtrans[i][j] = markers[index].trans[i][j];
  }
  int GetMultiTrans(int index, double trans[3][4]) {
    int i,j;
    for (i=0;i<3;i++)
      for(j=0;j<4;j++)
        trans[i][j] = multi->marker[index].trans[i][j];
  }
  double GetMultiErr() {return multiErr;}
  int GetNumMarkersFound() {return nMarkersFound;}
  int GetScreenPos(int index, double pos[2]);
  int GetThreshold() {return threshold;}
  int SetThreshold(int thresh) {threshold=thresh;}
  ARMultiMarkerInfoT *GetMulti() {return multi;}
private:
  // Info on markers found in video stream
  ARMarkerInfo *markersFound;
  int nMarkersFound;
  string modelName;
  // Multi-object pattern info
  ARMultiMarkerInfoT  *multi;
  string multiModelName;
  double multiErr;
  // Pattern model information
  ObjectData_T *markers;
  int nMarkers;
  // Detection settings
  int threshold;
};

#endif
