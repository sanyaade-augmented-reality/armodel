INC_DIR= /usr/local/include
LIB_DIR= /usr/local/lib
BIN_DIR= .

COMMON_OBJECTS=cxxsupport.o cxx_extensions.o cxxextensions.o IndirectPythonInterface.o


LDFLAG= -g -L$(LIB_DIR)
PYLIBS= -bundle -g -u _PyMac_Error -lobjc -F/System/Library/Frameworks -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -framework System -framework Python -L$(LIB_DIR) -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti -lcv -lcxcore -lhighgui -L$(ARTKP)/lib -lARToolKitPlus
CFLAG= -g -O -fPIC -I$(INC_DIR) -I/usr/include/python2.5 -I. -I$(ARTKP)/include -I$(ARTKP)/src -I$(ARTKP) #-I/usr/local/Qt4.3/mkspecs/darwin-g++  -march=pentium4 -msse2 -msse -mtune=pentium4 

OBJS = object.o MarkerTracker.o ARSetup.o ARCV.o 
PYOBJS = $(COMMON_OBJECTS) $(OBJS)
HEADERS = object.h MarkerTracker.hpp ARSetup.hpp ARCV.hpp # framework.hpp 

all: AR.so 

AR.so: $(PYOBJS) AR.o
	g++ -o AR.so AR.o $(PYOBJS) $(PYLIBS)

AR.o: AR.cpp
	g++ -c AR.cpp $(CFLAG) 

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

