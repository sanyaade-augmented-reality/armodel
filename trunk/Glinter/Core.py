import os,sys

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLE import *
from OpenGL.GLUT import *

import xml.etree.ElementTree as etree
import pickle,pprint,time,code
from trackball import *

from Glinter.Colors import * # MATERIALS, COLORS

from Glinter.Option import *

prompt = compile("""
try:
    _prompt
    _recursion = 1
except:
    _recursion = 0
if not _recursion:
    from traceback import print_exc as print_exc
    from traceback import extract_stack
    _prompt = {'print_exc':print_exc, 'inp':'','inp2':'','co':''}
    _a_es, _b_es, _c_es, _d_es = extract_stack()[-2]
    if _c_es == '?':
        _c_es = '__main__'
    else:
        _c_es += '()' 
    print '\\nprompt in %s at %s:%s  -  continue with CTRL-D' % (_c_es, _a_es, _b_es)
    del _a_es, _b_es, _c_es, _d_es, _recursion, extract_stack, print_exc
    while 1:
        try:
            _prompt['inp']=raw_input('>>> ')
            if not _prompt['inp']:
                continue
            if _prompt['inp'][-1] == chr(4): 
                break
            exec compile(_prompt['inp'],'<prompt>','single')
        except EOFError:
            print
            break
        except SyntaxError:
            while 1:
                _prompt['inp']+=chr(10)
                try:
                    _prompt['inp2']=raw_input('... ')
                    if _prompt['inp2']:
                        if _prompt['inp2'][-1] == chr(4): 
                            print
                            break
                        _prompt['inp']=_prompt['inp']+_prompt['inp2']
                    _prompt['co']=compile(_prompt['inp'],'<prompt>','exec')
                    if not _prompt['inp2']: 
                        exec _prompt['co']
                        break
                    continue
                except EOFError:
                    print
                    break
                except:
                    if _prompt['inp2']: 
                        continue
                    _prompt['print_exc']()
                    break
        except:
            _prompt['print_exc']()
    print '--- continue ----'
    # delete the prompts stuff at the end
    del _prompt
""", '<prompt>', 'exec')

######################################################
#  Helper classes
######################################################
# 
# These are helper classes designed to encapsulate certain
#  OpenGL concepts. Hopefully, they will make the 3D design
#  process a litle more friendly.
#

# Filip Salomonsson's excellent modification of Fredrick Lundt's
#  pretty printing code for his ElementTree object
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        for e in elem:
            indent(e, level+1)
            if not e.tail or not e.tail.strip():
                e.tail = i + "  "
        if not e.tail or not e.tail.strip():
            e.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# Font Info
FONTS = {
    '8by13':(GLUT_BITMAP_8_BY_13,13),
    '9by15':(GLUT_BITMAP_9_BY_15,15),
    'Times10':(GLUT_BITMAP_TIMES_ROMAN_10,10),
    'Times24':(GLUT_BITMAP_TIMES_ROMAN_24,24),
    'Helvetica10':(GLUT_BITMAP_HELVETICA_10,10),
    'Helvetica12':(GLUT_BITMAP_HELVETICA_12,12),
    'Helvetica18':(GLUT_BITMAP_HELVETICA_18,18),
    'times10':(GLUT_BITMAP_TIMES_ROMAN_10,10),
    'times24':(GLUT_BITMAP_TIMES_ROMAN_24,24),
    'helvetica10':(GLUT_BITMAP_HELVETICA_10,10),
    'helvetica12':(GLUT_BITMAP_HELVETICA_12,12),
    'helvetica18':(GLUT_BITMAP_HELVETICA_18,18),
    }

def set_color(name):
    c = name
    if type(name) is type(''):
        c = COLORS[name]
    glColor3f(c[0],c[1],c[2])
        
def get_text_bbox(string,font=None,glutfont=None):
    w,h=0.,0.
    if font is None:
        font = glutfont
    else:
        font = FONTS[font]
    for c in string:
        w += glutBitmapWidth(font[0],ord(c))
    h = font[1]
    return w,h

