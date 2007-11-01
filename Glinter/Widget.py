try:
    import Glinter.Core
except:
    import os,sys
    sys.path.append(os.path.join(os.environ['HOME'],'lib'))
from Glinter.Core import *

__all__=['Widget','Shutter','Button','Canvas3D']

class Widget(Core):
    def __init__(self,parent=None,**kw):
        options = (
            ('title','',self.Reset),
            ('size',(600,600),self.Reset),
            ('pos',(0,0),self.Reset),
            ('lighting',1,self.Reset),
            ('bg',[.4,.4,.4,1],self.Reset),
            ('gloptions',[],self.Reset),
            ('bd',0,self.Reset),
            )
        self.InitOptions(options,kw)
        self.AddWidget(parent,self)
    def Reset(self):
        self.StartLocal()
        self.ResetPosition()
        self.ResetSize()
        self.ResetGL()
        self.ResetPerspective()
        self.EndLocal()
    def ResetPosition(self):
        self.StartLocal()
        pos = self['pos']
        glutPositionWindow(pos[0],pos[1])
        self.EndLocal()
    def ResetSize(self):
        self.StartLocal()
        size = self['size']
        glutReshapeWindow(size[0],size[1])
        self.EndLocal()
    def ResetGL(self):
        self.StartLocal()
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        for option in self['gloptions']:
            glEnable(option)
        glColorMaterial(GL_FRONT_AND_BACK,GL_DIFFUSE)
        glShadeModel(GL_SMOOTH)
        self.EndLocal()
    def ResetPerspective(self):
        self.StartLocal()
        w,h=self['size']
        glViewport (0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, w, 0, h, -1000.,1000.);
        glMatrixMode(GL_MODELVIEW)
        self.EndLocal()
    def DrawBorder(self):
        bd=self['bd']
        w,h = self['size']
        self.DrawBox(0,w,0,h,bd)
    def DrawBox(self,left,right,bottom,top,size,which='raised'):
        colors=[(.3,.3,.3),(.45,.45,.45),
                (.6,.6,.6),(.75,.75,.75),]
        if which is 'lowered':
            colors.reverse()
        c=colors
        l,r,b,t=left,right,bottom,top
        glePolyCylinder([(l,b,0),(l,b,0),(r,b,0),(r,b,0)],
                        [c[0],c[1],c[1],c[1]],size)
        glePolyCylinder([(r,b,0),(r,b,0),(r,t,0),(r,t,0)],
                        [c[1],c[2],c[2],c[1]],size)
        glePolyCylinder([(r,t,0),(r,t,0),(l,t,0),(l,t,0)],
                        [c[2],c[3],c[3],c[2]],size)
        glePolyCylinder([(l,t,0),(l,t,0),(l,b,0),(l,b,0)],
                        [c[1],c[1],c[0],c[0]],size)

    def DrawText(self,x,y,string,color=(.8,.8,.8)):
        if not isinstance(string,DrawableString):
            string = self.ProcessString(string)
        font = string.font
        for i in range(len(string)):
            c = string[i]
            cw,ch = string.widths[i]
            glColor3f(color[0],color[1],color[2])
            glRasterPos2f(x,y)
            glutBitmapCharacter(font[0],ord(c))
            x+=cw
    def ProcessString(self,string,font):
        return DrawableString(string,font)

    def Display(self):
        self.StartLocal()

        bg=self['bg']
        glClearColor(bg[0],bg[1],bg[2],bg[3])
        glClear(GL_COLOR_BUFFER_BIT|
                GL_DEPTH_BUFFER_BIT)

        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()

        self.Draw()
        
        glPopMatrix()

        glutSwapBuffers()

    def Draw(self):
        pass

