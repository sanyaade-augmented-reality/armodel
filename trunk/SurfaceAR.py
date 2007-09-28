#!/usr/bin/env python
import os,sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import AR
import Surface
from Marker import Marker,NestedMarker
import numpy
import numpy.random as random

def drawbox(min,max):
    glColor(0,0,0,1)
    glPushMatrix()
    glTranslatef( min[0],min[1], 0.0 );
    glutSolidSphere(5,10,10)
    glPopMatrix()
    glColor(.33,.33,.33,1)
    glPushMatrix()
    glTranslatef( min[0],max[1], 0.0 );
    glutSolidSphere(5,10,10)
    glPopMatrix()
    glColor(.66,.66,.66,1)
    glPushMatrix()
    glTranslatef( max[0],max[1], 0.0 );
    glutSolidSphere(5,10,10)
    glPopMatrix()
    glColor(1,1,1,1)
    glPushMatrix()
    glTranslatef( max[0],min[1], 0.0 );
    glutSolidSphere(5,10,10)
    glPopMatrix()


class MarkerDisplay:
    identTrans = ((1,0,0,0),
                  (0,1,0,0),
                  (0,0,1,0))
    def __init__(self,marker):
        self.marker = marker
    def GetMarker(self):
        return self.marker
    def GetCenter3(self):
        marker = self.GetMarker()
        p3 = marker.GetPoint3()
        return p3
    def GetCenter4(self):
        marker = self.GetMarker()
        p4 = marker.GetPoint4()
        return p4
    def DrawPaddle(self):
        m = self.marker
        AR.argDrawMode3D();
        AR.argDraw3dCamera( 0, 0 );

        # load the camera transformation matrix
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix()
        #glPara = AR.argConvGlpara(m['trans']);
        glLoadMatrixd( m['mvmat'] );

        glColor(1,1,1,.8)
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
        glPopMatrix()

    def Draw(self):
        m = self.marker
        self.DrawPaddle()
        glPushMatrix()
        glLoadMatrixd(m['mvmat'])
        glColor(1,0,0,.7)
        glTranslatef(0,0,5)
        glutSolidSphere(10,10,10)
        glPopMatrix()

class HiroMarkerDisplay(MarkerDisplay):
    def Draw(self):
        m = self.marker
        self.DrawPaddle()
        glPushMatrix()
        glLoadMatrixd(m['mvmat'])
        glColor(0,1,0,1)
        #glTranslatef(0,0,5)
        glutSolidSphere(5,10,10)
        glPopMatrix()

class KanjiMarkerDisplay(MarkerDisplay):
    def Draw(self):
        m = self.marker
        self.DrawPaddle()
        glPushMatrix()
        glLoadMatrixd(m['mvmat'])
        glColor(1,0,0,.4)
        glTranslatef(0,0,5)
        glutSolidSphere(10,10,10)
        glPopMatrix()
        
class MarkerDisplayFactory:
    def __init__(self):
        self.default = MarkerDisplay
        self.classMap = {'kanji':KanjiMarkerDisplay,
                    'hiro':HiroMarkerDisplay,
                    }
    def GetDisplay(self,marker):
        name = marker['name'].lower()
        if name in self.classMap.keys():
            return self.classMap[name](marker)
        return self.default(marker)

        
class SurfaceAR:
    cp = numpy.array( [ [ [0,0,0],
                          [.3333,0,0],
                          [.6666,0,0],
                          [1,0,0] ],
                        [ [0,.3333,0],
                          [.3333,.3333,0],
                          [.6666,.3333,0],
                          [1,.3333,0] ],
                        [ [0,.6666,0],
                          [.3333,.6666,0],
                          [.6666,.6666,0],
                          [1,.6666,0] ],
                        [ [0,1,0],
                          [.3333,1,0],
                          [.6666,1,0],
                          [1,1,0] ] ] )
    scale = 150
    def __init__(self):
        centroid = numpy.zeros(3)
        cp = self.cp.copy()
        for i in range(4):
            for j in range(4):
                cp[i][j][2] = numpy.random.random()*.7
                cp[i][j] *= self.scale
                centroid += cp[i][j]
        print centroid
        centroid/=16
        print centroid
        for i in range(4):
            for j in range(4):
                cp[i][j] -= centroid
        minz = 1e300
        for i in range(4):
            for j in range(4):
                if cp[i][j][2] < minz:
                    minz = cp[i][j][2]
        #minz -= 50
        print minz
        for i in range(4):
            for j in range(4):
                cp[i][j][2] -= minz
                cp[i][j][0] += 100
                cp[i][j][1] -= 70
        self.bsurf = Surface.BezierSurface(cp)
        self.bsdisplay = Surface.BezierSurfaceDisplay(self.bsurf)

        self.displayFactory = MarkerDisplayFactory()

        AR.SetSingleLoop(self.SingleDisplay)
        AR.SetMultiLoop(self.MultiDisplay)

    def GetFound(self):
        found = AR.GetFound()
        markers = []
        for m in found:
            marker = Marker(m)
            markers.append(marker)
        return markers

    def SingleDisplay(self):
        found = self.GetFound()
        AR.argDrawMode3D()
        AR.argDraw3dCamera( 0, 0 )
        for marker in found:
            markerDisplay = self.displayFactory.GetDisplay(marker)
            #markerDisplay.Draw()
    def MultiDisplay(self):
        glEnable(GL_DEPTH_TEST)
        AR.argDrawMode3D()
        AR.argDraw3dCamera( 0, 0 )
        multi = AR.GetMulti()
        self.bsdisplay.SetMV(multi['mvmat'])
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixd( multi['mvmat'] )
        width = 100
        found = self.GetFound()
        if found:
            #self.bsdisplay.Highlight((-1,-1))
            for marker in found:
                if marker.GetName() == "hiro":
                    p4 = marker.GetPoint4()
                    self.bsdisplay.MoveHighlight(p4,multi['mvmat'])
                elif marker.GetName() == "kanji":
                    point4 = marker.GetPoint4()
                    near = self.bsdisplay.FindNearest(point4,multi['mvmat'])
                    if near is not None:
                        self.bsdisplay.Highlight(near)
        glLoadMatrixd( multi['mvmat'] )
        self.bsdisplay.DrawCP()
        for marker in found:
            markerDisplay = self.displayFactory.GetDisplay(marker)
            center = marker.GetPoint4()
            center = self.bsdisplay.GetPointTransform(center)
            cToZ = center.copy()
            print marker['name']
            cToZ[2,0] = 0.0
            glColor(0,1,1)
            glBegin(GL_LINES)
            glVertex(center)
            glVertex(cToZ)
            glEnd()

            markerDisplay.Draw()
            
        glLoadMatrixd( multi['mvmat'] )
        self.bsdisplay.Draw()
        min,max=(-50,-180),(250,80)
        #drawbox(min,max)
        #glColor(1,1,1,.5)
        #glBegin(GL_POLYGON);
        #glVertex3f(min[0],min[1],0);
        #glVertex3f(min[0],max[1],0);
        #glVertex3f(max[0],max[1],0);
        #glVertex3f(max[0],min[1],0);
        #glEnd();
    def Init(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA,)
        glEnable(GL_NORMALIZE)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)
    def Run(self):
        vconf = " ".join(sys.argv[1:])
        print sys.argv
        AR.Init(threshold=85,
                vconf=vconf,
                initFunc=self.Init,
                )
        AR.Run()

if __name__=='__main__':
    sar = SurfaceAR()
    sar.Run()
