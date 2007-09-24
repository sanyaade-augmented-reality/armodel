#include "framework.hpp"


// ============================================================================
//	Constants
// ============================================================================

// ============================================================================
//	Global variables
// ============================================================================

// Image acquisition.
static ARUint8 *imageData = NULL;

// Drawing.
//static ARParam gARTCparam;
//static ARGL_CONTEXT_SETTINGS_REF gArglSettings = NULL;

static MarkerTracker tracker = MarkerTracker();
static ARSetup setup = ARSetup();

static double screen_position[2];
static int found;
static double zeroTrans[3][4] = { {1,0,0,0},
                                  {0,1,0,0},
                                  {0,0,1,0} };
static double cp[4][4][3] = { { {0,0,4},
                                {10,0,18},
                                {20,0,12},
                                {30,0,20} },
                              { {0,10,0},
                                {10,10,0},
                                {20,10,0},
                                {30,10,0} },
                              { {0,20,0},
                                {10,20,0},
                                {20,20,0},
                                {30,20,0} },
                              { {0,30,0},
                                {10,30,0},
                                {20,30,0},
                                {30,30,0} } };
static double work[4][4][3];
static void copycp() {
  int i,j,k;
  for (i=0;i<4;i++)
    for (j=0;j<4;j++)
      for(k=0;k<3;k++)
        work[i][j][k] = cp[i][j][k];
}
#define RES 20
static double dp[RES][RES][3];
static double np[RES][RES][3];
static void deCast(double u, double v, double pt[3]) {
  int i,j,k,l;
  copycp();
  for(i=0;i<4;i++) {
    for(k=1;k<4;k++) {
      for(j=0;j<4-k;j++) {
        for(l=0;l<3;l++) 
          work[i][j][l] = (1-u)*work[i][j][l] + u*work[i][j+1][l];
      }
    }
  }
  for(k=0;k<4;k++) {
    for(i=0;i<4-k;i++) {
      for(l=0;l<3;l++)
        work[i][0][l] = (1-v)*work[i][0][l] + v*work[i+1][0][l];
    }
  }
  for(i=0;i<3;i++)
    pt[i] = work[0][0][i];
}
static void makeBez() {
  /*
        bs = self.bSurface
        res = self.resolution
        for i in range(res):
            u = float(i)/res
            for j in range(res):
                v = float(j)/res
                self.drawPoints[i][j] = bs(u,v)
        dp = self.drawPoints
        for i in range(res-1):
            for j in range(res-1):
                self.normPoints[i][j] = numpy.cross(dp[i][j+1]-dp[i][j],
                                                    dp[i+1][j]-dp[i][j])
  */
  int i,j,k;
  double u,v,pt[3];
  for (i=0;i<RES;i++) {
    u = ((float) i)/RES;
    for(j=0;j<RES;j++) {
      v = ((float) j)/RES;
      deCast(u,v,pt);
      for(k=0;k<3;k++)
        dp[i][j][k] = pt[k];
    }
  }
}

static int frameCount=0;

