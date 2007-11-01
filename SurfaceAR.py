#!/usr/bin/env python
import os,sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import AR
import Surface
import Tools
from Marker import Marker,MarkerDisplay
from NestedMarker import NestedMarker
import numpy
import numpy.random as random

class WandDisplay(MarkerDisplay):
    def Draw(self):
        m = self.marker
        self.DrawPaddle()
        glPushMatrix()
        glLoadMatrixd(m['mvmat'])
        glColor(1,0,0,.7)
        glTranslatef(0,0,5)
        glutSolidSphere(10,10,10)
        glPopMatrix()
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

class HiroMarkerDisplay(WandDisplay):
    def Draw(self):
        m = self.marker
        self.DrawPaddle()
        glPushMatrix()
        glLoadMatrixd(m['mvmat'])
        glColor(0,1,0,1)
        #glTranslatef(0,0,5)
        glutSolidSphere(5,10,10)
        glPopMatrix()

class KanjiMarkerDisplay(WandDisplay):
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
    scale = 150
    def __init__(self):
        import BezierSurface,BezierGroup
        self.bsdisplay = BezierGroup.BezierGroupDisplay()

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
            markerDisplay.Draw()

    def MultiDisplay(self):
        glEnable(GL_DEPTH_TEST)
        AR.argDrawMode3D()
        AR.argDraw3dCamera( 0, 0 )
        multi = AR.GetMulti()
        self.bsdisplay.SetMV(multi['mvmat'])
        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixd( multi['mvmat'] )
        found = self.GetFound()
        if found:
            #self.bsdisplay.Highlight((-1,-1))
            for marker in found:
                if marker.GetName() == "hiro":
                    p4 = marker.GetPoint4()
                    self.bsdisplay.MoveHighlight(p4)
                elif marker.GetName() == "kanji":
                    point4 = marker.GetPoint4()
                    near = self.bsdisplay.FindNearest(point4)
                    if near is not None:
                        self.bsdisplay.Highlight(near)
        glLoadMatrixd( multi['mvmat'] )
        #self.bsdisplay.DrawCP()
        """
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
        """    
        glLoadMatrixd( multi['mvmat'] )
        self.bsdisplay.Draw()
        min,max=(-50,-180),(250,80)
        #Tools.drawbox(min,max)
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
        self.bsdisplay.Init()
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