class DrawableString:
    def __init__(self,data,font):
        self.data = data
        self.font = FONTS[font]
        self.ProcessPositions()
    def __getitem__(self,index):
        return self.data[index]
    def __len__(self):
        return len(self.data)
    def Add(self,index,text):
        self.data = self.data[:index]+text+self.data[index:]
        self.ProcessPositions()
    def DeleteBack(self,index,num=1):
        if index<=0:
            return
        self.data = self.data[:index-num]+self.data[index:]
        self.ProcessPositions()
    def DeleteForward(self,index,num=1):
        self.data = self.data[:index]+self.data[index+num:]
        self.ProcessPositions()
    def DeleteSection(self,start,end):
        self.data = self.data[:start]+self.data[end:]
        self.ProcessPositions()
    def ProcessPositions(self):
        p = self.positions = []
        csize = self.widths = []
        data,font = self.data,self.font
        x,y = 0.,0.
        for c in data:
            w,h = get_text_bbox(c,glutfont=font)
            p.append([x,y])
            csize.append([w,h])
            x+=w
        self.w,self.h = get_text_bbox(data,
                                      glutfont=font)
    def Extents(self):
        x,y,w,h = 0,0,0,0
        if self.positions and self.widths:
            x,y = self.positions[-1]
            w,h = self.widths[-1]
        return x+w,y+h
    def GetSize(self):
        return self.w,self.h
    def SetFont(self,font):
        self.font = FONTS[font]
        self.ProcessPositions()
    def GetSubstringWidth(self,start,end):
        p = self.positions
        return p[end]-p[start]
    def Find(self,x):
        if not self.data:
            return self.Position(0)
        #print 
        for i,(px,py) in enumerate(self.positions):
            char = self.data[i]
            w,h=get_text_bbox(char,glutfont=self.font)
            #print 'x: ',x,'i: ',i,'px: ',px,'w,h: ',(w,h),'c: ',px+w/2.
            if x<=px+w/2.:
                return i
        if x>px+w/2.:
            return len(self.positions)
            
    def Position(self,index):
        if not self.data:
            return 0,0
        if index == len(self.data):
            px,py=self.positions[-1]
            w,h=self.widths[-1]
            return px+w,py
        else:
            return self.positions[index]
        
class Light:
    def __init__(self,light_number,position=[0.2,0.2,100,1],
                 ambient=[0,0,0,1],diffuse=[.8,.8,.8,1],
                 specular=[.8,.8,.8,1]):
        self.on = 0
        self.light_number = light_number
        self.position = position
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        
        self.type_map = {0:self.ambient,
                         1:self.diffuse,
                         2:self.specular}
    def TurnOn(self,on=True):
        if self.on != on:
            self.on = on
            self.Reset()
    def IsOn(self):
        return self.on
    def Reset(self):
        if self.on:
            if not glIsEnabled(self.light_number):
                glEnable(self.light_number)
        else:
            return
        glLightfv(self.light_number, GL_POSITION,
                 self.position)
        #print 'In Light.Reset',self.position
        glLightfv(self.light_number, GL_AMBIENT,
                 self.ambient)
        glLightfv(self.light_number, GL_DIFFUSE,
                 self.diffuse)
        glLightfv(self.light_number, GL_SPECULAR,
                 self.specular)
        #print 'lighting reset'

    def SetColor(self,color,which=0):
        self.type_map[which][0] = color[0]
        self.type_map[which][1] = color[1]
        self.type_map[which][2] = color[2]
    def Move(self,pnt):
        for i in range(3):
            self.position[i] = pnt[i]

class LightRack:
    GLLIGHTS = [GL_LIGHT0,GL_LIGHT1,GL_LIGHT2,GL_LIGHT3,
                GL_LIGHT4,GL_LIGHT5,GL_LIGHT6,GL_LIGHT7]

    def __init__(self,on=True):
        glDisable(GL_LIGHT0)
        self.on = on
        self.lights = []
        for i in range(8):
            self.lights.append(Light(self.GLLIGHTS[i]))
    def TurnOn(self,on=True):
        self.on = on
        self.Reset()
    def TurnOff(self):
        self.on = False
        self.Reset()
    def TurnOnLight(self,index=0):
        self.lights[index].TurnOn()
    def TurnOffLight(self,index=0):
        self.lights[index].TurnOff()
    def IsOn(self,index):
        return self.lights[index].IsOn()
    def Reset(self):
        if self.on:
            if not glIsEnabled(GL_LIGHTING):
                glEnable(GL_LIGHTING)
            self.lights[0].TurnOn()
        else:
            glDisable(GL_LIGHTING)
        for light in self.lights:
            light.Reset()
    def SetLightColor(self,index,color,which=0):
        self.lights[index].SetColor(color,which)
        self.lights[index].Reset()
    def MoveLight(self,index,pnt):
        self.lights[index].Move(pnt)
        self.lights[index].Reset()


