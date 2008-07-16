#ifndef __arcv_h__
#define __arcv_h__

#include "framework.hpp"

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
  IplImage *originalImage; // original image
  IplImage *modifiedImage; // original image
  IplImage *tempImage; // temp placeholder for camera framecap
  IplImage *grayImage; // grayscale image
  ARUint8 *tempStorage; // to store pixel information from ARTK screen
                        // cap
  ARUint8 *modifiedStorage; // to store ARUint8 array version of
                            // modified CV image
  void gray2rgba(IplImage *gray, IplImage *rgba);
};


#endif // __arcv_h__
