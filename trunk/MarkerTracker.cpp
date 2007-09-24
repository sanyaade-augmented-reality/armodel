#include "MarkerTracker.hpp"

MarkerTracker::MarkerTracker () {
  modelName = "/Users/dogwynn/AR/Data/object_data2";
  multiModelName = "/Users/dogwynn/AR/Data/multi/marker.dat";
  threshold = 100;
}

int MarkerTracker::Track(ARUint8 *dataPtr) {
  int i,j,k;
  if(arDetectMarker(dataPtr, threshold, 
                    &markersFound, &nMarkersFound) < 0 ) {
    return -1;
  }
  multiErr=arMultiGetTransMat(markersFound, nMarkersFound, multi);

//   int go=0;
//   for (i=0;i<multi->marker_num;i++) {
//     if (multi->marker[i].visible>=0) {
//       if (!go) { cout <<  "| "; go=1; }
//       cout << i << ": " << multi->marker[i].pos3d[0][0] << " | " ;
//     }
//   }
//   if (go>0) cout << endl;

  /* check for known patterns */
  for( i = 0; i < nMarkers; i++ ) {
    k = -1;
    for( j = 0; j < nMarkersFound; j++ ) {
      if( markers[i].id == markersFound[j].id) {
        /* you've markersFound a pattern */
//         printf("Pattern markersFound! %f %f\n",markersFound[j].pos[0],
//                 markersFound[j].pos[1]);
        if( k == -1 ) k = j;
        else /* make sure you have the best pattern (highest confidence factor) */
          if( markersFound[k].cf < markersFound[j].cf ) k = j;
      }
    }
    if( k == -1 ) {
      markers[i].visible = 0;
      continue;
    }
		
    /* calculate the transform for each marker */
    if( markers[i].visible == 0 ) {
      arGetTransMat(&markersFound[k],
                    markers[i].marker_center, markers[i].marker_width,
                    markers[i].trans);
    }
    else {
      arGetTransMatCont(&markersFound[k], markers[i].trans,
                        markers[i].marker_center, markers[i].marker_width,
                        markers[i].trans);
    }
    markers[i].pos[0]=markersFound[k].pos[0];
    markers[i].pos[1]=markersFound[k].pos[1];
    markers[i].visible = 1;
    //cout << "here" << endl;
  }
}

int MarkerTracker::GetFound(int *foundIds) {
  int i=0,j=0;
  for (i=0;i<nMarkers;i++) {
    if (markers[i].visible) {
      foundIds[j]=i;
      j++;
    }
  }
  return j;
}

int MarkerTracker::GetScreenPos(int index, double pos[2]) {
  assert(index>=0);
  assert(index<nMarkers);
  if (markers[index].visible) {
    pos[0] = markers[index].pos[0];
    pos[1] = markers[index].pos[1];
  }
}

int MarkerTracker::MarkerFound() {
  int i,j,k;
  for (i=0;i<nMarkers;i++) {
    //cout << markers[i].visible << endl;
    if (markers[i].visible) return i;
  }
  return -1;
}

int MarkerTracker::MarkerFound(string name) {
  // Is the pattern even loaded into the system?
  int i,j,k;
  int haspat=FALSE;
  for (i=0;i<nMarkers;i++) {
    if (strcmp(markers[i].name,name.c_str())>=0) haspat=TRUE;
  }
  if (!haspat) return -1;
  // If so, has it been found?
  for(i=0;i<nMarkers;i++) {
    if ((strcmp(markers[i].name,name.c_str())>=0) &&
        (markers[i].visible)) return i;
  }
  return -1;
}

int MarkerTracker::InitTracker() {
  int i,j,k;
  markers = read_ObjData(modelName.c_str(), &nMarkers);
  if (markers == NULL) return FALSE;
  cout << "Loading multi marker data: " << multiModelName << endl;
  if( (multi = arMultiReadConfigFile(multiModelName.c_str())) == NULL ) {
    printf("XXX config data load error !!\n");
    return FALSE;
  }
  for(k=0;k<multi->marker_num;k++) {
    //cout << "Marker num: " << k << " id: " << multi->marker[k].patt_id << endl;
//     for(i=0;i<3;i++) {
//       for(j=0;j<4;j++) printf("%10.5f ", multi->marker[k].trans[i][j]);
//       printf("\n");
//     }
//     printf("\n");
  }
}
  
