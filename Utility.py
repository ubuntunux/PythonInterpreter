#---------------------#
# custom log
#---------------------#
import sys
file = open("kivy_log.txt","w")
file.write("")
file.close()
class myLogger:
  def write(self, data):
    file = open("kivy_log.txt","a")
    file.write(data)
    file.close()
sys.stderr = myLogger()

#---------------------#
# Import kivy
#---------------------#
import kivy
from kivy import metrics
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.extras.highlight import KivyLexer
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle, Point, GraphicException, Line, Quad, Ellipse, Fbo, RenderContext
from kivy.graphics.instructions import Instruction
from kivy.graphics.opengl import glLineWidth
from kivy.logger import Logger
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, SwapTransition, WipeTransition, FadeTransition
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.codeinput import CodeInput
from kivy.uix.dropdown import DropDown
from kivy.uix.filechooser import FileChooserListView, FileChooserIconView
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeView, TreeViewLabel
from kivy.uix.widget import Widget
from kivy.vector import Vector

from toast import toast

#---------------------#
# Import android library
#---------------------#
from kivy import platform

global isAndroid
isAndroid = False

if platform() == 'android':
  global isAndroid
  isAndroid = True
  
try:
  import android
  from jnius import autoclass
  AndroidString = autoclass('java.lang.String')
  PythonActivity = autoclass('org.renpy.android.PythonActivity')
  VER = autoclass('android.os.Build$VERSION')
except:
  autoclass = None

#---------------------#
# Import standard library
#---------------------#
import time
from cmath import polar, rect
from copy import copy, deepcopy
from glob import glob
import math
from math import cos,sin,pi,sqrt,atan,atan2
import os
from os import path
import random
import threading
import traceback 
from cStringIO import StringIO

#---------------------#
# loading post process
#---------------------#
def loading_postprocess():
  global gMyRoot, gDebug, log, Print
  gMyRoot = MyRoot.instance()
  gDebug = DebugPrint.instance()
  log = gDebug.log
  Print = gDebug.Print
  
  # pyinterpreter
  from PyInterpreter import PyInterpreter
  global gPyInterpreter
  gPyInterpreter = PyInterpreter.instance()
  
#---------------------#
# Global variable
#---------------------#
W = float(Window.size[0])
H = float(Window.size[1])
WW = (W,W)
HH = (H,H)
WH = (W, H)
WRatio = H/W
HRatio = W/H
cX = W * 0.5
cY = H * 0.5
cXY = (W * 0.5, H * 0.5)

def WRect(size):
  return mul(WH, (size, size*HRatio))

def HRect(size):
  return mul(WH, (size*WRatio, size))

global fAccTime
fUpdateTime = 1.0 / 60.0
fFrameTime = 1.0
fAccTime = 0.0
bButtonLock = False

def add(A, B):
  if type(B) != tuple and type(B) != list:
    return [i+B for i in A]
  else:
    return [A[i]+B[i] for i in range(len(A))]

def sub(A, B):
  if type(B) != tuple and type(B) != list:
    return [i-B for i in A]
  else:
    return [A[i]-B[i] for i in range(len(A))]

def mul(A, B):
  if type(B) != tuple and type(B) != list:
    return [i*B for i in A]
  else:
    return [A[i]*B[i] for i in range(len(A))]

def div(A, B):
  if type(B) != tuple and type(B) != list:
    return [i/B for i in A]
  else:
    return [A[i]/B[i] for i in range(len(A))]

def dot(A, B):
 return sum(mul(A, B))
 
def getDist(A, B = None):
  temp = sub(A, B) if B else A
  return sqrt(sum([i*i for i in temp]))
  
def normalize(A, dist = None):
  if dist == None:
    dist = getDist(A)
  return div(A, dist) if dist > 0.0 else mul(A, 0.0)

def getFrameTime():
  return fFrameTime
  
def getAccTime():
  return fAccTime