######################################################
#  Widget Tree class
######################################################

class WidgetTree:
    # Tree hierarchy for widgets. Things to do:
    #  - keep track of parent/child relationships
    #  - (future) output XML document describing current layout
    def __init__(self):
        root = etree.Element('Glinter',version='0.01')
        self.widgets = etree.ElementTree(root)
    def get_name(self,widget):
        #return widget.__class__.__name__+str(id(widget))
        return widget.__class__.__name__
    def XML(self):
        indent(self.widgets.getroot())
        etree.dump(self.widgets)
    def RootWidgets(self):
        cnodes = self.widgets.getroot().getchildren()
        widgets = []
        for n in cnodes:
            widgets.append(n.widget)
        return widgets
    def FindById(self,node,ID):
        for c in node:
            if c.get('id')==str(ID):
                return c
            cnode = self.FindById(c,ID)
            if cnode is not None:
                return cnode
    def AddWidget(self,parent,child):
        root = self.widgets.getroot()
        found = self.FindById(root,id(parent))
        options = child.GetOption()
        c = etree.Element(self.get_name(child),
                          id=str(id(child)),**options)
        c.widget = child
        if found is not None:
            found.append(c)
        else:
            options = {}
            #print 'parent in WidgetTree.AddWidget',parent
            if parent:
                options = parent.GetOption()
                p = etree.Element(self.get_name(parent),
                                  id=str(id(parent)),**options)
                p.widget = parent
                root.append(p)
                p.append(c)
            else:
                root.append(c)
    def get_parent(self,node,child):
        for c in node:
            if c.get('id') == str(id(child)):
                return node
            pnode = self.get_parent(c,child)
            if pnode is not None:
                return pnode
    def GetParent(self,child):
        root = self.widgets.getroot()
        parent = self.get_parent(root,child)
        if parent != root:
            return parent.widget
    def GetChildren(self,parent):
        root = self.widgets.getroot()
        #print 'Parent in GetChildren', parent,self.get_name(parent)
        pnode = self.FindById(root,id(parent))
        if pnode is None:
            exec prompt
            self.XML()
        children = []
        for c in pnode:
            children.append(c.widget)
        return children
    def GetSiblings(self,widget):
        root = self.widgets.getroot()
        pnode = self.GetParent(widget)
        if pnode is None:
            pnode = root
        children = []
        for cnode in pnode:
            children.append(cnode.widget)
        return children
    def GetToplevelWidgets(self):
        root = self.widgets.getroot()
        toplevel = []
        for cnode in root:
            toplevel.append(cnode.widget)
        return toplevel


######################################################
#  Widget mixin classes
######################################################

GLUT_SCROLLUP_BUTTON = 3
GLUT_SCROLLDOWN_BUTTON = 4

