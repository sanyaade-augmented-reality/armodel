#ifndef __framework_h__
#define __framework_h__

// ============================================================================
//	Includes
// ============================================================================

#include <assert.h>
#include <stdio.h>
#include <stdlib.h> // malloc(), free()
#include <string.h>
#include <math.h>

#ifdef __APPLE__
#  include <GLUT/glut.h>
#else
#  include <GL/glut.h>
#endif

#include <AR/config.h>
#include <AR/video.h>
#include <AR/param.h> // arParamDisp()
#include <AR/ar.h>
#include <AR/gsub.h>
#include <AR/gsub_lite.h>
#include <AR/arMulti.h>
#include "object.h"

#include <string>
#include <vector>
#include <iostream>

using namespace std;

#include "ARSetup.hpp"
#include "MarkerTracker.hpp"
/*#include "ARControl.hpp"*/

#endif // __framework_h__