class Shutter(Widget,Geometry):
    __open=False
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options = (
            ('percent',50,self.Reset),
            ('side','right',self.Reset),
            ('bd',2),
            ('sticky',True,self.Reset),
            )
        self.InitOptions(options,kw)
        self.__open = self['sticky']
    def GetOpen(self):
        #print 'sticky',self['sticky']
        return self.__open
    def ResetPosition(self):
        self.StartLocal()
        if self['sticky']:
            self.__open=True
        x,y = self['pos']
        nx,ny=x,y
        geom = self.GetGeometry()
        w,h = self['size']
        parent = self.GetParent()
        pw,ph = parent['size']
        ny = int(ph*(self['percent']/100.)-h/2.)
        if self.GetOpen():
            #print str(parent)
            nx = pw-w
        else:
            nx = pw-(8+8)
        if (nx != x) or (ny != y):
            self.SetOption('pos',(nx,ny),False)
        pos = self['pos']
        glutPositionWindow(pos[0],pos[1])
        self.EndLocal()
    def Update(self,children=False):
        self.StartLocal()
        self.ResetPosition()
        glutPostRedisplay()
        self.EndLocal()
        if children:
            for child in self.GetChildren():
                child.Update(children)
    def Reset(self):
        #self.__open=False
        Widget.Reset(self)
    def TopLeft(self):
        return self['bd']+20,8+8+self['bd']
    def OnMouse(self):
        if self.RightButton():
            self['sticky']=not self['sticky']
    def OnEntry(self):
        mx,my = self.GetMousePosition('passive','current')
        w,h=self['size']
        lx,ty = glutGet(GLUT_WINDOW_X),glutGet(GLUT_WINDOW_Y)
        rx,by = glutGet(GLUT_WINDOW_X)+w,glutGet(GLUT_WINDOW_Y)+h
        fudge = 15
        #print mx,my
        if mx>=(lx-fudge) and mx<=(lx+fudge):
            if self.Left():
                #print 'left to the left'
                self.__open=False
            else:
                #print 'entered to the left'
                self.__open=True
            self.Reset()
            self.Update()
        elif my>=(ty-fudge) and my<=(ty+fudge):
            if self.Left():
                #print 'left to the top'
                self.__open=False
            else:
                #print 'entered to the top'
                self.__open=True
            self.Reset()
            self.Update()
        elif my>=(by-fudge) and my<=(by+fudge):
            if self.Left():
                #print 'left to the bottom'
                self.__open=False
            else:
                #print 'entered to the bottom'
                self.__open=True
            self.Reset()
            self.Update()
    def DrawStickyBox(self):
        w,h=self['size']
        sbsize=7
        sbbd=1
        sbpad=4
        x,y = w-2*sbbd-sbpad-sbsize,h-2*sbbd-sbpad-sbsize
        if (self['sticky']):
            c=(.5,.5,.5)
        else:
            c=(.7,.7,.7)
        glColor3f(c[0],c[1],c[2])
        glBegin(GL_POLYGON)
        glVertex3f(x+sbbd,y+sbbd,0)
        glVertex3f(x+sbsize+sbbd,y+sbbd,0)
        glVertex3f(x+sbsize+sbbd,y+sbsize+sbbd,0)
        glVertex3f(x+sbbd,y+sbsize+sbbd,0)
        glEnd()

        bg=self['bg']
        dc=(bg[0]-.2,bg[1]-.2,bg[2]-.2)
        mc=(bg[0]+.1,bg[1]+.1,bg[2]+.1)
        lc=(bg[0]+.3,bg[1]+.3,bg[2]+.3)
        colors=[dc,mc,lc]
        if (self['sticky']):
            colors.reverse()
        glBegin(GL_LINES)
        glColor3f(colors[0][0],colors[0][1],colors[0][2])
        glVertex3f(x,y,0)
        glColor3f(colors[1][0],colors[1][1],colors[1][2])
        glVertex3f(x+sbbd+sbsize,y,0)
        glVertex3f(x+sbbd+sbsize,y,0)
        glColor3f(colors[2][0],colors[2][1],colors[2][2])
        glVertex3f(x+sbbd+sbsize,y+2*sbbd+sbsize,0)
        glVertex3f(x+sbbd+sbsize,y+sbbd+sbsize,0)
        glColor3f(colors[1][0],colors[1][1],colors[1][2])
        glVertex3f(x+sbbd,y+sbbd+sbsize,0)
        glVertex3f(x,y+sbbd+sbsize,0)
        glColor3f(colors[0][0],colors[0][1],colors[0][2])
        glVertex3f(x,y,0)
        glEnd()
        
    def Draw(self):
        w,h=self['size']
        bw,bh=8,h
        size = bw/2.
        self.DrawBox(size,bw+size,0,bh,size)
        bd = self['bd']
        self.DrawBox(bw+size+bd,w,0,bh,bd)

        glBegin(GL_LINES)
        glColor3f(.5,.5,.5)
        glVertex3f(8+8+bd,h-bd-17,0)
        glVertex3f(w-bd,h-bd-17,0)
        glColor3f(.4,.4,.4)
        glVertex3f(8+8+bd,h-bd-18,0)
        glVertex3f(w-bd,h-bd-18,0)
        glColor3f(.6,.6,.6)
        glVertex3f(8+8+bd,h-bd-19,0)
        glVertex3f(w-bd,h-bd-19,0)
        glEnd()

        try:
            self.DrawStickyBox()
            pass
        except:
            raise