class Mouse:
    # Mouse mixin class for keeping track of mouse movements
    #   - Would like to somehow keep track of global
    #     mouse position as well as as much metadata as possible
    #     - **IDEA** use GLUT_WINDOW_X/Y + cumulative position of window
    __button=None
    __generator=None
    __pos = None
    __passive_pos = {'current':None,'last':None}
    __glut_english = {'buttons':{GLUT_LEFT_BUTTON:'left',
                                 GLUT_MIDDLE_BUTTON:'middle',
                                 GLUT_RIGHT_BUTTON:'right',
                                 GLUT_SCROLLUP_BUTTON:'scrollup',
                                 GLUT_SCROLLDOWN_BUTTON:'scrolldown'},
                      'states': {GLUT_DOWN:'down',
                                 GLUT_UP:'up'}}
    def MouseState(self,state):
        self.__init()
        buttons=[]
        for button,state in self.__button.items():
            if state is 'down':
                buttons.append(button)
        return buttons
    def GetLastButton(self):
        return self.__generator
    def MouseDown(self):
        return self.MouseState('down')
    def MouseUp(self):
        return self.MouseState('up')
    def ButtonIsDown(self,button):
        self.__init()
        return self.__button[button] is 'down'
    def ButtonIsUp(self,button):
        self.__init()
        return self.__button[button] is 'up'
    def LeftButton(self):
        return self.ButtonIsDown('left')
    def MiddleButton(self):
        return self.ButtonIsDown('middle')
    def RightButton(self):
        return self.ButtonIsDown('right')
    def LeftButtonUp(self):
        return self.ButtonIsUp('left') and (self.__generator is 'left')
    def MiddleButtonUp(self):
        return self.ButtonIsUp('middle') and (self.__generator is 'middle')
    def RightButtonUp(self):
        return self.ButtonIsUp('right') and (self.__generator is 'right')
    def __init(self):
        if self.__button is None:
            self.__button = {'left':'up',
                             'middle':'up',
                             'right':'up',
                             'scrollup':'up',
                             'scrolldown':'up',
                             }
        if self.__pos is None:
            self.__pos = {'left':{'down':None,'up':None,
                                  'current':None,'last':None},
                          'middle':{'down':None,'up':None,
                                    'current':None,'last':None},
                          'right':{'down':None,'up':None,
                                   'current':None,'last':None},
                          'scrollup':{'down':None,'up':None,
                                      'current':None,'last':None},
                          'scrolldown':{'down':None,'up':None,
                                        'current':None,'last':None},
                          }
    def SetMouse(self,button=None,state=None,x=None,y=None):
        self.__init()
        if button is not None:
            if button is 'passive':
                x,y = x+glutGet(GLUT_WINDOW_X),y+glutGet(GLUT_WINDOW_Y)
                current = Mouse.__passive_pos['current']
                Mouse.__passive_pos['last']=current
                Mouse.__passive_pos['current']=x,y
                #print x,y
            else:
                button = self.__glut_english['buttons'][button]
                state = self.__glut_english['states'][state]
                self.__generator = button
                self.__button[button]=state
                if state is 'down':
                    for state in ['down','current','last']:
                        self.__pos[button][state]=x,y
                    self.__pos[button]['up']=None
                else:
                    self.__pos[button]['up']=x,y
        elif (x,y) is not (None,None):
            buttons = self.MouseDown()
            for button in buttons:
                current = self.__pos[button]['current']
                self.__pos[button]['last']=current
                self.__pos[button]['current']=x,y
    def GetMousePosition(self,button='left',state='down',absolute=False):
        if button is 'passive':
            pos = Mouse.__passive_pos[state]
        else:
            pos = self.__pos[button][state]
        if pos is not None:
            pos = list(pos)
            if absolute:
                x,y = glutGet(GLUT_WINDOW_X),glutGet(GLUT_WINDOW_Y)
                pos[0]+=x
                pos[1]+=y
        return pos

class Keyboard:
    __key=None
    __glut_english = {
        GLUT_KEY_F1:'F1',
        GLUT_KEY_F2:'F2',
        GLUT_KEY_F3:'F3',
        GLUT_KEY_F4:'F4',
        GLUT_KEY_F5:'F5',
        GLUT_KEY_F6:'F6',
        GLUT_KEY_F7:'F7',
        GLUT_KEY_F8:'F8',
        GLUT_KEY_F9:'F9',
        GLUT_KEY_F10:'F10',
        GLUT_KEY_F11:'F11',
        GLUT_KEY_F12:'F12',
        GLUT_KEY_LEFT:'left',
        GLUT_KEY_UP:'up',
        GLUT_KEY_RIGHT:'right',
        GLUT_KEY_DOWN:'down',
        GLUT_KEY_PAGE_UP:'page_up',
        GLUT_KEY_PAGE_DOWN:'page_down',
        GLUT_KEY_HOME:'home',
        GLUT_KEY_END:'end',
        GLUT_KEY_INSERT:'insert',
        '\x08': 'backspace',
        #'\x08': 'bs',
        '\x7f': 'delete',
        #'\x7f': 'del',
        '\x1b': 'escape',
        #'\x1b': 'esc',
        }
    __modifiers = { GLUT_ACTIVE_SHIFT: 'shift',
                    GLUT_ACTIVE_CTRL: 'control',
                    GLUT_ACTIVE_ALT: 'alt',}
    __generator = None
    # Keyboard mixin class for keeping track of mouse movements
    def __init(self):
        if self.__key is None:
            self.__key = {}
    def get_english_keyname(self,key):
        return self.__glut_english.get(key,key)
    def SetKey(self,key=None,state=None,x=None,y=None):
        self.__init()
        key = self.__glut_english.get(key,key)
        if self.ControlIsDown():
            key =  chr(ord(key)+ord('a')-1)
        self.__generator = [key,state]
        #print str(key),state,x,y
        if state is 'down':
            self.__key[key]={'down':(x,y),'up':None}
        else:
            self.__key[key]['up'] = (x,y)
        return key,state,x,y
    def ControlIsDown(self):
        m = glutGetModifiers()
        return m&GLUT_ACTIVE_CTRL
    def AltIsDown(self):
        m = glutGetModifiers()
        return m&GLUT_ACTIVE_ALT
    def ShiftIsDown(self):
        m = glutGetModifiers()
        return m|GLUT_ACTIVE_SHIFT
    def GetModifiers(self):
        modifiers = []
        m = glutGetModifiers()
        for mod in [GLUT_ACTIVE_CTRL,GLUT_ACTIVE_ALT,
                    GLUT_ACTIVE_SHIFT,]:
            if m&mod:
                modifiers.append(self.__modifiers[mod])
        return modifiers
    def GetGenerator(self):
        return self.__generator
    def GetKey(self,key):
        return self.__key.get(key)

