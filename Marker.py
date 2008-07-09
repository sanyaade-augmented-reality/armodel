import os,sys,optparse
import numpy
import numpy.random as random
import Image,ImageDraw

class Marker:
    origin = numpy.mat([0,0,0,1])
    def __init__(self,marker):
        self.marker = marker
        self.SetMV(marker['mvmat'])
        self.SetPoint3()
        self.SetPoint4()
    def __getitem__(self,key):
        return self.marker[key]
    def SetMV(self,mvmat):
        mvmat = numpy.array(mvmat).reshape(4,4)
        mvmat = numpy.mat(mvmat.transpose())
        self.mvmat = mvmat
    def GetMV(self):
        return self.mvmat
    def GetName(self):
        return self['name'].lower()
    def SetPoint3(self):
        mvmat = self.GetMV()
        pos = mvmat*Marker.origin.T
        self.point3 = numpy.resize(pos,3)
    def GetPoint3(self):
        return self.point3
    def SetPoint4(self):
        mvmat = self.GetMV()
        pos = mvmat*Marker.origin.T
        self.point4 = pos.T
    def GetPoint4(self):
        return self.point4
    
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
    def Draw(self,**kw):
        pass

class MarkerCreator:
    def __init__(self,**kw):
        op = optparse.OptionParser()
        op.add_option('-f','--file',dest='markerDirName',
                      help='name of marker file',
                      default='testMarker')
        op.add_option('-v','--verbose',dest='verbose',
                      action="store_true")
        args = []
        if __name__=='__main__': args = sys.argv
        self.__dict__.update(options.__dict__)
        self.__dict__.update(kw)
    

