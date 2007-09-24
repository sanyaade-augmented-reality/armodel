#!/usr/bin/env python
import os,sys
import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Glinter.Core import LightRack

class Surface:
    def __init__(self):
        pass
    def __call__(self,u,v):
        return [0,0,0]
    
class BezierSurface(Surface):
    def __init__(self,cp=None):
        Surface.__init__(self)
        self.cp = cp
        if cp is None:
            self.cp = numpy.zeros((4,4,3))
        self.degree = 4
        self.Reset()
    def Reset(self):
        self.work = self.cp.copy()
        self.cpCopy = self.cp.copy()
    def DeCasteljau(self,u,v):
        cp = self.work = numpy.array(self.cp,copy=1)
        for i in range(self.degree):
            for k in range(1,self.degree):
                for j in range(self.degree-k):
                    cp[i][j] = (1-u)*cp[i][j] + u*cp[i][j+1]
        for k in range(1,self.degree):
            for i in range(self.degree-k):
                cp[i][0] = (1-v)*cp[i][0] + v*cp[i+1][0]
        return cp[0][0]
    def __call__(self,u,v):
        return self.DeCasteljau(u,v)
    def copy(self):
        return self.cpCopy
    def Move(self,i,j,dxPoint):
        self.cp[i][j] = dxPoint
        self.Reset()
        

class SurfaceDisplay:
    def __init__(self):
        pass
    def Draw(self):
        pass
    
class BezierSurfaceDisplay(SurfaceDisplay):
    def __init__(self,surface=None,resolution=10):
        SurfaceDisplay.__init__(self)
        self.bSurface = surface
        self.resolution = r = resolution
        self.drawPoints = numpy.zeros((r,r,3),'d')
        self.normPoints = numpy.zeros((r,r,3),'d')
        self.Reset()
        self.__lightRack = None
    def GetSurface(self):
        return self.bSurface
    def LightRack(self):
        if not self.__lightRack:
            self.__lightRack = LightRack()
        return self.__lightRack
    def Reset(self):
        bs = self.bSurface
        res = self.resolution
        for i in range(res):
            u = float(i)/(res-1)
            for j in range(res):
                v = float(j)/(res-1)
                self.drawPoints[i][j] = bs(u,v)
        dp = self.drawPoints
        for i in range(res-1):
            for j in range(res-1):
                self.normPoints[i][j] = numpy.cross(dp[i][j+1]-dp[i][j],
                                                    dp[i+1][j]-dp[i][j])
        for j in range(res):
            self.normPoints[res-1][j] = self.normPoints[res-1][j-1]
        for i in range(res):
            self.normPoints[i][res-1] = self.normPoints[i-1][res-1]
        #print dp[res-1][res-1],bs.cp[3][3]
        
    def MoveLight(self,index,point):
        lights = self.LightRack()
        lights.MoveLight(index,point)
        lights.TurnOnLight(index)
    def FindNearest(self,pos,mvmat):
        #print mvmat
        mvmat = numpy.mat(numpy.array(mvmat).reshape(4,4).transpose())
        #print mvmat
        mindx = 1e300
        mincp = None
        test = numpy.array(pos)
        cp = self.bSurface.copy()
        v=0
        #print 'test',test
        for i in range(4):
            for j in range(4):
                p = numpy.mat(numpy.resize(cp[i][j],4))
                p[0,-1] = 1
                if v>0:
                    print p
                mvp = mvmat*p.T
                if v>0:
                    print mvp
                #print 'p,test,p-test',p,test,p-test
                dx = numpy.linalg.norm(mvp-test.T)
                if v>0:
                    print dx
                if dx < mindx:
                    mincp = i,j
                    mindx = dx
        #print 'Mindx: ', mindx
        if mindx>30:
            mincp = -1,-1
        return mincp
    def SetMV(self,mvmat):
        self.mvArray = numpy.array(mvmat).reshape(4,4).transpose()
        self.mvMatrix = numpy.mat(self.mvArray)
    def GetPointTransform(self,point4):
        mvmat = self.mvMatrix
        mvinv = self.mvMatrix.I
        return mvinv*point4.T
    def MoveHighlight(self,point4,mvmat):
        i,j = self.GetHighlight()
        if (i,j) == (-1,-1):
            return
        mvmat = self.mvMatrix
        cp = self.bSurface.cp
        p = numpy.mat(numpy.resize(cp[i][j],4))
        p[0,-1] = 1.
        #mvp = mvmat*p.T
        #print mvmat.I
        #print point4.T
        newp = self.GetPointTransform(point4)
        #dx = point4-mvp
        #dx = numpy.resize(dx,3)
        newp = numpy.resize(newp,3)
        self.bSurface.Move(i,j,newp)
        self.Reset()
        
        
    highlight = (-1,-1)
    def GetHighlight(self):
        return self.highlight
    def Highlight(self,indeces=None):
        if indeces is None:
            return (self.highlight == (-1,-1))
        self.highlight = indeces
    def DrawCP(self):
        glEnable(GL_NORMALIZE)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)
        lights = self.LightRack()
        lights.MoveLight(0,(10,10,100))
        lights.Reset()
        bs = self.bSurface
        cp = bs.cp
        for j in range(len(cp)):
            for i in range(len(cp[0])):
                p = cp[i][j]
                pLineToZ = p.copy()
                pLineToZ[2] = 0.0
                size = 5
                glBegin(GL_LINES)
                glColor(0,0,0)
                glVertex(p)
                glVertex(pLineToZ)
                glEnd()
                glPushMatrix()
                glTranslate(p[0],p[1],p[2])
                if (i,j) == self.highlight:
                    glColor(0,1,0,1)
                    glScalef(5.5,5.5,5.5)
                    glutSolidIcosahedron()
                else:
                    glColor(1,1,0,1)
                    glutSolidSphere(size,10,10)
                glPopMatrix()
    def Draw(self):
        glEnable(GL_NORMALIZE)
        glLightModeli(GL_LIGHT_MODEL_TWO_SIDE,1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK,GL_AMBIENT_AND_DIFFUSE)
        lights = self.LightRack()
        lights.MoveLight(0,(10,10,100))
        lights.Reset()
        bs = self.bSurface
        res = self.resolution
        dp,np = self.drawPoints,self.normPoints
        cp = bs.cp
        self.DrawCP()
        #return        
        for j in range(res-1):
            """
            for i in range(res):
                glColor(i/float(res),j/float(res),1)
                glPushMatrix()
                p = dp[i][j]
                #print p
                glTranslate(p[0],p[1],p[2])
                glutSolidSphere(.01,10,10)
                glPopMatrix()
            """
            glColor(1,1,1,.7)
            glBegin(GL_QUAD_STRIP)
            for i in range(res):
                glNormal3dv(np[i][j])
                glVertex(dp[i][j])
                glVertex(dp[i][j+1])
            glEnd()
                
        #print self.drawPoints

