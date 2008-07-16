INC_DIR= /usr/local/include
LIB_DIR= /usr/local/lib
BIN_DIR= .

COMMON_OBJECTS=cxxsupport.o cxx_extensions.o cxxextensions.o IndirectPythonInterface.o


LDFLAG= -g -L$(LIB_DIR)
PYLIBS= -bundle -g -u _PyMac_Error -lobjc -L$(LIB_DIR) -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -F/Library/Frameworks -framework System -framework Python -lcv -lcxcore -lhighgui
CFLAG= -g -O -fPIC -I$(INC_DIR) -I/Library/Frameworks/Python.framework/Versions/2.5/include/python2.5 -I.

OBJS = object.o MarkerTracker.o ARSetup.o ARCV.o 
PYOBJS = $(COMMON_OBJECTS) $(OBJS)
HEADERS = framework.hpp object.h MarkerTracker.hpp ARSetup.hpp ARCV.hpp

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