// Something to look at, draw a rotating colour cube.
static void DrawCube(void)
{
  // Colour cube data.
  static GLuint polyList = 0;
  float fSize = 0.5f;
  long f, i;	
  const GLfloat cube_vertices [8][3] = {
    {1.0, 1.0, 1.0}, {1.0, -1.0, 1.0}, {-1.0, -1.0, 1.0}, {-1.0, 1.0, 1.0},
    {1.0, 1.0, -1.0}, {1.0, -1.0, -1.0}, {-1.0, -1.0, -1.0}, {-1.0, 1.0, -1.0} };
  const GLfloat cube_vertex_colors [8][3] = {
    {1.0, 1.0, 1.0}, {1.0, 1.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 1.0, 1.0},
    {1.0, 0.0, 1.0}, {1.0, 0.0, 0.0}, {0.0, 0.0, 0.0}, {0.0, 0.0, 1.0} };
  GLint cube_num_faces = 6;
  const short cube_faces [6][4] = {
    {3, 2, 1, 0}, {2, 3, 7, 6}, {0, 1, 5, 4}, {3, 0, 4, 7}, {1, 2, 6, 5}, {4, 5, 6, 7} };
	
  if (!polyList) {
    polyList = glGenLists (1);
    glNewList(polyList, GL_COMPILE);
    glBegin (GL_QUADS);
    for (f = 0; f < cube_num_faces; f++)
      for (i = 0; i < 4; i++) {
        glColor3f (cube_vertex_colors[cube_faces[f][i]][0], cube_vertex_colors[cube_faces[f][i]][1], cube_vertex_colors[cube_faces[f][i]][2]);
        glVertex3f(cube_vertices[cube_faces[f][i]][0] * fSize, cube_vertices[cube_faces[f][i]][1] * fSize, cube_vertices[cube_faces[f][i]][2] * fSize);
      }
    glEnd ();
    glColor3f (0.0, 0.0, 0.0);
    for (f = 0; f < cube_num_faces; f++) {
      glBegin (GL_LINE_LOOP);
      for (i = 0; i < 4; i++)
        glVertex3f(cube_vertices[cube_faces[f][i]][0] * fSize, cube_vertices[cube_faces[f][i]][1] * fSize, cube_vertices[cube_faces[f][i]][2] * fSize);
      glEnd ();
    }
    glEndList ();
  }
	
  glPushMatrix(); // Save world coordinate system.
  glTranslatef(0.0, 0.0, 0.5); // Place base of cube on marker surface.
  //glDisable(GL_LIGHTING);	// Just use colours.
  glCallList(polyList);	// Draw the cube.
  glPopMatrix();	// Restore world coordinate system.
	
}

static void draw( double trans1[3][4], double trans2[3][4], int mode )
{
    double    gl_para[16];
    GLfloat   mat_ambient[]     = {0.0, 0.0, 1.0, 1.0};
    GLfloat   mat_ambient1[]    = {1.0, 0.0, 0.0, 1.0};
    GLfloat   mat_flash[]       = {0.0, 0.0, 1.0, 1.0};
    GLfloat   mat_flash1[]      = {1.0, 0.0, 0.0, 1.0};
    GLfloat   mat_flash_shiny[] = {50.0};
    GLfloat   mat_flash_shiny1[]= {50.0};
    GLfloat   light_position[]  = {100.0,-200.0,200.0,0.0};
    GLfloat   ambi[]            = {0.1, 0.1, 0.1, 0.1};
    GLfloat   lightZeroColor[]  = {0.9, 0.9, 0.9, 0.1};
    
    argDrawMode3D();
    argDraw3dCamera( 0, 0 );
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    
    /* load the camera transformation matrix */
    glMatrixMode(GL_MODELVIEW);
    argConvGlpara(trans1, gl_para);
    glLoadMatrixd( gl_para );
    argConvGlpara(trans2, gl_para);
    glMultMatrixd( gl_para );

    if( mode == 0 ) {
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_POSITION, light_position);
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambi);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor);
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_flash);
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_flash_shiny);	
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient);
    }
    else {
        glEnable(GL_LIGHTING);
        glEnable(GL_LIGHT0);
        glLightfv(GL_LIGHT0, GL_POSITION, light_position);
        glLightfv(GL_LIGHT0, GL_AMBIENT, ambi);
        glLightfv(GL_LIGHT0, GL_DIFFUSE, lightZeroColor);
        glMaterialfv(GL_FRONT, GL_SPECULAR, mat_flash1);
        glMaterialfv(GL_FRONT, GL_SHININESS, mat_flash_shiny1);	
        glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient1);
    }
    glMatrixMode(GL_MODELVIEW);
    //glTranslatef( 0.0, 0.0, 25.0 );
    //glutSolidCube(50.0);
    glBegin(GL_POLYGON);
    glVertex3f(-25,-25,0);
    glVertex3f(-25,25,0);
    glVertex3f(25,25,0);
    glVertex3f(25,-25,0);
    glEnd();
    glTranslatef( 0.0, 0.0, 0.0 );
    glutSolidCone(10,50,20,20);
    glDisable( GL_LIGHTING );

    glDisable( GL_DEPTH_TEST );
}

static void Quit(void)
{
  setup.CleanUp();
  exit(0);
}

static void Keyboard(unsigned char key, int x, int y)
{
  int mode;
  switch (key) {
  case 0x1B:  // Quit.
  case 'Q':
  case 'q':
    Quit();
    break;
  case ' ':
    break;
  default:
    break;
  }
}

