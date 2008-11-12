from OpenGL.GL import *
from OpenGL.GLUT import *
import _AR
import ctypes
from ctypes import *
import CVtypes
from CVtypes import cv
import numpy

def draw1():
    glColor(0,1,0)
    glPushMatrix()
    glTranslate(0,0,10)
    glutSolidSphere(10,10,10)
    glutSolidCube(10)
    glPopMatrix()

def draw2():
    glColor(1,1,1,.6)
    glBegin(GL_POLYGON);
    width = 30
    glVertex3f(-width,-width,0);
    glVertex3f(-width,width,0);
    glVertex3f(width,width,0);
    glVertex3f(width,-width,0);
    glEnd();
    wo2 = width/2.
    glBegin(GL_POLYGON);
    glVertex3f(-wo2,-4*width,0);
    glVertex3f(-wo2,-width,0);
    glVertex3f(wo2,-width,0);
    glVertex3f(wo2,-4*width,0);
    glEnd()
    glColor(1,0,0)
    glPushMatrix()
    glTranslate(0,0,10)
    glutWireSphere(10,10,10)
    glPopMatrix()

def imageAsArray(image):
    btype = c_byte * image[0].imageSize
    buf = buffer(btype.from_address(image[0].imageData))
    array = numpy.frombuffer(buf,dtype=numpy.ubyte)
    return array
    