def getHint(ratioX, ratioY, size = WH):
  return (size[0] * ratioX, size[1] * ratioY)
  
def getCenter(pos, size):
  return (pos[0] + size[0]*.5, pos[1] + size[1]*.5)

def getLT(center, size):
  return (center_pos[0]-size[0]/2.0, center_pos[1]+size[1]/2.0)

def getRT(center, size):
  return (center_pos[0]+size[0]/2.0, center_pos[1]+size[1]/2.0)

def getLB(center, size):
  return (center_pos[0]-size[0]/2.0, center_pos[1]-size[1]/2.0)

def getRB(center, size):
  return (center_pos[0]+size[0]/2.0, center_pos[1]-size[1]/2.0)
#---------------------#
# Utility
#---------------------#
def nRand(min, max):
  return random.randint(min, max)

def fRand(min, max):
  return random.uniform(min, max)

def calcCenterPos(pos, size):
  return (pos[0]+size[0]/2.0, center_pos[1]+size[1]/2.0)
     
def calcPos(center_pos, size):
  return (center_pos[0]-size[0]/2.0, center_pos[1]-size[1]/2.0)

def calcSize(size, ratioX, ratioY):
  return (size[0]*ratioX, size[1]*ratioY)

def getButton(text, center, size):
  widget = Button()
  widget.text = text
  widget.size = getHint( size[0], size[1], WH )
  widget.center = getHint( center[0], center[1], WH )
  return widget

#---------------------#
# use for c style pointer variable
#---------------------#
class Pointer:
  value = None
  
  def __init__(self, value):
    self.set(value)
  
  def set(self, value):
    self.value = value
    
  def get(self):
    return self.value
    
#---------------------#
# CLASS : Singleton
#---------------------#
class Singleton:
  __instance = None
  
  @classmethod
  def getInstance(cls):
    return cls.__instance
    
  @classmethod
  def instance(cls, *args, **kargs):
    cls.__instance = cls(*args, **kargs)
    cls.instance = cls.getInstance
    return cls.__instance

#---------------------#
# CLASS : Var
#---------------------#
class Var:
  def __init__(self, v1=None, v2=None):
    if v1 == None:
      return
      
    self.min = v1
      
    if v2 != None:
      self.v1 = v1
      self.v2 = v2
      self.max = v2
      if type(v1) == list or type(v1) == tuple:
        self.get = self.getRandList
      else:
        self.get = self.getRandScalar
    else:
      self.v1 = v1
      self.max = v1
      if type(v1) == list or type(v1) == tuple:
        self.get = self.getList
      else:
        self.get = self.getScalar
    
  def setValue(self, v1=None, v2=None):
    self.__init__(v1, v2)
    
  def getMin(self):
    return self.min
  
  def getMax(self):
    return self.max

  def get(self):
    pass

  def getList(self):
    return copy(self.v1)

  def getScalar(self):
    return self.v1

  def getRandList(self):
    return [random.uniform(self.v1[i],self.v2[i]) for i in range(len(self.v1))]

  def getRandScalar(self):
    return random.uniform(self.v1, self.v2)

#---------------------#
# CLASS : jobObject
#---------------------#
class jobObject:
  def __init__(self, func, args=(), kargs={}):
    self.func = func
    self.args = args
    self.kargs = kargs
        
  def doJob(self):
    self.func(*self.args, **self.kargs)

#---------------------#
# CLASS : Job
#---------------------#
class Job:  
  def __init__(self, title):
    self.title = title
    self.jobList = []
    self.isFirstUpdate = True
      
  def addJob(self, func, args=(), kargs={}):
    self.jobList.append(jobObject(func, args, kargs))
      
  def update(self): 
    if self.isFirstUpdate:
      # show popup
      gMyRoot.createProgressPopup(self.title, 0)
      self.isFirstUpdate = False
    else:
      # do job
      while self.jobList:
        job = self.jobList.pop(0)
        job.doJob()
      # destroy popup
      gMyRoot.destroyProgressPopup()
       
  def isComplete(self):
    return self.jobList == []
      
