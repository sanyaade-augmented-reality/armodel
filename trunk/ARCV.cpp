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
  originalImage = cvCreateImage(*size, IPL_DEPTH_8U, 3);
  modifiedImage = cvCreateImage(*size, IPL_DEPTH_8U, 3);
  tempImage = cvCreateImage(*size, IPL_DEPTH_8U, 4);
  grayImage = cvCreateImage(*size, IPL_DEPTH_8U, 1);
  hsvImage = cvCreateImage(*size, IPL_DEPTH_8U, 3);
  // workspace images
  for(int i=0;i<5;i++) {
    work1[i] = cvCreateImage(*size, IPL_DEPTH_8U, 1);
    work3[i] = cvCreateImage(*size, IPL_DEPTH_8U, 3);
  }
  // rgbaPlanes
  for(int i = 0; i < 4; i++ ) 
    rgbaPlanes[i] = cvCreateImage(*size, IPL_DEPTH_8U, 1);
  // hsvPlanes
  for(int i = 0; i < 3; i++ ) 
    hsvPlanes[i] = cvCreateImage(*size, IPL_DEPTH_8U, 1);
  // Laplacian info
  //   laplacian image
  laplace = cvCreateImage( *size, IPL_DEPTH_16S, 1 );
  //   color version of laplacian
  colorLaplace = cvCreateImage( *size, IPL_DEPTH_8U, 4);
  // Storage array
  for(int i=0;i<10;i++)
    cvStorage[i] = cvCreateMemStorage(0);
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
  cvCvtColor(tempImage,originalImage,CV_RGBA2RGB);
  cvCvtColor(tempImage,modifiedImage,CV_RGBA2RGB);
  //cvCvtColor(tempImage,colorLaplace,CV_RGBA2RGB);
  cvCvtColor(originalImage, grayImage, CV_RGB2GRAY);
  cvCvtColor(originalImage, hsvImage, CV_RGB2HSV);

  cvCvtPixToPlane( tempImage,
                   rgbaPlanes[0], rgbaPlanes[1],
                   rgbaPlanes[2], rgbaPlanes[3] );
  cvCvtPixToPlane( hsvImage,
                   hsvPlanes[0], hsvPlanes[1],
                   hsvPlanes[2], 0 );

  if (0) {
    for (int i=0;i<4;i++) {
      cvLaplace( rgbaPlanes[i], laplace, 3 );
      cvConvertScaleAbs( laplace, rgbaPlanes[i], 1, 0 );
    }
    cvCvtPlaneToPix( rgbaPlanes[0], rgbaPlanes[1],
                     rgbaPlanes[2], rgbaPlanes[3], colorLaplace );
    colorLaplace->origin = originalImage->origin;
  }
}

ARUint8* ARCV::GetModifiedAsCameraReady() {
  // test code, not permanent
  //cvLaplace(grayImage,grayImage,1);
  //cvCvtColor(grayImage,modifiedImage,CV_GRAY2RGB);
  //cvCvtColor(laplace,modifiedImage,CV_GRAY2RGB);
  //gray2rgba(grayImage,modifiedImage);
  //cvCanny(rgbaPlanes[2],grayImage,150,150);
  //
  //cvCvtColor(colorLaplace,grayImage,CV_RGBA2GRAY);


  #if 0
  // saturation
  cvCopyImage(hsvPlanes[1],work1[1]);
  cvThreshold( work1[1], work1[1], 130, 255, CV_THRESH_BINARY);

  // value
  cvCopyImage(hsvPlanes[2],work1[2]);
  cvThreshold( work1[2], work1[2], 90, 255, CV_THRESH_BINARY);

  // hue 
  cvCopyImage(hsvPlanes[0],work1[0]);
  cvThreshold( work1[0], work1[0], 100, 0, CV_THRESH_TOZERO_INV);
  cvThreshold( work1[0], work1[0], 65, 0, CV_THRESH_TOZERO);

  cvAnd(work1[0],work1[1],work1[0]);
  cvAnd(work1[0],work1[2],work1[0]);
  
  cvThreshold( work1[0], work1[0], 1, 255, CV_THRESH_BINARY);
  

  cvSmooth(work1[0],work1[0],CV_GAUSSIAN,17,17);
  cvThreshold( work1[0], work1[0], 128, 255, CV_THRESH_BINARY);
  cvCanny(work1[0],work1[0],50,200);
  cvCopyImage(work1[0],grayImage);
  //cvCvtColor(work1[0],modifiedImage,CV_GRAY2RGB);

  //cvSmooth(grayImage,grayImage,CV_GAUSSIAN,17,17);
  //cvCanny(grayImage,grayImage,50,200);
  cvCvtColor(grayImage,modifiedImage,CV_GRAY2RGB);

  CvSeq* contour = 0;
  cvFindContours(grayImage, cvStorage[0], &contour, sizeof(CvContour),
                 CV_RETR_CCOMP, CV_CHAIN_APPROX_SIMPLE);
//   contour = cvApproxPoly( contour, sizeof(CvContour), cvStorage[0],
//                            CV_POLY_APPROX_DP, 3, 1 );
  cvDrawContours(modifiedImage,contour,
                 CV_RGB(255,0,0),CV_RGB(0,255,0),
                 1, 1);
  
  CvSeq* lines = cvHoughLines2(grayImage,cvStorage[0],
                               CV_HOUGH_PROBABILISTIC, 1, CV_PI/180,
                               50,50,10);
  for (int i=0;i<lines->total;i++) {
    CvPoint* line = (CvPoint*)cvGetSeqElem(lines,i);
    cvLine(modifiedImage, line[0], line[1], CV_RGB(255,0,0), 3, 8);
  }

  CvSeq* circles = cvHoughCircles(grayImage,cvStorage[0],
                                  CV_HOUGH_GRADIENT, 2, grayImage->height/4,
                                  200,100);
  for (int i=0;i<circles->total;i++) {
    float* p = (float*)cvGetSeqElem(circles,i);
    cvCircle(modifiedImage,cvPoint(cvRound(p[0]),cvRound(p[1])),
             3, CV_RGB(0,255,0), -1, 8, 0);
    cvCircle(modifiedImage,cvPoint(cvRound(p[0]),cvRound(p[1])),
             cvRound(p[2]), CV_RGB(255,0,0), 3, 8, 0);
  }
  #endif

  ARUint8 temp;
  for (int i=0,j=0;i<size->width*size->height*4;i+=4,j+=3) {
    // ARToolkit wants AGBR, we have RGBA
    modifiedStorage[i] = (char)255;
    modifiedStorage[i+1] = modifiedImage->imageData[j+2];
    modifiedStorage[i+2] = modifiedImage->imageData[j+1];
    modifiedStorage[i+3] = modifiedImage->imageData[j];
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