##         glePolyCylinder([(8+8+bd,h-bd-20,0),(8+8+bd,h-bd-20,0),
##                          (w-bd,h-bd-20,0),(w-bd,h-bd-20,0),],
##                         None,2)
        #self.DrawBorder()
        pass

class TextInfo:
    pass

class Button(Widget,TextInfo):
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options = (('bd',0,None),
                   ('command',None),
                   ('depth',3,self.Reset),
                   ('text','',self.Reset),
                   ('font','9by15',self.Reset),
                   ('padx',8,self.Reset),
                   ('pady',5,self.Reset),
                   )
        self.InitOptions(options,kw)
        w,h = self.GetCurrentTextSize()
        self.SetOption('size',(w,h),False)
    def GetCurrentTextSize(self,withpadding=1):
        dstring = self.ProcessString(self['text'],self['font'])
        tw,th = dstring.GetSize()
        if withpadding:
            tw,th = (tw+2*self['padx']+2*self['depth'],
                     th+2*self['pady']+2*self['depth'],)
        return int(tw),int(th)
    def ResetText(self):
        self.StartLocal()
        bw,bh = self.GetCurrentTextSize()
        w,h = self['size']
        if (w < bw) or (h < bh):
            self['size']=int(bw),int(bh)
            #return
        self.EndLocal()
    def Reset(self):
        self.StartLocal()
        self.ResetText()
        Widget.Reset(self)
        self.EndLocal()
    def OnMouse(self):
        if self.LeftButtonUp() and self.Entered():
            if self['command'] is not None:
                self['command'](self)
    def Draw(self):
        depth=self['depth']
        w,h = self['size']
        #print w,h
        text = self.ProcessString(self['text'],self['font'])
        tw,th = self.GetCurrentTextSize(0)
        x,y=max(self['padx']+depth,w/2-tw/2),self['pady']+depth
        if self.LeftButton():
            self.DrawBox(0,w,0,h,depth,'lowered')
            color=(.80,.80,.80)
            x+=1;y+=1
        else:
            self.DrawBox(0,w,0,h,depth)
            color=(.83,.83,.83)
        dc=list(color)
        for i in range(3):
            dc[i]=color[i]-.2
        self.DrawText(x,y,text,color)
        self.DrawText(x+1,y+1,text,dc)
        