class Trackball:
    # Trackball mixin class for doing trackball rotations 
    #   on a Canvas3D widget
    __quaternion = None
    def __init(self):
        if not self.__quaternion:
            self.__quaternion = [0,0,0,0]
            trackball(self.__quaternion,0,0,0,0)
    def TrackballMotion(self):
        self.__init()
        lx,ly = self.GetMousePosition(self['tbbutton'],'last')
        x,y = self.GetMousePosition(self['tbbutton'],'current')
        quat = [0,0,0,0]
        w,h = self['size']
        trackball(quat,(2.0 * lx - w)/w,
                  (h - 2.0*ly)/h,
                  (2.0*x - w)/w,
                  (h - 2.0*y)/h)
        self.__quaternion = add_quats(quat,self.__quaternion)
    def TrackballDraw(self):
        self.__init()
        m = build_rotmatrix(self.__quaternion)
        glMultMatrixf(m)
    def GetTrackballMatrix(self):
        m = build_rotmatrix(self.__quaternion)
        return m
    def GetTrackballQuaternion(self):
        return self.__quaternion

class Camera:
    # Camera mixin class for handling 3D camera issues
    __eye = (0,0,40)
    __up = (0,1,0)
    __center = (0,0,0)
    def GetEye(self):
        return list(self.__eye)
    def SetEye(self,eye):
        self.__eye = tuple(eye)
    def GetUp(self):
        return list(self.__up)
    def SetUp(self,up):
        self.__up = tuple(up)
    def GetCenter(self):
        return list(self.__center)
    def SetCenter(self,center):
        self.__center = tuple(center)
    def GetCameraInfo(self):
        return self.GetEye(),self.GetCenter(),self.GetUp()
    def GetLineOfSight(self):
        eye,center,up = self.GetCameraInfo()
        return [eye[0]-center[0],eye[1]-center[1],eye[2]-center[2]]

class Lighted:
    # Lighting mixin class. Handles the high-level
    #   lighting details
    __lights=None
    def LightRack(self):
        if self.__lights is None:
            self.__lights=LightRack()
        return self.__lights
    def ResetLighting(self):
        rack = self.LightRack()
        if self['lighting']:
            rack.TurnOn()
        else:
            rack.TurnOff()
        rack.Reset()

class Callback:
    def InitCallbacks(self):
        glutDisplayFunc(self.Display)
        glutEntryFunc(self.Entry)
        glutIdleFunc(self.Idle)
        keyfunc=lambda key,x,y,s=self: s.Keyboard(key,'down',x,y)
        glutKeyboardFunc(keyfunc)
        keyfunc=lambda key,x,y,s=self: s.Keyboard(key,'up',x,y)
        glutKeyboardUpFunc(keyfunc)
        keyfunc=lambda key,x,y,s=self: s.Keyboard(key,'down',x,y)
        glutSpecialFunc(keyfunc)
        keyfunc=lambda key,x,y,s=self: s.Keyboard(key,'up',x,y)
        glutSpecialUpFunc(keyfunc)
        glutMenuStatusFunc(self.MenuStatus)
        glutMotionFunc(self.Motion)
        glutPassiveMotionFunc(self.PassiveMotion)
        glutMouseFunc(self.Mouse)
        glutReshapeFunc(self.Reshape)
        #glutTimerFunc(self.Timer)
        glutVisibilityFunc(self.Visibility)
        glutWindowStatusFunc(self.WindowStatus)
    def Display(self):
        pass
    def Idle(self):
        pass
    def Entry(self,state):
        pass
    def Keyboard(self,key,state,x,y):
        pass
    def MenuStatus(self,status,x,y):
        pass
    def Motion(self,x,y):
        pass
    def PassiveMotion(self,x,y):
        pass
    def Mouse(self,button,state,x,y):
        pass
    def Reshape(self,w,h):
        pass
    def Timer(self,msecs,func,*a):
        pass
    def Visibility(self,state):
        pass
    def WindowStatus(self,state):
        pass

