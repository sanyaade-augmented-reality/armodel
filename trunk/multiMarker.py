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
%s
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

        cx,cy = size[0]/2,size[1]/2
        mIndex = 0
        config = configHead
        trans = [
            [ [-27.75,16.125],[0.0,16.125],[27.75,16.125] ],
            [ [-27.75,-16.125],[0.0,-16.125],[27.75,-16.125] ],
            ] # transforms for config file
        for i,row in enumerate(positions):
            for j,point in enumerate(row):
                mImage = mImages[mIndex]
                ipoint = tuple(map(int,point))
                mainImage.paste(mImage,ipoint)
                # setup config info
                if 0:
                    x = (point[0]+hsize) - cx
                    y = cy - (point[1]+hsize)
                else:
                    x,y = trans[i][j]
                #print point,cx,cy,x,y
                config += markerText%(markers[mIndex],markers[mIndex],
                                      16.125,x,y)

                mIndex += 1
        fnameRoot = '%s_%s_%s_%s_%s_%s'%tuple(markers)
        mainImage.save(fnameRoot+'.jpg')

        # save config file
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