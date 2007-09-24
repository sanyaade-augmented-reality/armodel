INC_DIR= /usr/local/include
LIB_DIR= /usr/local/lib
BIN_DIR= .

COMMON_OBJECTS=cxxsupport.o cxx_extensions.o cxxextensions.o IndirectPythonInterface.o


LDFLAG= -g -L$(LIB_DIR)
LIBS= -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -lobjc -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti 
PYLIBS= -bundle -g -u _PyMac_Error -lobjc -L$(LIB_DIR) -lAR -lARvideo -lARgsub -lARgsub_lite -lARmulti -framework Carbon -framework QuickTime -framework GLUT -framework OpenGL -framework AppKit -framework Foundation -F/Library/Frameworks -framework System -framework Python
CFLAG= -g -O -fPIC -I$(INC_DIR) -I/Library/Frameworks/Python.framework/Versions/2.5/include/python2.5 -I.

OBJS = object.o MarkerTracker.o ARSetup.o # ARControl.o 
PYOBJS = $(COMMON_OBJECTS) $(OBJS)
HEADERS = object.h MarkerTracker.hpp ARSetup.hpp # ARControl.hpp

all: AR.so VideoTest 

AR.so: $(PYOBJS) AR.o
	g++ -o AR.so AR.o $(PYOBJS) $(PYLIBS)

AR.o: AR.cpp
	g++ -c AR.cpp $(CFLAG) 

VideoTest: $(OBJS) VideoTest.o 
	g++ -o VideoTest VideoTest.o $(OBJS) $(LDFLAG) $(LIBS)

VideoTest.o: VideoTest.cpp $(HEADERS)
	g++ -c VideoTest.cpp $(CFLAG) 

object.o: object.c $(HEADDERS)
	g++ -c object.c $(CFLAG) 

MarkerTracker.o: MarkerTracker.cpp $(HEADDERS)
	g++ -c MarkerTracker.cpp $(CFLAG) 

ARSetup.o: ARSetup.cpp $(HEADDERS)
	g++ -c ARSetup.cpp $(CFLAG) 

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
	rm VideoTest
	rm *.so