class Geometry:
    __geometry = None
    def GetGeometry(self):
        return self.__geometry
    def ShrinkWrap(self):
        geom = self.GetGeometry()
        size = geom['bbox'][1]
        size[0]+=self['bd']
        size[1]+=self['bd']
        self.SetOption('size',size,False)
    def __init(self,geometry):
        self.__geometry = {'matrix':[0]*len(geometry),
                           'bbox':[[0,0],[0,0]]}
        geom = self.__geometry['matrix']
        maxcols=0
        for row in geometry:
            if len(row)>maxcols:
                maxcols=len(row)
        for i,row in enumerate(geometry):
            geom[i]=[0]*maxcols
            for j,widget in enumerate(row):
                geom[i][j]={'id':id(widget),
                                       'bbox':[[0,0],[0,0]]}
    def TopLeft(self):
        t,l = self['bd'],self['bd']
        return t,l
    def __get_widget(self,item):
        widget = item
        if type(item) is type({}):
            widget = item['widget']
        return widget
    def SetGeometry(self,geometry):
        self.__init(geometry)
        maxcols=0
        maxrowheight = [0]*len(geometry)
        for i,row in enumerate(geometry):
            numcols=len(row)
            if numcols>maxcols:
                maxcols=numcols
            for item in row:
                widget = self.__get_widget(item)
                w,h=widget['size']
                if h>maxrowheight[i]:
                    maxrowheight[i]=h
        maxcolwidth = [0]*maxcols
        for i,row in enumerate(geometry):
            for j,item in enumerate(row):
                widget=self.__get_widget(item)
                w,h=widget['size']
                if w>maxcolwidth[j]:
                    maxcolwidth[j]=w
        #print maxrowheight
        #print maxcolwidth
        t,l = self.TopLeft()
        y = t
        maxx,maxy=0,0
        for i,maxh in enumerate(maxrowheight):
            x = l
            for j,maxw in enumerate(maxcolwidth):
                if len(geometry[i])>j:
                    item = geometry[i][j]
                    widget = self.__get_widget(item)
                    widget.SetOption('pos',(x,y),False)
                    w,h = widget['size']
                    if w<maxcolwidth[j]:
                        widget.SetOption('size',(maxcolwidth[j],h),False)
                    w,h = widget['size']
                    self.__geometry['matrix'][i][j]['bbox'][0]=[x,y]
                    self.__geometry['matrix'][i][j]['bbox'][1]=[x+w,y+h]
                    if x+w>maxx:
                        maxx=x+w
                    if y+h>maxy:
                        maxy=y+h
                x += maxcolwidth[j]
            y += maxrowheight[i]
        self.__geometry['bbox'][1]=[maxx,maxy]
        #pprint.pprint( self.__geometry)
        self.ShrinkWrap()
                