class ARSystem:
    size = cv.Size(640,480)
    image = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,3)
    grayImage = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1)
    maskImage = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1)
    backprojectImage = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1)
    modifiedImage = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,3)
    hsvImage = cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,3)
    histDims = 32
    histRanges = [[50,110]]
    histogram = cv.CreateHist(1, [histDims],
                              CVtypes.CV_HIST_ARRAY,
                              histRanges, 1)
    hsvPlanes = [
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        ]
    rgbPlanes = [
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1),
        ]
    work1 = []
    work3 = []
    cvStorage = []
    for i in range(10):
        work1.append(cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,1))
        work3.append(cv.CreateImage(size,CVtypes.IPL_DEPTH_8U,3))
        cvStorage.append(cv.CreateMemStorage(0))

    def __init__(self):
        _AR.Init(
            multiDisplayDict={'Data/markerboard-1-6.cfg':draw1},
            singleDisplayDict={0:draw2},
            initFunc=self.Init,
            preRender=self.preRender,
            render=self.render,
            )

    def Run(self):
        _AR.Run()
    def Init(self):
        glutKeyboardFunc(self.keyboard)

    displayType = 'mask'
    def keyboard(self,key,x,y):
        key = key.lower()
        if key == 'h':
            self.queHistSnap = True
        elif key == 'c':
            self.displayType = 'color'
        elif key == 'b':
            self.displayType = 'back'
        elif key == 'g':
            self.displayType = 'gray'
        elif key == 'm':
            self.displayType = 'mask'

    def renderFrame(self,frame):
        glEnable(GL_TEXTURE_2D);
        internalFormat = GL_RGB
        format = GL_BGR
        if frame[0].nChannels == 1:
            internalFormal,format = GL_LUMINANCE,GL_LUMINANCE
        glTexImage2D(GL_TEXTURE_2D, 0, internalFormat,
                     frame[0].width,frame[0].height,
                     0,format,GL_UNSIGNED_BYTE,
                     imageAsArray(frame));

        z = 0;

        glMatrixMode(GL_PROJECTION);
        glLoadIdentity();

        glMatrixMode(GL_MODELVIEW);
        glPushMatrix();
        glLoadIdentity();
        glBegin(GL_POLYGON);

        glTexCoord2f(0.0, 1.0); glVertex3f(-1.0, -1.0, z);
        glTexCoord2f(1.0, 1.0); glVertex3f( 1.0, -1.0, z);
        glTexCoord2f(1.0, 0.0); glVertex3f( 1.0,  1.0, z);
        glTexCoord2f(0.0, 0.0); glVertex3f(-1.0,  1.0, z);

        glEnd();
        glPopMatrix();

        glFlush();
        glDisable(GL_TEXTURE_2D);

    def render(self):
        self.renderFrame(self.modifiedImage)

    def getFrame(self):
        p = _AR.GetImage()
        ip = cast(c_void_p(p),
                         POINTER(CVtypes.IplImage))
        return ip
    
    def preRender(self):
        frame = self.getFrame()

        cv.Copy(frame,self.image)

        cv.CvtColor(frame, self.grayImage, CVtypes.CV_RGB2GRAY);
        cv.CvtColor(frame, self.hsvImage, CVtypes.CV_RGB2HSV);
        cv.Split( frame,
                  self.rgbPlanes[0], self.rgbPlanes[1],
                  self.rgbPlanes[2], 0 )
        cv.Split( self.hsvImage,
                  self.hsvPlanes[0], self.hsvPlanes[1],
                  self.hsvPlanes[2], 0 )
        
        self.backProject()
        #self.getContours()

    queHistSnap = False
    histSnapTaken = False
    def backProject(self):
        work = self.work1[0]
        #cv.Smooth(self.hsvImage,self.hsvImage,CVtypes.CV_GAUSSIAN,7,7);
        cv.InRangeS(self.hsvImage,
                    cv.Scalar(0,30,200,0),
                    cv.Scalar(180,256,256,0),
                    self.maskImage)

        cv.InRangeS(self.hsvImage,
                    cv.Scalar(0,30,100,0),
                    cv.Scalar(180,256,256,0),
                    work)


        if self.queHistSnap:
            cv.CalcHist( [self.hsvPlanes[0]], self.histogram,0, self.maskImage )
            values = cv.GetMinMaxHistValue( self.histogram )
            self.histSnapTaken = True
            self.queHistSnap = False
        if self.histSnapTaken:
            cv.CalcBackProject( [self.hsvPlanes[0]],
                                self.backprojectImage,
                                self.histogram )
            cv.And( self.backprojectImage, work, self.backprojectImage, 0 )
        if self.displayType == 'color':
            cv.Copy(self.image,self.modifiedImage)
        elif self.displayType == 'back':
            cv.CvtColor(self.backprojectImage,self.modifiedImage,
                        CVtypes.CV_GRAY2RGB)
        elif self.displayType == 'gray':
            cv.CvtColor(self.grayImage,self.modifiedImage,CVtypes.CV_GRAY2RGB)
        elif self.displayType == 'mask':
            cv.CvtColor(self.maskImage,self.modifiedImage,CVtypes.CV_GRAY2RGB)
            
        self.getContours(self.backprojectImage)
        #self.getContours(self.maskImage)

    def getContours(self,image):
        cv.Smooth(image,image,CVtypes.CV_GAUSSIAN,17,17);
        #cv.CvtColor(image,self.modifiedImage,CVtypes.CV_GRAY2RGB);
        cv.Threshold( image, image, 128, 255, CVtypes.CV_THRESH_BINARY);
        #cv.CvtColor(image,self.modifiedImage,CVtypes.CV_GRAY2RGB);
        cv.Canny(image,image,50,200);

        #cv.CvtColor(image,self.modifiedImage,CVtypes.CV_GRAY2RGB);
        #cv.CvtColor(self.grayImage,self.modifiedImage,CVtypes.CV_GRAY2RGB);
        #cv.Copy(frame,self.modifiedImage)
        #return
        contour = POINTER(cv.Seq)()
        if 1:
            cv.FindContours(
                image,
                #self.grayImage,
                self.cvStorage[0],
                byref(contour),
                sizeof(cv.Contour),
                CVtypes.CV_RETR_CCOMP,
                CVtypes.CV_CHAIN_APPROX_SIMPLE,
                cv.Point(0,0),
                )
        contourBlocks = []
        if contour:
            cSeq = cast(contour,POINTER(cv.Seq))
            ellipses = []
            while cSeq:
                contours = []
                total = cSeq[0].total
                if total >= 6:
                    box = cv.FitEllipse2(cSeq)
                    ellipses.append(box)
                #print
                #print
                for i in range(total):
                    next = CVtypes.CV_GET_SEQ_ELEM(cv.Seq,cSeq,i)
                    nContour = cast(next,POINTER(cv.Contour))
                    rect = nContour[0].rect
                    contours.append(rect)
                    #print rect
                contourBlocks.append(contours)
                cSeq = cast(cSeq[0].h_next,POINTER(cv.Seq))
        #print ellipses[0]
        #print
        if 1:
            if contourBlocks:
                bboxes = []
                for contours in contourBlocks:
                    c0 = contours[0]
                    bbox = [641,481,-1,-1]
                    for i,c in enumerate(contours):
                        #if i==(len(contours)-1): break
                        x0,y0,x1,y1 = c.x,c.y,c.width,c.height
                        if ((x0>640) or (x1>640) or (y0>480) or (y1>480) or
                            (x0<=0) or (x1<=0) or (y0<=0) or (y1<=0) ):
                            x0,y0,x1,y1 = c0.x,c0.y,c0.width,c0.height
                            continue
                        if x0<bbox[0]: bbox[0] = x0
                        if x1<bbox[0]: bbox[0] = x0
                        if x0>bbox[2]: bbox[2] = x0
                        if x1>bbox[2]: bbox[2] = x0
                        if y0<bbox[1]: bbox[1] = y0
                        if y1<bbox[1]: bbox[1] = y0
                        if y0>bbox[3]: bbox[3] = y0
                        if y1>bbox[3]: bbox[3] = y0
                        cv.Line(self.modifiedImage,
                                cv.Point(x0,y0),
                                cv.Point(x1,y1),
                                #cv.Point(contours[i+1].x,contours[i+1].y),
                                CVtypes.CV_RGB(255,0,0),
                                1, 1,
                                )
                    bboxes.append(bbox)
                for bbox in bboxes:
                    cv.Rectangle(self.modifiedImage,
                                 cv.Point(bbox[0],bbox[1]),
                                 cv.Point(bbox[2],bbox[3]),
                                 CVtypes.CV_RGB(0,255,255),
                                 1,8,
                                 )
                cx,cy = 0,0
                num = 0
                for e in ellipses:
                    x = e.center.x
                    y = e.center.y
                    center = cv.Point(int(x),int(y))
                    size = cv.Size(int(e.size.width),int(e.size.height))
                    if size.width>640 or size.height>480: continue
                    cx+=x;cy+=y
                    num += 1
                    angle = -e.angle
                    cv.Ellipse(self.modifiedImage,
                               center,
                               size,
                               angle,
                               0, 360,
                               CVtypes.CV_RGB(0,255,255),
                               )
                if num:
                    cx /= num
                    cy /= num
                    cv.Circle(self.modifiedImage,
                              cv.Point(int(cx),int(cy)),
                              20,
                              CVtypes.CV_RGB(255,255,0),
                              )

        cv.DrawContours(
            self.modifiedImage,
            contour,
            CVtypes.CV_RGB(255,0,0),
            CVtypes.CV_RGB(0,255,0),
            1, 1, 
            )


if __name__=='__main__':
    ar = ARSystem()
    ar.Run()