class TextEntry(Widget,TextInfo):
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options=[
            ('textfg',(0.1,0.1,0.1),self.Reset),
            ('textbg',[.9,.9,.9],self.Reset),
            ('text','Tungsten Carbide Drills, boy!',self.Reset),
            ('font','9by15',self.Reset),
            #('font','times24',self.Reset),
            ('innerbd',2,self.Reset),
            ('padx',3,self.Reset),
            ('pady',5,self.Reset),
            ('bd',2,self.Reset),
            ('width',20,self.Reset),
            ('select',None,self.Reset),
            ]
        self.InitOptions(options,kw)
        w,h = self.GetCurrentSize()
        self.SetOption('size',(w,h),False)

    def GetCurrentSize(self):
        dtext = self.ProcessString('Z',self['font'])
        tw,th = dtext.GetSize()
        w,h = (self['width']*tw+2*self['bd']+2*self['innerbd']+2*self['padx'],
               th+2*self['bd']+2*self['innerbd']+2*self['pady'])
        return int(w),int(h)
    def ResetText(self):
        self.StartLocal()
        nw,nh = self.GetCurrentSize()
        w,h = self['size']
        if w!=nw or h!=nh:
            self['size']=int(nw),int(nh)
        self.EndLocal()
    def Reset(self):
        self.StartLocal()
        self.ResetText()
        Widget.Reset(self)
        self.EndLocal()
    __cursor = 0
    def Cursor(self,dx=None,x=None):
        if (dx,x) == (None,None):
            return self.__cursor
        if dx is not None:
            m={'start':0,'end':len(self['text'])}
            if dx in m:
                self.__cursor=m[dx]
                return
            self.__cursor+=dx
            if self.__cursor < 0:
                self.__cursor = 0
            if self.__cursor > len(self['text']):
                self.__cursor = len(self['text'])
        else:
            self.__cursor=x
            
    def Draw(self):
        w,h=self['size']
        bd,ibd = self['bd'],self['innerbd']
        self.DrawBox(0,w,0,h,bd)
        self.DrawBox(bd,w-bd,bd,h-bd,ibd,'lowered')
        bg,fg = self['textbg'],self['textfg']
        glColor3f(bg[0],bg[1],bg[2])
        glBegin(GL_POLYGON)
        glVertex3f(bd+ibd,bd+ibd,0)
        glVertex3f(w-(bd+ibd),bd+ibd,0)
        glVertex3f(w-(bd+ibd),h-(bd+ibd),0)
        glVertex3f(bd+ibd,h-(bd+ibd),0)
        glEnd()

        text = self.ProcessString(self['text'],self['font'])
        # draw the insertion cursor
        x,y = text.Position(self.Cursor())
        tw,th = text.GetSize()
        #print x,y
        glColor3f(fg[0],fg[1],fg[2])
        glBegin(GL_LINES)
        glVertex3f(x+bd+ibd+self['padx'],
                   y+bd+ibd+self['pady']/2.,0.001)
        glVertex3f(x+bd+ibd+self['padx'],
                   y+bd+ibd+self['pady']+th,0.001)
        glEnd()

        # draw the select box
        if self['select'] is not None:
            start,end = self['select']
            if end is not None:
                glColor3f(.4,.4,.4)
                x0,y0 = text.Position(start)
                x1,y1 = text.Position(end)
                glBegin(GL_QUAD_STRIP)
                glVertex3f(x0+bd+ibd+self['padx'],
                           y0+bd+ibd+self['pady']/2.,0.0005)
                glVertex3f(x0+bd+ibd+self['padx'],
                           y0+bd+ibd+self['pady']+th,0.0005)
                glVertex3f(x1+bd+ibd+self['padx'],
                           y1+bd+ibd+self['pady']/2.,0.0005)
                glVertex3f(x1+bd+ibd+self['padx'],
                           y1+bd+ibd+self['pady']+th,0.0005)
                glEnd()

        # draw the text
        glTranslate(0,0,0.0008)
        self.DrawText(bd+ibd+self['padx'],bd+ibd+self['pady'],text,fg)


    def SelectStart(self,index):
        if self['select'] is None:
            self.SetOption('select',[index,None],False)
    def SelectEnd(self,index):
        select = self['select']
        select[1]=index
        #select.sort()
        self.SetOption('select',select,False)
    def KillSelect(self):
        if self['select'] is not None:
            self['select']=None
    def DeleteSelect(self):
        select = self['select']
        if select is not None:
            start,end = select
            if end is not None:
