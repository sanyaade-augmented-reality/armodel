import Image
import os,sys

markerPath = os.path.join(
    os.environ['HOME'],
    'Development/ARToolKitPlus/id-markers/bch/'
    )

allImage = Image.open(os.path.join(markerPath,'AllBchThinMarkers.png'))
_size = allImage.size

def _eq(im0,im1):
    if im0.size != im1.size: return False
    for i in range(im0.size[0]):
        for j in range(im0.size[1]):
            if im0.getpixel((i,j)) != im1.getpixel((i,j)):
                return False
    return True

def getMarker(index):
    ndim,mdim = 64,64
    margin = 4
    msize = 8
    row = index/64
    col = index-row*64

    topLeft = [margin*(col+1)+col*msize,margin*(row+1)+row*msize]
    bottomRight = [topLeft[0]+msize,topLeft[1]+msize]
    bbox = (topLeft[0],topLeft[1],bottomRight[0],bottomRight[1])
            
    mImage = allImage.crop(bbox)
    mImage.load()

    return mImage

if __name__=='__main__':
    m = getMarker(int(sys.argv[1]) if len(sys.argv)>1 else 0)
    m.show()
