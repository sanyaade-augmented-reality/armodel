INC_DIR= /usr/local/include
LIB_DIR= /usr/local/lib
BIN_DIR= .

COMMON_OBJECTS=cxxsupport.o cxx_extensions.o cxxextensions.o IndirectPythonInterface.o

all: newAR.so 

#----------------------------------------------------------------
newAR_CFLAGS= -g -O -fPIC -I/usr/local/include -I/usr/include/python2.5 -I. -I$(ARTKP)/include -I$(ARTKP)/src -I$(ARTKP) #-I/usr/local/Qt4.3/mkspecs/darwin-g++  -march=pentium4 -msse2 -msse -mtune=pentium4
newAR_PYOBJECTS= $(COMMON_OBJECTS)
newAR_PYLIBS= -bundle -g -u _PyMac_Error -lobjc \
	-F/System/Library/Frameworks -framework Carbon \
	-framework QuickTime -framework GLUT -framework OpenGL \
	-framework AppKit -framework Foundation -framework System \
	-framework Python -L$(LIB_DIR) -lcv -lcxcore -lhighgui \
	-L$(ARTKP)/lib -lARToolKitPlus
newAR.so: $(newAR_PYOBJECTS) newAR.o
	g++ -o newAR.so newAR.o $(newAR_PYOBJECTS) $(newAR_PYLIBS)
newAR.o: newAR.cpp
	g++ -c newAR.cpp $(newAR_CFLAGS)
#----------------------------------------------------------------

#----------------------------------------------------------------
artkp.dylib: artkp.o
	g++ -dynamiclib -g -o libartkp.dylib artkp.o -L$(ARTKP)/lib -lARToolKitPlus 

artkp.o: artkp.cpp artkp.hpp
	g++ -c -mtune=pentium4 -march=pentium4 -msse2 -msse -g -D__USE_WS_X11__ -I/usr/local/Qt4.3/mkspecs/darwin-g++ -I. -I$(ARTKP)/include -I/usr/local/include -o artkp.o artkp.cpp

#----------------------------------------------------------------


PYLIBS= -bundle -g -u _PyMac_Error -lobjc -F/System/Library/Frameworks -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -framework System -framework Python -L$(LIB_DIR) -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti -lcv -lcxcore -lhighgui -L$(ARTKP)/lib -lARToolKitPlus
CFLAG= -g -O -fPIC -I$(INC_DIR) -I/usr/include/python2.5 -I. -I$(ARTKP)/include -I$(ARTKP)/src -I$(ARTKP) #-I/usr/local/Qt4.3/mkspecs/darwin-g++  -march=pentium4 -msse2 -msse -mtune=pentium4 

OBJS = object.o MarkerTracker.o ARSetup.o ARCV.o 
PYOBJS = $(COMMON_OBJECTS) $(OBJS)
HEADERS = object.h MarkerTracker.hpp ARSetup.hpp ARCV.hpp # framework.hpp 

AR.so: $(PYOBJS) AR.o # artkpTracker.dylib
	g++ -o AR.so AR.o $(PYOBJS) $(PYLIBS)

AR.o: AR.cpp
	g++ -c AR.cpp $(CFLAG)

artkptest: artkptest.o artkpTracker.dylib 
	g++ -o artkptest artkptest.o -L. -lartkpTracker -L/usr/local/lib -lcv -lcxcore -lhighgui -L$(ARTKP)/lib -lARToolKitPlus -framework GLUT -framework OpenGL
artkptest.o: artkptest.cpp
	g++ -c artkptest.cpp -o artkptest.o -I/usr/local/include -I. -I$(ARTKP)/include -I/usr/local/include
artkpTracker.dylib: artkpTracker.hpp artkpTracker.o
	g++ -dynamiclib -g -o libartkpTracker.dylib artkpTracker.o -L$(ARTKP)/lib -lARToolKitPlus 
artkpTracker.o:
	g++ -c -mtune=pentium4 -march=pentium4 -msse2 -msse -g -D__USE_WS_X11__ -I/usr/local/Qt4.3/mkspecs/darwin-g++ -I. -I$(ARTKP)/include -I/usr/local/include -o artkpTracker.o artkpTracker.cpp

object.o: object.c $(HEADERS)
	g++ -c object.c $(CFLAG) 

MarkerTracker.o: MarkerTracker.cpp $(HEADERS)
	g++ -c MarkerTracker.cpp $(CFLAG) 

ARSetup.o: ARSetup.cpp $(HEADERS)
	g++ -c ARSetup.cpp $(CFLAG) 

ARCV.o: ARCV.cpp $(HEADERS)
	g++ -c ARCV.cpp $(CFLAG) 

#
#	common objects
#
cxxsupport.o: CXX/cxxsupport.cxx
	g++ -c $(CFLAG) -o $@ $<

cxx_extensions.o: CXX/cxx_extensions.cxx
	g++ -c $(CFLAG) -o $@ $<

cxxextensions.o: CXX/cxxextensions.c
	gcc -c $(CFLAG) -o $@ $<

IndirectPythonInterface.o: CXX/IndirectPythonInterface.cxx
	g++ -c $(CFLAG) -o $@ $< 


clean:
	rm *.o
#	rm VideoTest
	rm *.so