##                 if end >= len(self['text']):
##                     end = len(self['text'])-1
                s=[start,end];s.sort();start,end=s
                self['text']=self['text'][:start]+self['text'][end:]
                #print start
                self.Cursor(x=start)
                self.KillSelect()
                return True
        return False
    def OnMouse(self):
        self.TakeFocus()
        x,y = self.GetMousePosition('left','down')
        dtext = self.ProcessString(self['text'],self['font'])
        index = dtext.Find(x-self['bd']-self['innerbd']-self['padx'])
        self.Cursor(x=index)
        if self.LeftButton():
            self.KillSelect()
            self.SelectStart(index)
    def OnMotion(self):
        x,y = self.GetMousePosition('left','current')
        dtext = self.ProcessString(self['text'],self['font'])
        index = dtext.Find(x-self['bd']-self['innerbd']-self['padx'])
        self.Cursor(x=index)
        self.SelectEnd(index)
        #print self['select']
    def OnKeyboard(self):
        focus = self.GetFocus()
        if focus is not self:
            return
        key,state = self.GetGenerator()
        mods = self.GetModifiers()
        other_keys = ['insert','page_up','page_down']
        for i in range(1,13):
            other_keys.append('F'+str(i))
        if state is 'down':
            if key is 'left':
                self.Cursor(-1)
            elif key is 'right':
                self.Cursor(1)
            elif key in ['up','home']:
                self.Cursor('start')
            elif key in ['down','end']:
                self.Cursor('end')
            elif key is 'escape':
                pass
            elif key is 'backspace':
                if not self.DeleteSelect():
                    cx = self.Cursor()
                    if cx!=0:
                        self['text']=self['text'][:cx-1]+self['text'][cx:]
                        self.Cursor(-1)
            elif key is 'delete':
                if not self.DeleteSelect():
                    cx = self.Cursor()
                    self['text']=self['text'][:cx]+self['text'][cx+1:]
            elif self.ControlIsDown():
                ## XXX Total hack.. haven't seen this before.
                ## Guaranteed that it's different on Windows and
                ## probably different on other *nixes.
                #ctrlkey =  chr(ord(key)+ord('a')-1)
                if key == 'f':
                    self.Cursor(1)
                elif key == 'b':
                    self.Cursor(-1)
                elif (key == 'n') or (key=='e'):
                    self.Cursor('end')
                elif (key == 'p') or (key=='a'):
                    self.Cursor('start')
                elif (key == 'd'):
                    if not self.DeleteSelect():
                        cx = self.Cursor()
                        self['text']=self['text'][:cx]+self['text'][cx+1:]
            elif key in other_keys:
                pass
            else:
                cx = self.Cursor()
                self['text'] = self['text'][:cx]+key+self['text'][cx:]
                self.Cursor(1)
    def OnIdle(self):
        print 1
        
class Canvas3D(Widget,Lighted,Camera,Trackball):
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options = (
            ('size',(600,600),),
            ('bg',[0,0,0,1],),
            ('fov',30,self.Reset),
            ('near',.1,self.Reset),
            ('far',10000,self.Reset),
            ('eye',(0,0,40),self.Reset),
            ('center',(0,0,0),self.Reset),
            ('up',(0,1,0),self.Reset),
            ('blend',1,self.Reset),
            ('lighting',1,self.Reset),
            ('tbbutton','left',),
            )
        self.InitOptions(options,kw)

        self.actors = []
        self.zoom=1
        self.translate=[0,0,0]
    def AddActor(self,actor):
        self.actors.append(actor)
    def Reset(self):
        self.StartLocal()
        self.ResetPosition()
        self.ResetGL()
        self.ResetLighting()
        self.ResetPerspective()
        self.ResetView()
        self.EndLocal()
    def ResetGL(self):
        self.StartLocal()
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK,GL_DIFFUSE)
        glEnable(GL_NORMALIZE)
        glEnable(GL_DEPTH_TEST)
        if(self['blend']):
            glEnable (GL_BLEND)
            glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
