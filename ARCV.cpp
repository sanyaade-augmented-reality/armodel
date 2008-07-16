#include "ARCV.hpp"

ARCV::ARCV() {
}

ARCV::~ARCV() {
}

void ARCV::Init(int width, int height) {
  // Setup OpenCV image information
  tempStorage = new ARUint8[width*height*4];
  modifiedStorage = new ARUint8[width*height*4];
  cout << "-------------------------------------"<< endl;
  cout << "Setting up OpenCV image information" << endl;
  size = new CvSize();
  size->width = width;
  size->height = height;
  originalImage = cvCreateImage(*size, IPL_DEPTH_8U, 4);
  modifiedImage = cvCreateImage(*size, IPL_DEPTH_8U, 4);
  tempImage = cvCreateImage(*size, IPL_DEPTH_8U, 4);
  grayImage = cvCreateImage(*size, IPL_DEPTH_8U, 1);
  cout << "-------------------------------------"<< endl;
}

void ARCV::gray2rgba(IplImage *gray, IplImage *rgba) {
  cvCvtColor(gray,rgba,CV_GRAY2RGBA);
  for (int i=0;i<size->width*size->height*4;i+=4) {
    rgba->imageData[i+3] = (char)255;
  }
}

void ARCV::SaveCameraCapture(ARUint8 *imageData) {
  for (int i=0;i<size->width*size->height*4;i+=4) {
    // Camera frames are stored AGBR.. we need RGBA
    tempStorage[i] = imageData[i+3];
    tempStorage[i+1] = imageData[i+2];
    tempStorage[i+2] = imageData[i+1];
    tempStorage[i+3] = imageData[i];
  }
  cvSetImageData(tempImage,tempStorage,size->width*4);
  cvCopyImage(tempImage,originalImage);
  cvCopyImage(tempImage,modifiedImage);
  cvCvtColor(originalImage, grayImage, CV_RGBA2GRAY);
}

ARUint8* ARCV::GetModifiedAsCameraReady() {

  // test code, not permanent
  cvCanny(grayImage,grayImage,20,20);
  gray2rgba(grayImage,modifiedImage);
  
  cvGetRawData(modifiedImage,&modifiedStorage);
  ARUint8 temp;
  for (int i=0;i<size->width*size->height*4;i+=4) {
    // ARToolkit wants AGBR, we have RGBA
    temp = modifiedStorage[i];
    modifiedStorage[i] = modifiedStorage[i+3];
    modifiedStorage[i+3] = temp;
    temp = modifiedStorage[i+1];
    modifiedStorage[i+1] = modifiedStorage[i+2];
    modifiedStorage[i+2] = temp;
  }
  return modifiedStorage;
}

void ARCV::CleanUp () {
  cout << "----------------------------------------" << endl;
  cout << "Cleaning up ARCV info" << endl;
  cout << "--> OpenCV image data" << endl;
  cout << "   .. releasing original cvimage" << endl;
  cvReleaseImage(&originalImage);
  cout << "   .. releasing modified cvimage" << endl;
  cvReleaseImage(&modifiedImage);
  cout << "   .. releasing temp cvimage" << endl;
  cvReleaseImage(&tempImage);
  cout << "   .. releasing grayscale cvimage" << endl;
  cvReleaseImage(&grayImage);
  cout << "Done with ARCV cleanup" << endl;
}