class Core(Option,Mouse,Keyboard,Callback):
    # Core mixin class.
    #
    # Handles:
    #   - Interface with WidgetTree
    #   - GLUT initialization
    #   - Window initialization
    #   - Window focus (glutSet/GetWindow)
    #
    # Stores:
    #   - GLUT window information (window id, etc.)
    __tree = WidgetTree()
    __init_called = False
    __window = None
    __key_callbacks = None
    __global_key_callbacks = {}
    __focus = None
    def __set_window(self,window):
        self.__window = window
    def __init_key_callbacks(self):
        if self.__key_callbacks is None:
            self.__key_callbacks = {}
    def __init_only_once(self):
        # Make sure init is only called once, to avoid multiple calls
        #   to glutInit and creation of redundant windows
        if Core.__init_called:
            raise SyntaxError,('Run should only be called once.')
        Core.__init_called=True
    def __init_widgets(self):
        self.__init_only_once()
        root_widgets = Core.__tree.RootWidgets()
        for root in root_widgets:
            root.__init_as_root()
    def __init_as_root(self):
        x,y = self['pos']
        w,h = self['size']
        glutInitWindowPosition(x,y)
        glutInitWindowSize(w,h)
        win = glutCreateWindow(self['title'])
        self.__set_window(win)
        self.InitCallbacks()
        self.Reset()
        children = self.GetChildren()
        for child in children:
            child.__init_as_sub(win)
    def __init_as_sub(self,parent_window):
        x,y = self['pos']
        w,h = self['size']
        win = glutCreateSubWindow(parent_window,x,y,w,h)
        self.__set_window(win)
        self.InitCallbacks()
        self.Reset()
        children = self.GetChildren()
        for child in children:
            child.__init_as_sub(win)
    def glutInitialized(self):
        return Core.__init_called
    def XML(self):
        return Core.__tree.XML()
    def GetParent(self):
        return Core.__tree.GetParent(self)
    def GetChildren(self):
        return Core.__tree.GetChildren(self)
    def GetSiblings(self):
        return Core.__tree.GetSiblings(self)
    def GetToplevelWidgets(self):
        return Core.__tree.GetToplevelWidgets()
    def AddChild(self,child):
        Core.__tree.AddWidget(self,child)
    def AddWidget(self,parent,child):
        Core.__tree.AddWidget(parent,child)
    def SetAsCurrentWindow(self):
        win = self.GetWindow()
        glutSetWindow(win)
    def GetCurrent(self):
        win = glutGetWindow()
        return win

    def TakeFocus(self):
        Core.__focus = self
    def ClearFocus(self):
        Core.__focus = None
    def SetFocus(self,widget):
        Core.__focus = widget
    def GetFocus(self):
        return Core.__focus

    __current = None
    def StartLocal(self):
        if self.__current is None:
            self.__current = []
        win = self.GetCurrent()
        self.__current.append(win)
        self.SetAsCurrentWindow()
    def EndLocal(self):
        win = self.__current.pop()
        glutSetWindow(win)
    def GlobalUpdate(self):
        toplevel = self.GetToplevelWidgets()
        for widget in toplevel:
            widget.Update(children=True)
    def Update(self,children=False):
        self.StartLocal()
        glutPostRedisplay()
        self.EndLocal()
        if children:
            for child in self.GetChildren():
                child.Update(children)
    def GetWindow(self):
        if self.__window is None:
            raise SyntaxError, 'Window has not been created yet'
        return self.__window
    def glutInit(self):
        # GLUT initialization function. Can be overridden, as
        #   there might be some extra functionality needed by the
        #   user.
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_ALPHA | GLUT_DEPTH)

        ## This is really annoying. X11 won't let you turn off key
        ##  repeats on a per-window basis, and GLUT steals the
        ##  process from python, so you can't make changes after
        ##  termination. Grrrr....
        ##
        #self.repeat=glutDeviceGet(GLUT_DEVICE_IGNORE_KEY_REPEAT)
        #if self.repeat in (GLUT_KEY_REPEAT_ON,GLUT_KEY_REPEAT_DEFAULT):
        #    glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF)
        glutIgnoreKeyRepeat(1)
    def Run(self):
        # Initialise all windows and start GLUT's mainloop
        self.glutInit()
        #print 'lskdfj'
        self.__init_widgets()
        glutMainLoop()

    ########################
    # Callback overides
    def Display(self):
        self.OnDisplay()
    def Idle(self):
        self.OnIdle()
    __entered=False
    def Entry(self,state):
        #print glutGet(GLUT_WINDOW_X),glutGet(GLUT_WINDOW_Y)
        self.__entered=state
        self.OnEntry()
        self.Update()
    def Entered(self):
        return self.__entered == GLUT_ENTERED
    def Left(self):
        return self.__entered == GLUT_LEFT
    def Keyboard(self,key,state,x,y):
        focus = self.GetFocus()
        if focus is not None:
            self = focus
            #print self
        key,state,x,y=self.SetKey(key,state,x,y)
        self.OnKeyboard()
        if state is 'down':
            self.CheckKeys(key)
            self.CheckGlobalKeys(key)
        self.GlobalUpdate()
    def CheckKeys(self,key):
        self.__init_key_callbacks()
        modifiers = self.GetModifiers()
        if key in self.__key_callbacks:
            func,mods,args,kw = self.__key_callbacks[key]
            #print mods,modifiers
            if mods == modifiers:
                func(*args,**kw)
    def CheckGlobalKeys(self,key):
        modifiers = self.GetModifiers()
        if key in Core.__global_key_callbacks:
            func,mods,args,kw = Core.__global_key_callbacks[key]
            #print mods,modifiers
            if mods == modifiers:
                func(*args,**kw)
    def RegisterKey(self,key,func,modifiers=[],*args,**kw):
        self.__init_key_callbacks()
        if type(modifiers) is type(''):
            modifiers = [modifiers]
        self.__key_callbacks[key] = [func,modifiers,
                                     args,kw]
    def RegisterGlobalKey(self,key,func,modifiers=[],*args,**kw):
        if type(modifiers) is type(''):
            modifiers = [modifiers]
        Core.__global_key_callbacks[key] = [func,modifiers,
                                            args,kw]
    def MenuStatus(self,status,x,y):
        self.OnMenuStatus()

    #############################################
    __decorators = None
    def __init_decorators(self):
        if self.__decorators is None:
            self.__decorators = {'callback': {'mouse':{}, 'motion':{}, 'passive_motion':{},
                                              'reshape':{}, 'entry':{}, 'keyboard':{},
                                              'visibility':{}},
                                 'draw': {},
                                 }
    def GetDecorators(self):
        return self.__decorators
    def RegisterCallbackDecorator(self,type,name,func):
        self.__init_decorators()
        decs = self.__decorators['callback'][type]
        if not decs:
            decs['order'] = [name]
        else:
            if name not in decs['order']:
                decs['order'].append(name)
        decs[name] = func
    def RegisterDrawDecorator(self,name,func):
        self.__init_decorators()
        self.__decorators['draw']['order'].append(name)
        self.__decorators['draw'][name] = func
    def CallCallbackDecorators(self,type):
        decorators = self.__decorators['callback'][type]
        for name in decorators:
            decorators[name]()
    #############################################
            
    def Mouse(self,button,state,x,y):
        #########################################
        # need to watch for scroll button actions
        if ((button in (GLUT_SCROLLDOWN_BUTTON,
                        GLUT_SCROLLUP_BUTTON)) and
            state == GLUT_DOWN): return
        #########################################
        self.SetMouse(button,state,x,y)
        #self.CallDecorators('mouse')
        self.OnMouse()
        self.GlobalUpdate()
    def Motion(self,x,y):
        self.SetMouse(x=x,y=y)
        #self.CallDecorators('')
        self.OnMotion()
        self.Update()
    def PassiveMotion(self,x,y):
        self.SetMouse('passive',x=x,y=y)
        self.OnPassiveMotion()
    def Reshape(self,w,h):
        self['size']=w,h
        self.OnReshape()
        self.GlobalUpdate()
    def Timer(self,msecs,func,*a):
        self.OnTimer()
    def Visibility(self,state):
        self.OnVisibility()
    def WindowStatus(self,state):
        self.OnWindowStatus()
    def OnDisplay(self):
        pass
    def OnIdle(self):
        pass
    def OnEntry(self):
        pass
    def OnKeyboard(self):
        pass
    def OnMenuStatus(self):
        pass
    def OnMouse(self):
        pass
    def OnMotion(self):
        pass
    def OnPassiveMotion(self):
        pass
    def OnReshape(self):
        pass
    def OnTimer(self):
        pass
    def OnVisibility(self):
        pass
    def OnWindowStatus(self):
        pass
        


######################################################
#  Actor mixin classes
######################################################

class Selectable:
    __selected = False
    def Select(self,state=True,quiet=False):
        self.__selected = state
        if not quiet:
            if state:
                self.OnSelect()
            else:
                self.OnDeselect()
    def OnSelect(self):
        pass
    def OnDeselect(self):
        pass
    def AddSubItems(self,items):
        pass
    def Selected(self):
        return self.__selected

class Rotatable:
    # Mixin class for keeping track of rotations on individual
    #   actors in a 3D scene
    __quaternion = None
    def __init(self):
        self.__quaternion = [0,0,0,0]
        trackball(self.__quaternion,0,0,0,0)
    def Rotate(self,quat):
        if not self.__quaternion:
            self.__init()

class Translatable:
    # Mixin class for keeping track of translations on
    #   individual actors in a 3D scene
    __translation = None
    def __init(self):
        if self.__translation is None:
            self.__translation = [0,0,0]
    def Translate(self,translation):
        self.__init()
        for i in range(3):
            self.__translation[i]+=translation[i]
    def GetTranslation(self):
        self.__init()
        return self.__translation

class Actor(Option,Translatable,
            Rotatable,Selectable):
    def Draw(self):
        pass