#---------------------#
# CLASS : DebugPrint
#---------------------#
class DebugPrint(Widget, Singleton):
  bShow = False
  curLineCount = 0
  staticLineCount = 0
  szString = ""
  szStatic = ""
  szOldString = ""
  bUpdate = False
  bShowFrame = True
  bShowUpdate = False
  checkFrameTime = 0.0
  lastFrameTime = 0.0
  frameCount = 0.0
  btn_width = kivy.metrics.dp(100)
  btn_height = kivy.metrics.dp(30)
  logBuffer = []
  bSaveLog = False

  def __init__(self):
    Widget.__init__(self)
    
  def init(self, bShow):
    self.bShow = bShow
    
    if not bShow:
      return
      
    # toggle btn
    self.btn_layout = BoxLayout(orientation='horizontal', size=(W, self.btn_height), pos=(0, H-self.btn_height))
    self.add_widget(self.btn_layout)
    self.fps = Button(text="Toggle", size_hint_x=1.5)
    self.fps.bind(on_release = self.toggleDebug)
    self.fps.name = "FPS"
    self.btn_layout.add_widget(self.fps)
    
    self.btn_update = Button(text="Show Update", size_hint_x=3)
    self.btn_update.bind(on_release=self.toggleShowUpdate)
    self.btn_layout.add_widget(self.btn_update)
    
    self.btn_clear = Button(text="Clear log", size_hint_x=2)
    self.btn_clear.bind(on_release = self.clearPrint)
    self.btn_layout.add_widget(self.btn_clear)
    
    self.btn_python = Button(text="Run Python", size_hint_x=3)
    self.btn_python.bind(on_release=self.togglePython)
    self.btn_layout.add_widget(self.btn_python)
    
    # label
    self.debugLabel = TextInput(text="", halign='left', valign='top', readonly=True, use_bubble=False, use_handles=False,
      allow_copy=False, multiline=True, background_color=(1,1,1,0), foreground_color=(1,1,1,1), size_hint_y=None)
    self.debugLabel.size = (W, 0)
    self.debugLabel.pos=(0,0)
    self.debugLabel.name = "Print output"
    self.add_widget(self.debugLabel)

    self.toggleDebug()
    
  def refreshDebugLabel(self):
    self.debugLabel.size = (W, self.debugLabel.minimum_height)
    self.debugLabel.pos = (0, H - (self.btn_height + self.debugLabel.minimum_height))
  
  def togglePython(self, *args):
    # set python interpreter flag..
    gPyInterpreter.setExitOnTouchPrev(False)
    gPyInterpreter.toggle()
     
  def toggleShowUpdate(self, *args):
    self.bShowUpdate = not self.bShowUpdate
    self.bUpdate = True
  
  def toggleDebug(self, *args):
    if self.debugLabel in self.children:
      self.remove_widget(self.debugLabel)
      self.btn_layout.remove_widget(self.btn_clear)
      self.btn_layout.remove_widget(self.btn_update)
      self.btn_layout.remove_widget(self.btn_python)
      self.btn_layout.size = (W*0.25, self.btn_layout.size[1])
    else:
      self.add_widget(self.debugLabel)
      self.btn_layout.add_widget(self.btn_clear)
      self.btn_layout.add_widget(self.btn_update)
      self.btn_layout.add_widget(self.btn_python)
      self.btn_layout.size = (W, self.btn_layout.size[1])

  def showFrame(self, bShow):
    self.bShowFrame = bShow

  def saveLogFile(self):
    if self.bSaveLog:
      logFile = open('log.txt', 'w')
      szString = "\n".join(self.logBuffer)
      logFile.write(szString)
      logFile.close()
  
  def clearPrint(self, inst):
    self.szString = ""
    self.szStatic = ""
    self.bUpdate = True 
     
  def Print(self, szString):
    if not self.bShow:
      return
      
    if type(szString) is not str:
      szString = str(szString)
    if self.bSaveLog:
      self.logBuffer.append(szString)
    if self.szString == "":
      self.szString = szString
    else:
      self.szString = "\n".join([self.szString, szString])

  def log(self, szString, insertPos = -1):
    if not self.bShow:
      return
      
    if type(szString) is not str:
      szString = str(szString)
    if self.bSaveLog:
      self.logBuffer.append(szString)
    self.bUpdate = True
    if self.szStatic == "":
      self.szStatic = szString
    else:
      if insertPos <= 0:
        self.szStatic = "\n".join([szString, self.szStatic])
      else:
        # insert mode
        szTemp = self.szStatic.split("\n")
        szTemp.insert(insertPos, szString)
        self.szStatic = "\n".join(szTemp)
    # write to logger
    Logger.info(szString)
      
  def showProp(self, obj, start = 0):
    if not self.bShow:
      return
      
    for x,i in enumerate(dir(obj)[start:-1]):
      if self.Print(str(x+start)+'.'+i) == False:
        return
  
  def update(self):
    if not self.bShow:
      return
    if self.bShowFrame:
      self.checkFrameTime += fFrameTime
      self.frameCount += 1.0
      if self.checkFrameTime > 1.0:
        self.checkFrameTime /= self.frameCount
        self.lastFrameTime = "%.2f" % (1.0/self.checkFrameTime)
        self.checkFrameTime = 0.0
        self.frameCount = 0.0
        self.fps.text = str(self.lastFrameTime)

    if self.szOldString != self.szString:
      self.szOldString = self.szString
      self.bUpdate = True
      
    if self.bUpdate:
      szString = ""
      if self.szStatic == "":
        szString = self.szString
      elif self.szString == "":
        szString = self.szStatic
      else:
        szString = "\n".join([self.szStatic, self.szString])
      self.debugLabel.text = szString
      self.refreshDebugLabel()
    self.bUpdate = False
    self.szString = ""

