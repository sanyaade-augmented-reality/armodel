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

def mb1_24():
    msize = 53
    ms2 = msize/2
    horCentGap = 35
    hcg = horCentGap/2
    verCentGap = 34
    vcg = verCentGap/2
    horGap = 34
    verGap = 49
    topLeft = [-hcg-msize-horGap-msize-horGap-ms2,vcg+msize+verGap+ms2,7]
    rowOne = [
        topLeft,
        [topLeft[0]+msize+horGap, topLeft[1],8],
        [topLeft[0]+2*msize+2*horGap, topLeft[1],9],
#         [topLeft[0]+3*msize+2*horGap+horCentGap,topLeft[1],19],
#         [topLeft[0]+4*msize+3*horGap+horCentGap,topLeft[1],20],
#         [topLeft[0]+4*msize+3*horGap+horCentGap,topLeft[1],21],
        [hcg+ms2,topLeft[1],19],
        [hcg+msize+horGap+ms2,topLeft[1],20],
        [hcg+2*msize+2*horGap+ms2,topLeft[1],21],
        ]
    rowTwo = [
        [rowOne[0][0],rowOne[0][1]-msize-verGap,10],
        [rowOne[1][0],rowOne[1][1]-msize-verGap,11],
        [rowOne[2][0],rowOne[2][1]-msize-verGap,12],
        [rowOne[3][0],rowOne[3][1]-msize-verGap,22],
        [rowOne[4][0],rowOne[4][1]-msize-verGap,23],
        [rowOne[5][0],rowOne[5][1]-msize-verGap,24],
        ]
    rowThree = [
        [rowTwo[0][0],-vcg-ms2,1],
        [rowTwo[1][0],-vcg-ms2,2],
        [rowTwo[2][0],-vcg-ms2,3],
        [rowTwo[3][0],-vcg-ms2,13],
        [rowTwo[4][0],-vcg-ms2,14],
        [rowTwo[5][0],-vcg-ms2,15],
        ]
    rowFour = [
        [rowThree[0][0],rowThree[0][1]-msize-verGap,4],
        [rowThree[1][0],rowThree[1][1]-msize-verGap,5],
        [rowThree[2][0],rowThree[2][1]-msize-verGap,6],
        [rowThree[3][0],rowThree[3][1]-msize-verGap,16],
        [rowThree[4][0],rowThree[4][1]-msize-verGap,17],
        [rowThree[5][0],rowThree[5][1]-msize-verGap,18],
        ]
    positions = [
        rowOne,
        rowTwo,
        rowThree,
        rowFour,
        ]
    config = configHead
    for i,row in enumerate(positions):
        for j,point in enumerate(row):
            x,y,mId = point
            config += markerText%(mId,mId,msize,x,y)

    fnameRoot = 'markerboard1_24'
    # save config file
    fp = open(os.path.join('data',fnameRoot+'.cfg'),'w')
    fp.write(config)
    fp.close()
            
        

if __name__=='__main__':
    if 0:
        markers = eval(sys.argv[1])
        if type(markers[0]) is type(1):
            mp = MarkerPanel(markers)
        else:
            for mlist in markers:
                mp = MarkerPanel(mlist)
        #mp.mainImage.show()
    else:
        mb1_24()
