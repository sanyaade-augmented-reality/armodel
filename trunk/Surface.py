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

class SurfaceGroup:
    pass

class DisplayObject:
    __mvArray = None
    __mvMatrix = None
    def __init__(self,*a,**kw):
        pass
    def Draw(self,*a,**kw):
        pass
    __lightRack = None
    def LightRack(self):
        if not self.__lightRack:
            self.__lightRack = LightRack()
        return self.__lightRack
    def MoveLight(self,index,point):
        lights = self.LightRack()
        lights.MoveLight(index,point)
        lights.TurnOnLight(index)
    def Init(self):
        pass
    def GetMV(self):
        return self.__mvArray,self.__mvMatrix
    def GetMvMat(self):
        return self.__mvMatrix
    def SetMV(self,mvmat):
        # mvmat == (16,1) OpenGL model-view matrix
        self.__mvArray = numpy.array(mvmat).reshape(4,4).transpose()
        self.__mvMatrix = numpy.mat(self.__mvArray)
    def GetPointTransform(self,point4):
        mvMatrix = self.GetMvMat()
        mvinv = mvMatrix.I
        return (mvinv*point4.T).T
    def FindNearest(self,*a,**kw):
        pass
    def MoveHighlight(self,*a,**kw):
        pass

class SurfaceDisplay(DisplayObject):
    pass

class SurfaceGroupDisplay(DisplayObject):
    pass

if __name__=='__main__':
    from Glinter.Widget import Canvas3D
    from teapot import teapot
    c = Canvas3D(eye=[0,0,10])
    c.Run()