class BezierQuilt:
    def __init__(self,fileName=None):
        self.patches = []
        if fileName is not None:
            self.Import(fileName)
    def Import(self,fileName):
        f = open(fname)
        for line in f.readlines():
            sl = line.strip()
            if len(sl)>1:
                vals = sl.split()[1:-1]
                vals = map(float,vals)
                rlist.append( vals )
        

class SurfaceApp:
    def __init__(self):
        cp = numpy.array( [ [ [0,0,0],
                              [1,0,0],
                              [2,0,0],
                              [3.,0,0] ],
                            [ [0,1,0],
                              [1,1,0],
                              [2,1,0],
                              [3.,1,0] ],
                            [ [0,2,0],
                              [1,2,0],
                              [2,2,0],
                              [3.,2,0] ],
                            [ [0,3,0],
                              [1,3,0],
                              [2,3,0],
                              [3.,3,0] ] ] )
        import random
        centroid = numpy.zeros(3)
        for i in range(4):
            for j in range(4):
                cp[i][j][2] = 3*random.random()
                centroid+= cp[i][j]
        centroid/=16
        for i in range(4):
            for j in range(4):
                cp[i][j] -= centroid
        self.bSurface = bs = BezierSurface(cp)
        self.bSurfaceDisplay = BezierSurfaceDisplay(bs)
    def Init(self):
        glClearColor(0,0,0,1)
    def OnReshape(self,w,h):
        glViewport (0, 0, w, h)
	glMatrixMode (GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45,float(w)/float(h),.1,100)
        #glOrtho(-10,10,-10,10,-10,10)
        gluLookAt(0,0,10,
                  0,0,0.,
                  0,1.,0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    def OnDisplay(self):
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glColor(1,1,1)
        glutSolidSphere(.1,20,20)

        self.bSurfaceDisplay.Draw()
        
        glutSwapBuffers()
    def Run(self):
        glutInit(sys.argv)
	glutInitDisplayMode (GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(640,480)
        glutCreateWindow("Surface")
        glutDisplayFunc(self.OnDisplay)
        glutReshapeFunc(self.OnReshape)
        self.Init()
        glutMainLoop()



if __name__=='__main__':
    from Glinter.Widget import Canvas3D
    cp = numpy.array( [ [ [0,0,0],
                          [1,0,0],
                          [2,0,0],
                          [3.,0,0] ],
                        [ [0,1,0],
                          [1,1,0],
                          [2,1,0],
                          [3.,1,0] ],
                        [ [0,2,0],
                          [1,2,0],
                          [2,2,0],
                          [3.,2,0] ],
                        [ [0,3,0],
                          [1,3,0],
                          [2,3,0],
                          [3.,3,0] ] ] )
    exec (open('teapot.py').read())
    import random
    c = Canvas3D(eye=[0,0,10])
    centroid = numpy.zeros(3)
    for i in range(4):
        for j in range(4):
            cp[i][j][2] = 3*random.random()
            centroid+= cp[i][j]
    centroid/=16
    for i in range(len(teapot)):
        cp = numpy.array(teapot[i])
        for i in range(4):
            for j in range(4):
                cp[i][j] *= .01
        #print cp
        bs = BezierSurface(cp)
        bsd = BezierSurfaceDisplay(bs,resolution=15)
        c.actors.append(bsd)
    c.Run()
