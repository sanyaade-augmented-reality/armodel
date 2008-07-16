#!/usr/bin/env python
import os,sys,optparse,pprint

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy
import numpy.random as random

import AR
import Surface
import BezierSurface,BezierGroup,MeshGroup
import Tools
from Marker import Marker,MarkerDisplay
from NestedMarker import NestedMarker

"""
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
        #AR.argDrawMode3D();
        #AR.argDraw3dCamera( 0, 0 );

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
"""
class WandDisplay(MarkerDisplay):
    def Draw(self,reflection=False,**kw):
        m = self.GetMarker()
        #AR.argDrawMode3D();
        #AR.argDraw3dCamera( 0, 0 );
        glMatrixMode(GL_MODELVIEW);
        glPushMatrix()
        glLoadMatrixd( m['mvmat'] );
        self.DrawPaddle()
        self.DrawIcon()
        glPopMatrix()
    def DrawIcon(self):
        glColor(1,0,0,.7)
        glTranslatef(0,0,5)
        glutSolidSphere(10,10,10)
    def DrawPaddle(self):
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

class HiroMarkerDisplay(WandDisplay):
    def DrawIcon(self):
        glColor(0,1,0,1)
        #glTranslatef(0,0,5)
        glutSolidSphere(5,10,10)

class KanjiMarkerDisplay(WandDisplay):
    def DrawIcon(self):
        glColor(1,0,0,.4)
        glTranslatef(0,0,5)
        glutSolidSphere(10,10,10)
        
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
        min,max=(-50,-180),(250,80)
        incx,incy = (max[0]-min[0])/4.,(max[1]-min[1])/4.
        minx,miny = min
        pts = []
        cp = numpy.array( [ [ [minx,miny,0.],
                              [minx+incx,miny,0],
                              [minx+incx*2,miny,0],
                              [minx+incx*3,miny,0] ],
                            [ [minx,miny+incy,0.],
                              [minx+incx,miny+incy,0],
                              [minx+incx*2,miny+incy,0],
                              [minx+incx*3,miny+incy,0] ],
                            [ [minx,miny+incy*2,0.],
                              [minx+incx,miny+incy*2,0],
                              [minx+incx*2,miny+incy*2,0],
                              [minx+incx*3,miny+incy*2,0] ],
                            [ [minx,miny+incy*3,0.],
                              [minx+incx,miny+incy*3,0],
                              [minx+incx*2,miny+incy*3,0],
                              [minx+incx*3,miny+incy*3,0] ] ] )
        import random
        centroid = numpy.zeros(3)
        for i in range(4):
            for j in range(4):
                cp[i][j][2] = 100*random.random()
#         for i in range(4):
#             for j in range(4):
#                 centroid+= cp[i][j]
#         centroid/=16
#         for i in range(4):
#             for j in range(4):
#                 cp[i][j] -= centroid
        #from teapot import teapot
        #cp = numpy.array(teapot[16])
        # XXXXXXXXX  hack
        #cp[:,:,0]+=110
        #cp[:,:,1]-=50
        
        bsurface = BezierSurface.BezierSurface(cp)
        self.bsdisplay = BezierSurface.BezierSurfaceDisplay(bsurface)
        #self.bsdisplay = BezierGroup.BezierGroupDisplay()
        #self.bsdisplay = MeshGroup.MeshGroupDisplay()

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

        # Add reflection (ripped from OpenGL example)
        # stencil buffer
        glClear(GL_STENCIL_BUFFER_BIT)
        glColorMask(0, 0, 0, 0);
        # Draw 1 into the stencil buffer. 
        glEnable(GL_STENCIL_TEST);
        glStencilFunc(GL_ALWAYS, 1, 1);
        glStencilOp(GL_KEEP, GL_KEEP, GL_REPLACE);

        # Now render floor; floor pixels just get their stencil set to 1. 
        glDisable(GL_LIGHTING)
        glDisable(GL_DEPTH_TEST)
        min,max=(-50,-180),(250,80)
        Tools.drawbox(min,max)
        glBegin(GL_POLYGON);
        glVertex3f(min[0],min[1],0);
        glVertex3f(min[0],max[1],0);
        glVertex3f(max[0],max[1],0);
        glVertex3f(max[0],min[1],0);
        glEnd();
        glEnable(GL_LIGHTING)
        glEnable(GL_DEPTH_TEST)

        # Re-enable update of color and depth. 
        glColorMask(1, 1, 1, 1);
        glEnable(GL_DEPTH_TEST);

        # Now, only render where stencil is set to 1. 
        glStencilFunc(GL_EQUAL, 1, 1);  # draw if ==1 
        glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP);

        glPushMatrix()
        glCullFace(GL_FRONT)
        """
        for marker in found:
            markerDisplay = self.displayFactory.GetDisplay(marker)
            markerDisplay.Draw(reflection=True)
        """
        glScalef(1,1,-1.)
        self.bsdisplay.Draw(reflection=True)
        glCullFace(GL_BACK)
        glPopMatrix()

        glDisable(GL_STENCIL_TEST)

        ######################
        # draw plate/floor
        #if False:
        if True:
            min,max=(-50,-180),(250,80)
            Tools.drawbox(min,max)
            glColor(0,1,1,.9)
            glBegin(GL_POLYGON);
            glVertex3f(min[0],min[1],0);
            glVertex3f(min[0],max[1],0);
            glVertex3f(max[0],max[1],0);
            glVertex3f(max[0],min[1],0);
            glEnd();
        ######################
        # draw bezier surface
        self.bsdisplay.Draw()
        
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
        op = optparse.OptionParser()
        op.add_option('-d', '--dialog',dest='dialog',
                      help='Camera input dialog',
                      action='store_true',
                      default=False,
                      )
        op.add_option('-t', '--thresh',dest='threshold',
                      default=85, type='int')
        (options,args) = op.parse_args()
        vconf = '-nodialog'
        if options.dialog:
            vconf = ''
        AR.Init(threshold=options.threshold,
                vconf=vconf,
                initFunc=self.Init,
                )
        AR.Run()

if __name__=='__main__':
    sar = SurfaceAR()
    sar.Run()
