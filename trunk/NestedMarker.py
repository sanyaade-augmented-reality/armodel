import os,sys
import numpy
import numpy.random as random
import optparse

import Image,ImageDraw,pprint
binary = lambda n: n>0 and [n&1]+binary(n>>1) or []

import Marker

class NestedMarker(Marker.Marker):
    pass

def binary(n):
    s = numpy.binary_repr(n).zfill(16)
    a = numpy.array(map(int,list(s))).reshape((4,4))
    s = ' '.join(list(s))
    return s,a
        
import leven

HTMLBP = """
<html>
  <body>
    <table cellspacing="60">
      %s
    </table>
  </body>
</html>
"""

class NestedMarkerCreator:
    similarity = 1
    size = 4
    sizeSquared = size**2
    two16 = 2**16
    def __init__(self,**kw):
        op = optparse.OptionParser()
        op.add_option('-f','--file',dest='markerDirName',
                      help='name of directory to store nested marker',
                      default='testNested')
        op.add_option('-v','--verbose',dest='verbose',
                      action="store_true")
        args = []
        if __name__=='__main__': args = sys.argv
        (options,args) = op.parse_args(args)
        self.__dict__.update(options.__dict__)
        self.__dict__.update(kw)
        self.randomIntegers = []
    def oldsimilar(self,value,values):
        if value in values: return 1
        testpatt,array = binary(value)
        minDistance = 4
        if self.verbose:
            print 
            print 'In Similar:'
            print 'Test pattern:',testpatt
        for i,v in enumerate(values):
            patt,array = binary(v)
            distance = leven.leven(patt,testpatt)
            if self.verbose:
                print '    Test:',testpatt
                print 'Rotate 0:',patt,'Leven:',distance
            if distance <= minDistance:
                if self.verbose:
                    print 'XXX --> TOO SIMILAR! RESETTING!'
                    return 1
            for j in range(3):
                patt = self.rotate(patt)
                distance = leven.leven(patt,testpatt)
                if self.verbose:
                    print 'Rotate %s:'%(j+1),patt,'Leven:',distance
                if distance <= minDistance:
                    if self.verbose:
                        print 'XXX --> TOO SIMILAR! RESETTING!'
                    return 1
    def similar(self,value,values):
        if value in values: return 1
        newPatt,newArray = binary(value)
        for v in values:
            testPatt,testArray = binary(v)
            angle = 0
            for i in range(3):
                testArray = numpy.rot90(testArray)
                angle+=90
                if (newArray == testArray).all():
                    print 'Found match! Angle:',angle
                    return 1
    def Generate(self,**kw):
        self.__dict__.update(kw)
        # create directory if it doesn't exist
        if not os.path.exists(self.markerDirName):
            os.mkdir(self.markerDirName)
        os.chdir(self.markerDirName)
            
        # create nested marker
        l1,l2,l3 = [],[],[]
        self.nestedMarkerDict = {'l1':l1,'l2':l2,'l3':l3}

        # Level 1: 16x16 markers, 16 of them
        bd,pwidth=5,32
        blockw = pwidth/4
        randints = []
        randints.extend(self.randomIntegers)
        tableRows = [[]]
        for i in range(4):
            l1.append([])
            for j in range(4):
                """
                rand = random.randint(self.two16)
                if random.random()<.9:
                    rand = random.randint(32)
                    if random.random()<.5:
                        rand <<= random.randint(8)
                while self.similar(rand, randints):
                    rand = random.randint(self.two16)
                randints.append(rand)
                """
                rand = 0
                for v in random.random_integers(1,15,size=3):
                    flip = 1<<v
                    if not flip&rand:
                        rand += flip
                    else:
                        rand -= flip
                #rand = random.randint(1,16)<<random.randint(8)
                if random.random() <= .5: rand = 2**16-1-rand
                if rand in randints: #self.similar(rand,randints):
                    rand = 2**16-1-rand
                #while rand in randints: #self.similar(rand,randints):
                while self.similar(rand,randints):
                    for v in random.random_integers(1,15,size=3):
                        flip = 1<<v
                        if not flip&rand:
                            rand += flip
                        else:
                            rand -= flip
                    """
                    flip = 1<<random.randint(15)
                    if not flip&rand:
                        rand += flip
                    else:
                        rand -= flip
                    """
                print rand
                randints.append(rand)
                patt,array = binary(rand)
                im = Image.new('L',(2*bd+pwidth,)*2)
                draw = ImageDraw.Draw(im)
                for k in range(4):
                    for l in range(4):
                        xy = (bd+blockw*l,bd+blockw*k,
                              bd+blockw*(l+1)-1,bd+blockw*(k+1)-1)
                        if array[k][l]:
                            draw.rectangle(xy,fill='white')
                imfname = 'test.L1.%s%s.gif'%(i,j)
                lastRow = tableRows[-1]
                if len(lastRow) < 2:
                    lastRow.append(imfname)
                else:
                    tableRows.append([imfname])
                imLarge = im.resize((227,227))
                imLarge.save(imfname)
                stringPatt = self.genText(patt,4)
                spfname = 'test.L1.%s%s.patt'%(i,j)
                f = open(spfname,'w')
                f.write(stringPatt)
                f.close()
                l1[-1].append({'intPattern':patt,
                               'stringPattern':stringPatt,
                               'array':array,
                               'imageFileName':imfname,
                               'stringPattFileName':spfname,
                               'imageObject': im})
        
        # Level 2: composite of Level 1 markers (4 x L1)
        bd,ws,pwidth = 3*bd,bd,l1[0][0]['imageObject'].size[0]
        imwidth = 2*bd+4*ws+2*pwidth
        for i in range(2):
            l2.append([])
            for j in range(2):
                ii,jj = 2*i,2*j
                #ind=[(i,j),(i,j+1),(i+1,j),(i+1,j+1)]
                patts = [l1[ii][jj],l1[ii][jj+1],l1[ii+1][jj],l1[ii+1][jj+1]]
                im = Image.new('L',(imwidth,imwidth))
                draw = ImageDraw.Draw(im)
                draw.rectangle((bd,bd,imwidth-bd-1,imwidth-bd-1),fill='white')
                im.paste(patts[0]['imageObject'],(bd+ws,bd+ws))
                im.paste(patts[1]['imageObject'],(bd+ws+pwidth+2*ws,bd+ws))
                im.paste(patts[2]['imageObject'],(bd+ws,bd+ws+pwidth+2*ws))
                im.paste(patts[3]['imageObject'],(bd+ws+pwidth+2*ws,
                                                  bd+ws+pwidth+2*ws))
                lastRow = tableRows[-1]
                fname = 'test.L2.%s%s.gif'%(i,j)
                if len(lastRow) < 2:
                    lastRow.append(fname)
                else:
                    tableRows.append([fname])
                imLarge = im.resize((227,227))
                imLarge.save(fname)
                spname = 'test.L2.%s%s.patt'%(i,j)
                # crop the border, resize to 16,16
                pim = im.crop((bd,bd,imwidth-bd,
                               imwidth-bd)).resize((16,16),
                                                   Image.ANTIALIAS)
                parray = pim.load()
                stringPattern = ''
                for rotate in range(4):
                    for duplicate in range(3):
                        for ii in range(16):
                            for jj in range(16):
                                s = '%s '%parray[ii,jj]
                                stringPattern += s.ljust(4)
                            stringPattern += '\n'
                    stringPattern += '\n'
                    pim = pim.rotate(90)
                    parray = pim.load()
                # write pattern out
                f = open(spname,'w'); f.write(stringPattern); f.close()
                l2[-1].append({'imageFileName':fname,
                               'imageObject':im,
                               'stringPattern':stringPattern,
                               'stringPattFileName':spname})

        # Write out table HTML code for L1 and L2
        tableText = ''
        for row in tableRows:
            row = tuple(row)
            if len(row) == 2:
                tableText+= ('<tr><td><img src="%s"/></td>'
                             '<td><img src="%s"</td></tr>\n'%row)
                tableText+= ('<tr><td>%s</td><td>%s</td></tr>\n'%row)
            else:
                print row
                tableText+= ('<tr><td><img src="%s"/></td></tr>\n'%row)
                tableText+= ('<tr><td>%s</td></tr>\n'%row)

        # Level 3: composite of Level 2 markers (4 x L2)
        bd,ws,pwidth = 3*bd,3*ws,l2[0][0]['imageObject'].size[0]
        imwidth = 2*bd+4*ws+2*pwidth
        patts = [l2[0][0],l2[0][1],l2[1][0],l2[1][1]]
        im = Image.new('L',(imwidth,imwidth))
        draw = ImageDraw.Draw(im)
        draw.rectangle((bd,bd,imwidth-bd-1,imwidth-bd-1),fill='white')
        im.paste(patts[0]['imageObject'],(bd+ws,bd+ws))
        im.paste(patts[1]['imageObject'],(bd+ws+pwidth+2*ws,bd+ws))
        im.paste(patts[2]['imageObject'],(bd+ws,bd+ws+pwidth+2*ws))
        im.paste(patts[3]['imageObject'],(bd+ws+pwidth+2*ws,
                                          bd+ws+pwidth+2*ws))
        fname = 'test.L3.gif'
        im.save(fname)
        spname = 'test.L3.patt'

        tableText += '<tr><td colspan=2><img src="test.L3.gif"/></td></tr>'
        
        # Write out HTML page with images on it for printing
        htmlText = HTMLBP%tableText
        htmlFP = open('test.html','w')
        htmlFP.write(htmlText)
        htmlFP.close()

        # crop the border, resize to 16,16
        pim = im.crop((bd,bd,imwidth-bd,
                       imwidth-bd)).resize((16,16),
                                           Image.ANTIALIAS)
        parray = pim.load()
        stringPattern = ''
        for rotate in range(4):
            for duplicate in range(3):
                for ii in range(16):
                    for jj in range(16):
                        s = '%s '%parray[ii,jj]
                        stringPattern += s.ljust(4)
                    stringPattern += '\n'
            stringPattern += '\n'
            pim = pim.rotate(90)
            parray = pim.load()
        # write pattern out
        f = open(spname,'w'); f.write(stringPattern); f.close()
        l3.append({'filename':fname,
                   'imageObject':im})
        self.randomIntegers.extend(randints)
        os.chdir('..')

    def GetStringPattern(self,image):
        # crop the border, resize to 16,16
        pim = image.crop((bd,bd,imwidth-bd,
                          imwidth-bd)).resize((16,16),
                                              Image.ANTIALIAS)
        parray = pim.load()
        stringPattern = ''
        for rotate in range(4):
            for duplicate in range(3):
                for ii in range(16):
                    for jj in range(16):
                        stringPattern += '%s '%parray[ii,jj]
                    stringPattern += '\n'
            stringPattern += '\n'
            pim = pim.rotate(90)
            parray = pim.load()
        # write pattern out
        f = open(spname,'w'); f.write(stringPattern); f.close()
        
    def genText (self, line, size):
        # transliterated from UUtah function
	dup = 0;
	if (size == 4):
	    dup = 4; # number of duplications for a 4x4
	elif (size == 3):
	    dup = 5; # number of duplications for a 3x3
        stringPatt = ''
	tempPattS = line;  
	tempC='';
	for u in range(4):
            for w in range(3): # each pattern is duped 3 times
                for x in range(size): # for each line of pattern
                    for z in range(dup): # do each line multiple times
                        for n in range(size):
			    tempC = tempPattS[n * 2 + size * x * 2];
			    if (tempC == '0'):
                                for y in range(dup):
				    stringPatt+=("255 ");
			    if (tempC == '1'):
                                for y in range(dup):
				    stringPatt+=("0   ");
			stringPatt+=('\n');
	    stringPatt+=('\n'); # add a blank line between rotations
	    
	    tempPattS = self.rotate(tempPattS);  # rotate 3 times right
        return stringPatt
    
    # written by chris
    def RIDX(self, i, j,  n):
	return (i)*(n)+(j) 
    def str2array(self,pattS):
        return map(int,pattS.split())
    def array2str(self,inarray):
        return ' '.join(map(str,inarray))
    def rotate(self,inStr):
	src = self.str2array(inStr);
	dim = int(numpy.sqrt(len(src)))
	rtn = numpy.zeros(dim*dim,'int');
        for i in range(dim):
            for j in range(dim):
		rtn[self.RIDX(dim-1-j, i, dim)] = src[self.RIDX(i, j, dim)]
	return self.array2str(rtn)

if __name__=='__main__':
    n = NestedMarkerCreator()
    if 1:
        directories = sys.argv[1:]
        for directory in directories:
            n.Generate(markerDirName=directory)
    else:
        for i in range(30):
            n.Generate(markerDirName='testMarker.%s'%str(i))
    
