#ifndef __arcv_h__
#define __arcv_h__

#include <assert.h>
#include <stdio.h>
#include <stdlib.h> // malloc(), free()
#include <string.h>
#include <math.h>

#include <string>
#include <vector>
#include <iostream>

#include "opencv/cv.h"
#include "opencv/highgui.h"

#include <AR/ar.h>

using namespace std;

class ARCV {
public:
  ARCV();
  ~ARCV();
  void Init(int width, int height);
  void SaveCameraCapture(ARUint8 *imageData);
  IplImage* GetOriginal() { return originalImage;}
  IplImage* GetGrayscale() { return grayImage;}
  IplImage* GetModified() { return modifiedImage;}
  ARUint8* GetModifiedAsCameraReady();
  void CleanUp();

private:
  CvSize *size;
  IplImage *originalImage; // original camera framecap
  IplImage *rgbaPlanes[4]; // RGBA layers of framecap
  IplImage *hsvImage; //HSV image info
  IplImage *hsvPlanes[3]; // HSV planes
  IplImage *modifiedImage; // modified version of original image
  IplImage *tempImage; // temp placeholder for camera framecap
  IplImage *grayImage; // grayscale image
  IplImage *work1[5]; // workspace 1-channel images
  IplImage *work3[5]; // workspace 3-channel images
  ARUint8 *tempStorage; // to store pixel information from ARTK screen
                        // cap
  ARUint8 *modifiedStorage; // to store ARUint8 array version of
                            // modified CV image
  IplImage *laplace; // Storage for Laplacian of framecap
  IplImage *colorLaplace; // color version
  CvMemStorage *cvStorage[10];

  void gray2rgba(IplImage *gray, IplImage *rgba);
};


#endif // __arcv_h__
