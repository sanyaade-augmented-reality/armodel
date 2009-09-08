INC_DIR= /usr/local/include
LIB_DIR= /usr/local/lib
BIN_DIR= .

ARCH = $(shell uname)

ifeq ($(ARCH), Darwin)
PY_INCDIR = /Library/Frameworks/Python.framework/Versions/2.6/include/python2.6
else
PY_INCDIR = /usr/include/python2.6
endif

COMMON_OBJECTS=cxxsupport.o cxx_extensions.o cxxextensions.o IndirectPythonInterface.o

all: _AR.so 

#----------------------------------------------------------------
_AR_CFLAGS= -g -O -fPIC -I/usr/local/include -I$(PY_INCDIR) -I. -I$(ARTKP)/include -I$(ARTKP)/src -I$(ARTKP) #-I/usr/local/Qt4.3/mkspecs/darwin-g++  -march=pentium4 -msse2 -msse -mtune=pentium4
_AR_PYOBJECTS= $(COMMON_OBJECTS)
_AR_PYLIBS= -bundle -g -u _PyMac_Error -lobjc \
	-F/Library/Frameworks -framework Python \
	-F/System/Library/Frameworks -framework Carbon \
	-framework QuickTime -framework GLUT -framework OpenGL \
	-framework AppKit -framework Foundation -framework System \
	-L$(LIB_DIR) -lcv -lcxcore -lhighgui \
	-L$(ARTKP)/lib -lARToolKitPlus
_AR.so: $(_AR_PYOBJECTS) _AR.o
	g++ -o _AR.so _AR.o $(_AR_PYOBJECTS) $(_AR_PYLIBS)
_AR.o: _AR.cpp
	g++ -c _AR.cpp $(_AR_CFLAGS)
#----------------------------------------------------------------

#----------------------------------------------------------------
artkp.dylib: artkp.o
	g++ -dynamiclib -g -o libartkp.dylib artkp.o -L$(ARTKP)/lib -lARToolKitPlus 

artkp.o: artkp.cpp artkp.hpp
	g++ -c -mtune=pentium4 -march=pentium4 -msse2 -msse -g -D__USE_WS_X11__ -I/usr/local/Qt4.3/mkspecs/darwin-g++ -I. -I$(ARTKP)/include -I/usr/local/include -o artkp.o artkp.cpp

#----------------------------------------------------------------


PYLIBS= -bundle -g -u _PyMac_Error -lobjc -F/System/Library/Frameworks -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -framework System -F/Library/Frameworks -framework Python -L$(LIB_DIR) -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti -lcv -lcxcore -lhighgui -L$(ARTKP)/lib -lARToolKitPlus
CFLAG= -g -O -fPIC -I$(INC_DIR) -I$(PY_INCDIR) -I. -I$(ARTKP)/include -I$(ARTKP)/src -I$(ARTKP) #-I/usr/local/Qt4.3/mkspecs/darwin-g++  -march=pentium4 -msse2 -msse -mtune=pentium4 

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