#---------------------#
# CLASS : MyScreen
#---------------------#
class MyScreen(Singleton):
  def __init__(self):
    self.screenMgr = ScreenManager(size=WH)
    self.name = "Root Screen"
    self.transition = WipeTransition()
    # or self.transition = SlideTransition(direction="down")
    self.emptyScreen = Screen(name = "empty screen")
    #self.emptyScreen.add_widget(Label(text="empty.screen"))
    self.add_screen(self.emptyScreen)
    self.current_screen(self.emptyScreen)
    
  def prev_screen(self):
    prev_screen = self.screenMgr.previous()
    if prev_screen:
      self.screenMgr.current = prev_screen
  
  def add_screen(self, screen):
    if screen.name not in self.screenMgr.screen_names:
      self.screenMgr.add_widget(screen)
    
  def current_screen(self, screen):
    if True or self.screenMgr.current != screen.name and self.screenMgr.has_screen(screen.name):
      self.screenMgr.current = screen.name
    
  def remove_screen(self, screen):
    if screen.name in self.screenMgr.screen_names:
      self.screenMgr.remove_widget(screen)
      self.prev_screen()
  
  def get_current_screen(self):
    return self.screenMgr.current

#---------------------#
# CLASS : MyWidget
#---------------------#
class MyWidget(Widget, Singleton):
  def __init__(self):
    super(MyWidget, self).__init__(size=WH)
    self.name = "Root Widget"
   