//
// This function is called when the window needs redrawing.
//
static void MainLoop(void)
{
  int i,j;
  GLdouble p[16];
  GLdouble m[16];
	
  // Grab a video frame.
  if( (imageData = (ARUint8 *)arVideoGetImage()) == NULL ) {
    arUtilSleep(2);
    return;
  }
  if( frameCount == 0 ) arUtilTimerReset();
  frameCount++;

  tracker.Track(imageData);
  int nFound,foundIds[10];
  if ((nFound=tracker.GetFound(foundIds)) > 0) {
    for (i=0;i<nFound;i++) {
      tracker.GetScreenPos(foundIds[i],screen_position);
      //cout << "Ping "<< i << " "<< screen_position[0] << " " << screen_position[1] << endl;
    }
  }

  argDrawMode2D();
  //argDispImage(imageData, 0,0);
  ARParam *cparam = setup.GetCParam();
  arglDispImage( imageData,cparam,1.0,setup.GetArglSettings());

  arVideoCapNext();
  // Image data is no longer valid after calling arVideoCapNext().
  imageData = NULL; 

  argDrawMode3D();
  argDraw3dCamera( 0, 0 );
  glClearDepth( 1.0 );
  glClear(GL_DEPTH_BUFFER_BIT);
  if (nFound>0) {
    double trans[3][4];
    for (i=0;i<nFound;i++) {
      tracker.GetTrans(foundIds[0],trans);
      draw(trans,zeroTrans,0);
    }
  }
  
  ARMultiMarkerInfoT *multi = tracker.GetMulti();
  if (tracker.GetMultiErr() < 0) {
    argSwapBuffers();
    return;
  }
  if(tracker.GetMultiErr() > 100.0 ) {
    argSwapBuffers();
    return;
  }

  argDrawMode3D();
  argDraw3dCamera( 0, 0 );
  glEnable(GL_DEPTH_TEST);
  glDepthFunc(GL_LEQUAL);
    
  /* load the camera transformation matrix */
  double    gl_para[16];
  glMatrixMode(GL_MODELVIEW);
  argConvGlpara(multi->trans, gl_para);
  glLoadMatrixd( gl_para );
  glTranslatef(-30,-30,0);
  glScalef(5,5,5);
  for(j=0;j<RES-1;j++) {
    for(i=0;i<RES;i++) {
      glColor3f(i/((float) RES),j/((float) RES),1);
      glPushMatrix();
      glTranslatef(dp[i][j][0],dp[i][j][1],dp[i][j][2]);
      glutSolidSphere(1,10,10);
      glPopMatrix();
    }
    glBegin(GL_QUAD_STRIP);
    for(i=0;i<RES;i++) {
      //cout << dp[i][j][0] << " " << dp[i][j][1] << " " << dp[i][j][2] << endl;
      glVertex3d(dp[i][j][0],dp[i][j][1],dp[i][j][2]);
      glVertex3d(dp[i][j+1][0],dp[i][j+1][1],dp[i][j+1][2]);
    }
    glEnd();
  }
  /*
  for( i = 0; i < multi->marker_num; i++ ) {
    if( multi->marker[i].visible >= 0 )
      draw( multi->trans, multi->marker[i].trans, 0 );
    else
      draw( multi->trans, multi->marker[i].trans, 1 );
  }
  */
  argSwapBuffers();
}

int main(int argc, char **argv)
{
  // -------------------------------------------------------------------
  // Hardware setup.
  //

  glutInit(&argc, argv);

  if (!setup.SetupCamera()) {
    fprintf(stderr, "main(): Unable to set up AR camera.\n");
    exit(-1);
  }

  if (!tracker.InitTracker()) {
    fprintf(stderr, "main(): Unable to set up AR marker.\n");
    Quit();
  }
  tracker.SetThreshold(85);

  makeBez();

  // -------------------------------------------------------------------
  // Library setup.
  //

  setup.SetupWindow();

  glEnable(GL_DEPTH_TEST);
  glDepthFunc(GL_LEQUAL);
    
  if (!setup.StartCamera()) {
    fprintf(stderr, "main(): Unable to start AR camera.\n");
    exit(-1);
  }

  argMainLoop( NULL, Keyboard, MainLoop );
  return (0);
}
