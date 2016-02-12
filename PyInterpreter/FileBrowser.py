import Utility as Util
from Utility import *

from Constants import *
import traceback

global gFileBrowser

#---------------------#
# CLASS : TouchableLabel
#---------------------#  
class TouchableLabel(Label):
  isDirType = False
  def on_touch_down(self, touch):
    if self.collide_point(*touch.pos):
      selectfile = os.path.join(gFileBrowser.lastDir, self.text[2:] if self.isDirType else self.text)
      if os.path.isdir(selectfile):
        gFileBrowser.open_directory(selectfile)
      elif os.path.isfile(selectfile):
        gFileBrowser.select_file(selectfile)
      
  def setType(self, isDir):
    self.isDirType = isDir
    if isDir:
      self.color = [1,1,0.5,2]
      self.text = "> " + self.text
    else:
      self.color = [1,1,1,1]
       
#---------------------#
# CLASS : FileBrowser
#---------------------#    
class FileBrowser(Singleton):
  def __init__(self, ui):
    global gFileBrowser
    gFileBrowser = self
    self.ui = ui
    self.lastDir = os.path.abspath("/")
    self.mode = ""
    # filename input layout
    self.filenameLayout = BoxLayout(orientation = "horizontal", size_hint=(1, None))
    self.filenameInput = TextInput(text="input filename", multiline = False, padding_y="15dp", font_name=defaultFont, size_hint=(1,None))
    self.filenameInput.height = self.filenameInput.minimum_height
    self.filenameLayout.height = self.filenameInput.height
    self.filenameInput.bind(focus=self.inputBoxFocus)
    self.btn_ok = Button(text="Ok", size_hint=(0.2,1), background_color=[1,1,1,2])
    def func_ok(inst):
      if self.mode == szFileBrowserOpen:
        self.open_file()
      elif self.mode == szFileBrowserSaveAs:
        self.save_as()
    self.btn_ok.bind(on_release = func_ok)
    self.filenameLayout.add_widget(self.filenameInput)
    self.filenameLayout.add_widget(self.btn_ok)
    
    # file browser
    self.fileLayout = BoxLayout(orientation="vertical", size_hint=(1,None))
    self.fileSV = ScrollView(size_hint=(1,1))
    self.fileSV.add_widget(self.fileLayout)
    
    # current directory
    self.curDir = Label(text="", text_size=(W * 0.9, None), size_hint_y=None, height=kivy.metrics.dp(50))
    
    #  rowser layout
    self.browserLayout = BoxLayout(orientation="vertical", pos_hint={"top":1}, size_hint=(1,1))
    self.browserLayout.add_widget(self.curDir)
    self.browserLayout.add_widget(self.fileSV)
    self.browserLayout.add_widget(self.filenameLayout)
    self.popup = Popup(title = "File Browser", content=self.browserLayout, auto_dismiss=False, size_hint=(1, 0.8)) 
  
  def open_directory(self, lastDir):
    absPath = os.path.abspath(lastDir)
    try:
      lastDir, dirList, fileList = os.walk(absPath).next()
    except:
      log(traceback.format_exc())
      toast("Cannot open directory")
      return False
    self.lastDir = absPath
    self.curDir.text = self.lastDir
    self.fileLayout.clear_widgets()
    fileList = sorted(fileList, key=lambda x:x.lower())
    dirList = sorted(dirList, key=lambda x:x.lower())
    fileList = dirList + fileList
    fileList.insert(0, "..")
    labelHeight = kivy.metrics.dp(25)
    for filename in fileList:
      absFilename = os.path.join(self.lastDir, filename)
      label = TouchableLabel(text=filename, font_size="15dp", size_hint_y = None, size=(W*0.9, labelHeight), shorten=True, shorten_from="right", halign="left")
      label.text_size = label.size
      label.setType(os.path.isdir(absFilename))
      self.fileLayout.add_widget(label)
    self.fileLayout.height = labelHeight * len(self.fileLayout.children)
  
  def open_file(self):
    self.close()
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.ui.editorLayout.open_file(filename)
    
  def save_as(self):
    if self.filenameInput.text:
      filename = os.path.join(self.lastDir, self.filenameInput.text)
      self.ui.editorLayout.save_as(filename)
    self.close()
    
  def select_file(self, selectfile):
    # lastdir
    self.lastDir, filename = os.path.split(selectfile)
    if not os.path.isdir(self.lastDir):
      self.lastDir = os.path.abspath(".")
    # set filename
    self.filenameInput.text = filename
      
  def showOpenLayout(self):
    self.mode = szFileBrowserOpen
    self.btn_ok.text = "Open"
    self.filenameInput.text = ""
    self.popup.open()
    self.open_directory(self.lastDir)
  
  def showSaveAsLayout(self):
    self.mode = szFileBrowserSaveAs
    self.btn_ok.text = "Save"
    self.filenameInput.text = ""
    self.popup.open()
    self.open_directory(self.lastDir)
     
  def close(self):
    self.inputBoxForceFocus(False)
    self.popup.dismiss()
    self.ui.setMode(szEditor)
     
  def touchPrev(self):
    if self.filenameInput.focus:
      self.inputBoxForceFocus(False)
    else:
      self.close()
    
  def inputBoxForceFocus(self, bFocus):
    if self.filenameInput and bFocus != self.filenameInput.focus:
      self.reFocusInputText = False
      self.filenameInput.focus = bFocus 
      
  def inputBoxFocus(self, inst, bFocus):
    bAlwaysPreserveFocus = False
    if not bFocus:
      if self.reFocusInputText:
        self.reFocusInputText = bAlwaysPreserveFocus
        inst.focus = True
    self.reFocusInputText = bAlwaysPreserveFocus
    self.refreshLayout()
    
  def refreshLayout(self):
    if self.browserLayout.size_hint_y != None:
      self.browserLayout.size_hint_y = None
      self.browserLayout_height = self.browserLayout.height
    
    if self.filenameInput.focus: 
      offset = gMyRoot.getKeyboardHeight() - self.browserLayout.pos[1]
      self.browserLayout.height = self.browserLayout_height - offset
    else:
      self.browserLayout.height = self.browserLayout_height
    