#---------------------#
# CLASS : MyRoot
#---------------------#
class MyRoot(App, Singleton):
  buildDone = False
  bPopup = False
  popupLayout = None
  bProgress = False
  progressPopup = None
  progress = None
  appList = []
  startAppList = []
  jobGroup = []
  myWidget = MyWidget.instance()
  myScreen = MyScreen.instance()
  startPoint = None
  keyboard = None
  keyboard_height = 0
  bAccelerometer = False
  bShowDebug = True
  acc = [0,0,0]
  
  def __init__(self):
    super(MyRoot, self).__init__()
    self.onTouchPrev = self.popup_exit
    
  def show_debug(self, bShow):
    self.bShowDebug = bShow

  def getAcc(self):
    return self.acc
    
  def getKeyboard(self):
    if not self.keyboard:
      self.keyboard = Window.request_keyboard(None, Widget(), 'text')
    return self.keyboard
    
  def refreshKeyboardHeight(self):
    if not self.keyboard:
      self.keyboard = Window.request_keyboard(None, Widget(), 'text')
    self.keyboard_height = 0
    fTime = time.time()
    while self.keyboard_height == 0:
      self.keyboard_height = Window.keyboard_height
      if self.keyboard_height == 0 and (time.time() - fTime) > 1.0:
        self.keyboard_height = H*0.3
    self.keyboard.release()
      
  def getKeyboardHeight(self):
    if self.keyboard_height == 0:
      self.refreshKeyboardHeight()
    elif Window.keyboard_height > 0 and Window.keyboard_height != self.keyboard_height:
      self.keyboard_height = Window.keyboard_height
    return self.keyboard_height
    
  def setAccelerometer(self, bSet):
    self.bAccelerometer = bSet
    
  def setKeyboardMode(self, mode=''):
    # '', 'below_target', 'pan', 'scale', 'resize'
    Window.softinput_mode = mode
    
  def _get_clipboard(f):
    def called(*args, **kargs):
      self = args[0]
      if not PythonActivity._clipboard:
        pass
      return f(*args, **kargs)
    return called

  @_get_clipboard
  def getClipboard(self, mimetype='text/plain'):
    clippy = PythonActivity._clipboard
    if VER.SDK_INT < 11:
      data = clippy.getText()
    elif clippy:
      ClipDescription = autoclass('android.content.ClipDescription')
      primary_clip = clippy.getPrimaryClip()
      if primary_clip:
        try:
          return primary_clip.getItemAt(0).coerceToText(PythonActivity.mActivity)
        except Exception:
          log('Clipboard: failed to paste')
    return ''
  
  # touch previous key
  def _key_handler(self, a,b,c,d,e):
    if b == 1001:
      if self.bPopup and self.popupLayout:
        self.popupLayout.dismiss()
        self.bPopup = False
      else:
        self.onTouchPrev()
      
  def build(self):
    self.root = Widget()
    
    # enable accelerometer
    if self.bAccelerometer:
      self.hardware = autoclass('org.renpy.android.Hardware')
      self.hardware.accelerometerEnable(True)
    
    # set keyboard mode - '', 'pan', 'scale', 'resize'
    self.setKeyboardMode('')
    self.refreshKeyboardHeight()
    
    global bButtonLock
    bButtonLock = False
    self.bPopup = False
    
    self.root.add_widget(self.myScreen.screenMgr)
    self.root.add_widget(self.myWidget)
    
    # debug print
    debugPrint = DebugPrint.instance()
    debugPrint.init(self.bShowDebug)
    if self.bShowDebug:
      self.root.add_widget(debugPrint)
    
    self.bind(on_start = self.post_build_init)
        
    self.buildDone = True
    return self.root
          
  def post_build_init(self,ev):
    global isAndroid
    if isAndroid:
      #android.map_key(android.KEYCODE_MENU, 1000) 
      android.map_key(android.KEYCODE_BACK, 1001) 
      android.map_key(android.KEYCODE_HOME, 1002) 
      android.map_key(android.KEYCODE_SEARCH, 1003) 

    win = self._app_window 
    win.bind(on_keyboard=self._key_handler)
    
    # regist update function
    Clock.schedule_interval(self.update, fUpdateTime)
    
  def regist(self, app):
    if app:
      if app in self.appList:
        return
      # start method
      if hasattr(app, "start"):
        self.startAppList.append(app)
      # update method
      if hasattr(app, "update"):
        Clock.schedule_interval(app.update, fUpdateTime)
      else:
        raise AttributeError("must implement update function..")
      # update state  
      if hasattr(app, "updateState"):
        Clock.schedule_interval(app.updateState, fUpdateTime)
      # regist app
      self.appList.append(app)
    
  def remove(self, app):
    if app in self.appList:
      self.appList.remove(app)
      Clock.unschedule(app.update)
    
  def update(self, frameTime):
    if not self.buildDone:
      return
      
    global fFrameTime, fAccTime
    fFrameTime = frameTime
    fAccTime += frameTime
    
    # doing job... it's just for show progress popup.
    while self.jobGroup:
      self.jobGroup[0].update()
      if self.jobGroup[0].isComplete():
        self.jobGroup.pop(0)
      else:
        break
        
    # get accelerometer
    if self.bAccelerometer and autoclass:
      self.acc = self.hardware.accelerometerReading()
      
    debugPrint = DebugPrint.instance()
    debugPrint.update()
    
    if debugPrint.bShowUpdate:
      self.show_widgets(self.root)      
      for app in self.appList:
        debugPrint.Print("Update : " + app.__class__.__name__)
        
    while self.startAppList:
      app = self.startAppList.pop()
      app.start()
        
  def show_widgets(self, parent, level=0):
    for child in parent.children:
      name = child.__class__.__name__
      if hasattr(child, "name"):
        name += " - " + child.name
      elif hasattr(child, "text"):
        n = child.text.find("\n")
        szString = child.text[:n] if n > 0 else child.text
        if len(szString) > 20:
          szString = szString[:20] + "..."
        name += " - " + szString
      DebugPrint.instance().Print("    " * level + name)
      self.show_widgets(child, level+1)

  def run(self, startPoint = None):
    self.startPoint = startPoint
    self.regist(startPoint)
    App.run(self)
  
  def exit(self, instance=None):
    DebugPrint.instance().saveLogFile()
    self.stop()
  
  def on_pause(self):
    return True
  
  def add_widget(self, widget):
    self.myWidget.add_widget(widget)
  
  def remove_widget(self, widget):
    self.myWidget.remove_widget(widget)
  
  def add_screen(self, screen):
    self.myScreen.add_screen(screen)
    
  def current_screen(self, screen):
    self.myScreen.current_screen(screen)
  
  def remove_screen(self, screen):
    self.myScreen.remove_screen(screen)
    
  def get_current_screen(self):
    return self.myScreen.get_current_screen()
    
  def getTouchPrev(self):
    return self.onTouchPrev
    
  def setTouchPrev(self, func):
    self.onTouchPrev = func if func else self.popup_exit
  
  def popup_exit(self):
    self.popup("Exit?", "", self.exit, None)
    
  def popup(self, title, message, lambdaYes, lambdaNo):
    if self.bPopup:
      return
    self.bPopup = True
    content = BoxLayout(orientation="vertical", size_hint=(1,1))
    self.popupLayout = Popup(title = title, content=content, auto_dismiss=False, size_hint = (0.9, 0.3))
    content.add_widget(Label(text=message))
    btnLayout = BoxLayout(orientation="horizontal", size_hint=(1,1), spacing=kivy.metrics.dp(20))
    btn_Yes = Button(text='Yes')
    btn_No = Button(text='No')
    btnLayout.add_widget(btn_No)
    btnLayout.add_widget(btn_Yes)
    
    content.add_widget(btnLayout)
    bResult = True
    def closePopup(instance, bYes):
      if bYes and lambdaYes:
        lambdaYes()
      elif lambdaNo:
        lambdaNo()
      self.popupLayout.dismiss()
      self.bPopup=False
    btn_Yes.bind(on_press=lambda inst:closePopup(inst, True))
    btn_No.bind(on_press=lambda inst:closePopup(inst, False))
    self.popupLayout.open()
    return
  
  # create Job insrance
  def newJob(self, title = "Progress.."):
    job = Job(title)
    self.jobGroup.append(job)
    return job
  
  def isProgress(self):
    return self.bProgress
    
  def createProgressPopup(self, title, itemCount):
    self.destroyProgressPopup()
    # loading flag
    self.bProgress = True
    content = Widget()
    sizehintW = 0.3
    sizehintH = 0.25
    self.progressPopup = Popup(title = title, content=content, auto_dismiss=False, size_hint = (sizehintW, sizehintH))
    content.pos = self.progressPopup.pos
    pbSize = mul(WH, (sizehintW * 0.9, sizehintH * 0.9))
    self.progress = ProgressBar(value=0, max=itemCount, pos=sub(cXY, (pbSize[0] * 0.5, sizehintH * H * 0.75)), size=pbSize)
    content.add_widget(self.progress)
    self.progressPopup.open()
    
  def increaseProgress(self):
    if self.progress:
      self.progress.value += 1
    
  def destroyProgressPopup(self):
    if self.progressPopup:
      self.progressPopup.dismiss()
      self.progressPopup = None
    # loading flag
    self.bProgress = False