##             glEnable (GL_LINE_SMOOTH)			
##             glHint (GL_LINE_SMOOTH_HINT, GL_FASTEST)
##             glEnable (GL_POINT_SMOOTH)
##             glHint (GL_POINT_SMOOTH_HINT, GL_FASTEST) 
##             glPointSize (6.0)
        glShadeModel(GL_SMOOTH)
        self.EndLocal()
    def ResetPerspective(self):
        self.StartLocal()
        w,h=self['size']
        glViewport (0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective( self['fov'], float(w)/h,
                        self['near'], self['far'])
        glMatrixMode(GL_MODELVIEW)
        self.EndLocal()
    def ResetView(self):
        self.StartLocal()
        glMatrixMode(GL_PROJECTION)
        eye,center,up = self['eye'],self['center'],self['up']
        gluLookAt( eye[0], eye[1], eye[2],
                   center[0], center[1], center[2],
                   up[0], up[1], up[2] )
        glMatrixMode(GL_MODELVIEW)
        self.EndLocal()
    def OnMotion(self):
        if self.LeftButton():
            self.TrackballMotion()
        elif self.RightButton():
            oldx,oldy = self.GetMousePosition('right','last')
            x,y = self.GetMousePosition('right','current')
            self.zoom -= .01*(y-oldy)
            if self.zoom<0:
                self.zoom=0
        elif self.MiddleButton():
            oldx,oldy = self.GetMousePosition('middle','last')
            x,y = self.GetMousePosition('middle','current')
            tr = self.translate
            tr[0] += 1.045*(x-oldx)
            tr[1] += 1.045*(oldy-y)
    def Draw(self):
        tr = self.translate
        glTranslate(tr[0],tr[1],tr[2])
        self.TrackballDraw()
        glScalef(self.zoom, self.zoom, self.zoom);
        for a in self.actors:
            a.Draw()

class Canvas2D(Widget):
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options = (
            ('size',(600,600),),
            ('bg',[0,0,0,1],),
            ('blend',1,self.Reset),
            ('bbox',[0,600,600,0],self.Reset),
            ('pointsize',6,self.Reset),
            ('zoom',1,),
            ('zoommode',False,),
            )
        self.InitOptions(options,kw)

        self.actors = []
        self.translate=[0,0,0]
    def Reset(self):
        self.StartLocal()
        self.ResetPosition()
        self.ResetGL()
        self.ResetPerspective()
        self.ResetView()
        self.EndLocal()
    def ResetGL(self):
        self.StartLocal()
        glEnable(GL_NORMALIZE)
        if(self['blend']):
            glEnable (GL_BLEND)
            glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable (GL_LINE_SMOOTH)			
            glHint (GL_LINE_SMOOTH_HINT, GL_FASTEST)
            glEnable (GL_POINT_SMOOTH)
            glHint (GL_POINT_SMOOTH_HINT, GL_FASTEST) 
            glPointSize (self['pointsize'])
        self.EndLocal()
    def ResetPerspective(self):
        self.StartLocal()
        w,h=self['size']
        left,right,bottom,top = self['bbox']
        glViewport (0, 0, w, h)
        #glViewport (0, 0, abs(left-right), abs(top-bottom))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        #print left,right,bottom,top
        gluOrtho2D(
            left,right,bottom,top,
            )
        glMatrixMode(GL_MODELVIEW)
        self.EndLocal()
    def ResetView(self):
        self.StartLocal()
        glMatrixMode(GL_PROJECTION)
        glMatrixMode(GL_MODELVIEW)
        self.EndLocal()
    def DoTranslate(self):
        # XXXX Fix
        oldx,oldy = self.GetMousePosition('middle','last')
        x,y = self.GetMousePosition('middle','current')
        tr = self.translate
        tr[0] += 1.045*(x-oldx)
        tr[1] += 1.045*(oldy-y)
        self.SetOption('left',self['left']+tr[0],False)
        self.SetOption('right',self['right']+tr[0],False)
        self.SetOption('top',self['top']+tr[1],False)
        self.SetOption('bottom',self['bottom']+tr[1],False)
        self.ResetPerspective()
    def SetBoundingBox(self,bbox):
        #print 'SetBoundingBox',bbox
        self.SetOption('bbox',[bbox[0][0],bbox[0][1],bbox[1][1],bbox[1][0]],
                       call= (self.glutInitialized()))
    def ScreenToWorld(self,point):
        x,y = point
        w,h = self['size']
        left,right,bottom,top = self['bbox']
        x,y = float(x)/w, float(y)/h
        x *= right-left; y *= bottom-top
        x += left; y += top
        return x,y
    def GetMousePositionWorld(self,**kw):
        x,y = self.GetMousePosition(**kw)
        return self.ScreenToWorld((x,y))

    __zw_start = None
    __zw_end = None
    __zoom_states = None
    def SetZoomWindowEnd(self,end):
        if end is not None: end = list(end)
        self.__zw_end = end
    def SetZoomWindowStart(self,start):
        if start is not None: start = list(start)
        self.__zw_start = start
    def ZoomWindow(self):
        return self.__zw_start,self.__zw_end
    def DrawZoomWindow(self):
        if self['zoommode']:
            start,end = self.ZoomWindow()
            if (start,end) != (None,None):
                set_color('black')
                start = self.ScreenToWorld(start)
                end = self.ScreenToWorld(end)
                front,back = glGetIntegerv(GL_POLYGON_MODE)
                glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
                glRectf(start[0],start[1],
                        end[0],end[1],)
                glPolygonMode(GL_FRONT,front)
                glPolygonMode(GL_BACK,back)
    def __init_zoom_states(self):
        if self.__zoom_states is None:
            bbox = self['bbox']
            bbox = [[bbox[0],bbox[1]],[bbox[3],bbox[2]]]
            self.__zoom_states = [bbox]
        return self.__zoom_states
    def PushZoomState(self,bbox):
        zs = self.__init_zoom_states()
        zs.append(bbox)
        self.SetBoundingBox(bbox)
    def PopZoomState(self):
        zs = self.__init_zoom_states()
        if len(zs)>1:
            bbox = zs.pop()
            self.SetBoundingBox(zs[-1])
            return bbox
    def StartZoomWindow(self):
        start,end =  self.ZoomWindow()
        if start is None:
            pos = self.GetMousePosition()
            print 'Start Zoom window',pos
            self.SetZoomWindowStart(pos)
            self.SetZoomWindowEnd(pos)
    def UpdateZoomWindow(self):
        pos = self.GetMousePosition('left','current')
        print 'Update Zoom window',pos
        self.SetZoomWindowEnd(pos)
    def EndZoomWindow(self):
        start,end = self.ZoomWindow()
        print 'endzoom',start,end
        end = self.GetMousePosition('left','current')
        bbox = [[min(start[0],end[0]),max(start[0],end[0])],
                [min(start[1],end[1]),max(start[1],end[1])],]
        print 'End Zoom window',bbox
        bleft = self.ScreenToWorld((bbox[0][0],bbox[1][0]))
        tright = self.ScreenToWorld((bbox[0][1],bbox[1][1]))
        bbox = [ [bleft[0],tright[0]], [bleft[1],tright[1]] ]
        self.PushZoomState(bbox)
        self.SetZoomWindowStart(None)
        self.SetZoomWindowEnd(None)
        self['zoommode'] = False
    def ZoomWindowMouseDecorator(self):
        if self['zoommode']:
            if self.LeftButton():
                self.StartZoomWindow()
            if self.LeftButtonUp():
                self.EndZoomWindow()
    def ZoomWindowMotionDecorator(self):
        if self['zoommode']:
            if self.LeftButton():
                self.UpdateZoomWindow()

    def Draw(self):
        #tr = self.translate
        #glTranslate(tr[0],tr[1],tr[2])
        #glScalef(self['zoom'], self['zoom'], self['zoom']);
        self.DrawZoomWindow()
        for actor in self.actors:
            if type(actor) in (type([]),type(())):
                for a in actor:
                    a.Draw()
            else:
                actor.Draw()

class Selector(Widget):
    def __init__(self,parent=None,**kw):
        Widget.__init__(self,parent,**kw)
        options = [
            ['w',100],
            ['h',200],
            ('bg',[0.1,0.1,0.1,1]),
            ('button','left'),
            ]
        self.InitOptions(options,kw)

        self.select_items = []
    def GetSelected(self):
        for item in self.select_items:
            if item.Selected():
                return item
    def AddItem(self,item):
        si=self.select_items
        self.select_items.append(item)
        item.AddSubItems(self.select_items)
        #self.SelectItem(len(si)-1)
    def SelectItem(self,index):
        for i,item in enumerate(self.select_items):
            if i != index:
                item.Select(0)
            else:
                item.Select(1)
    def DeselectItem(self,index):
        self.select_items[index].Select(0)
    def OnMouse(self):
        up = self.MouseUp()
        if ('left' in up) or ('right' in up):
            w,h = self['size']
            x,y = self.GetMousePosition(self['button'],'up')
            for i,(section,item) in enumerate(self.pixel_sections):
                #print y,i,section,item
                if y>=h-section:
                    if self.ButtonIsUp('left'):
                        self.SelectItem(i)
                    elif self.ButtonIsUp('right'):
                        self.DeselectItem(i)
                    break
            self.GlobalUpdate()
    def Draw(self):
        nitems = len(self.select_items)
        self.pixel_sections = []
        if nitems:
            w,h = self['size']
            size = h/float(nitems)
            for i,item in enumerate(self.select_items):
                #t = i/float(nitems-1)
                section = (i+1)*size
                self.pixel_sections.append([section,item])
                p0 = (0,section,0)
                p1 = (w,section,0)
                glePolyCylinder([p0,p0,p1,p1],None,bd)
                if item.Selected():
                    glNormal(0,0,1)
                    glBegin(GL_POLYGON)
                    glVertex3f(0,i*size,0)
                    glVertex3f(w,i*size,0)
                    glVertex3f(p1[0],p1[1],p1[2])
                    glVertex3f(p0[0],p0[1],p0[2])
                    glEnd()

if __name__=='__main__':
    class test:
        wire=0
        def quit(self,button=None):
            sys.exit()
        def wireframe(self,button):
            self.wire = not self.wire
        def Draw(self):
            if self.wire:
                glutWireTeapot(5)
            else:
                glutSolidTeapot(5)
    t = test()
        
    c = Canvas3D(lighting=1)
    c.RegisterGlobalKey('q',t.quit,'control')
    c.actors.append(t)
    s = Shutter(c,pos=(30,200),size=(500,500))
    b = Button(s,text='Quit',command=t.quit)
    b2 = Button(s,text='Wireframe',command=t.wireframe)
    b3 = Button(s,text='Blah')
    te = TextEntry(s)
    #b4 = Button(s,text='Toodles Poodles')
    b5 = Button(s,text='lfksdj')
    b6 = Button(s,text='Toodle')
    s.SetGeometry([
        [b,b2,b3],
        [te,b5,b6],#,b4],
        ])
    #c.XML()
    c.Run()
