import os,sys
import xml.etree.ElementTree as etree

import Image

from bchMarkers import getMarker

configHead = """# produced by multiMarker.py

# number of markers
6
"""

markerText = """
# marker %s
%s
40.0
0.0 0.0
 1.0000  0.0000 0.0000  %s
 0.0000  1.0000 0.0000  %s
 0.0000  0.0000 1.0000  0.000
"""

class MarkerPanel:
    # multi-marker panel with 6 markers on it
    size = (1100,850)
    margin = 50 # margin around markers
    markerSize = 220 # size of markers on page
    layout = (2,3)
    def __init__(self,markers,
                 size=size,
                 layout = layout,
                 margin=margin,
                 markerSize=markerSize,
                 ):
        margin = margin
        msize = markerSize

        mImages = self.markerImages = []
        for markerId in markers:
            image = getMarker(markerId)
            new = image.resize((msize,msize))
            mImages.append(new)
        
        firstRow = [ [0,0], [0,0], [0,0] ]
        secondRow = [ [0,0], [0,0], [0,0] ]
        positions = self.markerPositions = [
            firstRow,
            secondRow,
            ]

        mainImage = self.mainImage = Image.new('RGB',size,(255,255,255))
        cx,cy = size[0]/2,size[1]/2
        hsize = msize/2
        if 0:
            firstRow[1] = [cx - hsize,cy - msize - margin]
            secondRow[1] = [cx - hsize,cy + margin]
            firstRow[0] = [firstRow[1][0]-2*margin-msize,firstRow[1][1]]
            secondRow[0] = [secondRow[1][0]-2*margin-msize,secondRow[1][1]]
            firstRow[2] = [firstRow[1][0]+2*margin+msize,firstRow[1][1]]
            secondRow[2] = [secondRow[1][0]+2*margin+msize,secondRow[1][1]]
        else:
            sw,sh = size[0]/3.,size[1]/2.
            cx,cy = sw/2,sh/2
            firstRow[0] = [cx-hsize,cy-hsize]
            secondRow[0] = [firstRow[0][0],firstRow[0][1]+sh]
            firstRow[1] = [firstRow[0][0]+sw,firstRow[0][1]]
            secondRow[1] = [firstRow[1][0],secondRow[0][1]]
            firstRow[2] = [firstRow[1][0]+sw,firstRow[0][1]]
            secondRow[2] = [firstRow[2][0],secondRow[0][1]]
        mIndex = 0
        for row in positions:
            for point in row:
                mImage = mImages[mIndex]
                point = tuple(map(int,point))
                mainImage.paste(mImage,point)
                mIndex += 1
        fnameRoot = '%s_%s_%s_%s_%s_%s'%tuple(markers)
        mainImage.save(fnameRoot+'.jpg')

        config = configHead
        trans = [
            [-80,40],[0,40],[80,40],
            [-80,-40],[0,-40],[80,-40],
            ]
        for i,mId in enumerate(markers):
            x,y = map(float,trans[i])
            config += markerText%(mId,mId,x,y)

        fp = open(os.path.join('data',fnameRoot+'.cfg'),'w')
        fp.write(config)
        fp.close()
        

if __name__=='__main__':
    markers = eval(sys.argv[1])
    if type(markers[0]) is type(1):
        mp = MarkerPanel(markers)
    else:
        for mlist in markers:
            mp = MarkerPanel(mlist)
    #mp.mainImage.show()