#---------------------#
# CLASS : StateItem
#---------------------#
class StateItem():  
  stateMgr = None
  
  def onEnter(self):
    pass
    
  def onUpdate(self):
    pass
    
  def onExit(self):
    pass
  
  def setState(self, state):
    if self.stateMgr:
      self.stateMgr.setState(state)
  
#---------------------#
# CLASS : StateMachine
#---------------------#
class StateMachine(object):
  stateCount = 0
  stateList = {}
  curState = None
  oldState = None
  
  def __init__(self):
    object.__init__(self)
    self.stateCount = 0
    self.stateList = {}
    self.curState = None
    self.oldState = None
    
  def addState(self, stateItem):
    self.stateList[stateItem] = stateItem()
    self.stateCount = len(self.stateList)
    stateItem.stateMgr = self
  
  def getCount(self):
    return self.stateCount
    
  def isState(self, index):
    return index == self.curState
    
  def getState(self):
    return self.curState

  def getStateItem(self):
    if self.curState:
      return self.stateList[self.curState]

  def setState(self, index, reset=False):
    if index:
      if index != self.curState:
        self.oldState = self.curState
        self.curState = index
        if self.oldState:
          self.stateList[self.oldState].onExit()
        self.stateList[index].onEnter()
      elif reset:
        self.stateList[index].onEnter()

  def updateState(self, *args):
    if self.curState:
      self.stateList[self.curState].onUpdate()
  
  def update(self, dt):
    '''must override'''
    pass

#---------------------#
# MultiMethod
#---------------------#
registry = {}

class MultiMethod(object):
    def __init__(self, name):
        self.name = name
        self.typemap = {}
    def __call__(self, *args):
        types = tuple(arg.__class__ for arg in args) # a generator expression!
        function = self.typemap.get(types)
        if function is None:
            raise TypeError("no match")
        return function(*args)
    def register(self, types, function):
        if types in self.typemap:
            raise TypeError("duplicate registration")
        self.typemap[types] = function

def multimethod(*types):
    def register(function):
        name = function.__name__
        mm = registry.get(name)
        if mm is None:
            mm = registry[name] = MultiMethod(name)
        mm.register(types, function)
        return mm
    return register
    
overload = multimethod

@overload()  
def getX():
  return cX
  
@overload(int)  
def getX(a):
  return cX*a

@overload(int, int)
def getX(a,b):
  return cX*b
  
#---------------------#
# loading post process
#---------------------#
loading_postprocess()