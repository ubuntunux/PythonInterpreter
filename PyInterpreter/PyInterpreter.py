import Utility as Util
from Utility import *
from kivy.uix.carousel import Carousel

from glob import glob

from Tutorial import TutorialLayout
from Editor import EditorLayout
from FileBrowser import FileBrowser

from Constants import *

#---------------------#
# CLASS : REPL
#---------------------#
class REPL(Singleton):
  name = "Python REPL"
  result = ""
  code = []
  lastCode = ""
  myGlobals = {}
  isIndentMode = False
  ui = None
  
  def __init__(self, ui):
    self.ui = ui
       
  def onConsoleInput(self, inputText):
    result = 0
    try:
      result = self.run_script(inputText)
    except:
      log("error")
    
    # insert result
    if result:
      self.ui.displayText(result, 0)
    
    if self.lastCode:
      temp = self.lastCode
      self.lastCode = None
      self.onConsoleInput(temp)
      
  def run_script(self, code):
    # run script
    stripCode = code.strip()
    if self.code and (stripCode == "" or code[0] != " " and code[0] != "\t"):
      self.lastCode = code
      code = "\n".join(self.code)
      self.isIndentMode = False
      self.code = []
      
    # inner indent mode
    elif self.code or stripCode and stripCode[-1] == ":":
      self.code.append(code)
      self.isIndentMode = True
      return None
      
    try:
      self.old_stdout = sys.stdout
      self.redirected_output = sys.stdout = StringIO()
      try:
        print eval(code, self.myGlobals)
      except:
        exec(code, self.myGlobals)
        
      sys.stdout = self.old_stdout
      self.result = self.redirected_output.getvalue()
    except Exception, e:
      self.errorstring = traceback.format_exc()
      self.result = ("ERROR: " + self.errorstring)
    return self.result[:-1]
    
#---------------------#
# CLASS : PyInterpreter
#---------------------#    
class PyInterpreter(Singleton):
  isInit = False
  bExitOnTouchPrev = True
  outputWidth = W
  prevMode = ""
  currentMode = "" # console, tutorial, editor
  emptyWidget = Widget(size_hint=(None,None), size=(0,0))
  
  def init(self):
    if self.isInit:
      return
      
    # add screens
    self.screen = Screen(name=szConsole)
    self.editorLayout = EditorLayout(self)
    self.tutorialLayout = TutorialLayout(self)
    self.fileBrowser = FileBrowser(self)
    
    self.repl = REPL(self)
    self.history = ["",]
    self.historyIndex = -1
    self.historyCount = 100
    self.lastIndentSpace = ""
    self.bIndentMode = False
    self.reFocusInputText = False
    self.oldTouchPrev = None
    self.textInputWidth = W * (4.0/5.0)
    
    # console menu layout
    self.consoleMenuLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height="35dp")
    btn_clear = Button(text="Clear", background_color=darkGray)
    btn_clear.bind(on_release = lambda inst:self.clearOutput())
    btn_prev = Button(text="<<", background_color=darkGray)
    btn_next = Button(text=">>", background_color=darkGray)
    self.consoleMenuLayout.add_widget(btn_clear)
    self.consoleMenuLayout.add_widget(btn_prev)
    self.consoleMenuLayout.add_widget(btn_next)
    self.screen.add_widget(self.consoleMenuLayout)
    
    # screen menu layout
    self.screenMenuLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height="35dp", pos=(0,0))
    btn_console = Button(text="Console", background_color=[1.5,0.8,0.8,2]) 
    btn_editor = Button(text="Code Editor", background_color=[0.8,1.5,0.8,2])
    btn_tutorial = Button(text="Python Tutotial", background_color=[0.8,0.8,1.5,2])
    btn_editor.bind(on_release=lambda inst:self.setMode(szEditor))
    btn_tutorial.bind(on_release=lambda inst:self.setMode(szTutorial))
    self.screenMenuLayout.add_widget(btn_console)
    self.screenMenuLayout.add_widget(btn_editor)
    self.screenMenuLayout.add_widget(btn_tutorial)
    self.screen.add_widget(self.screenMenuLayout)
    
    # text input
    self.consoleInput = TextInput(text = "text", multiline=False, size_hint=(None, None), auto_indent = True, font_name=defaultFont, 
      background_color=(.1, .1, .1, 1), foreground_color=(1,1,1,1), text_size=(0,0), font_size="14dp", padding_x="20dp", padding_y="15dp")  
    self.consoleInput.size = (W, self.consoleInput.minimum_height)
    self.consoleInput.text = ""
    '''
    def paste():
      self.consoleInput.insert_text(gMyRoot.getClipboard())
      self.refreshLayout()
    self.consoleInput.paste = paste
    '''
    self.consoleInput.bind(on_text_validate = self.onConsoleInput)
    self.consoleInput.bind(focus = self.inputBoxFocus)
    
    # textinput scroll view
    self.textInputSV = ScrollView(size_hint=(None, None), size = (W, self.consoleInput.minimum_height))
    self.textInputSV.scroll_y = 0
    self.textInputSV.add_widget(self.consoleInput)
    
    # add input widget
    self.screen.add_widget(self.textInputSV)
    
    # run button
    self.btn_run = Button(text="Run", size_hint=(None,None), size =(W-self.consoleInput.size[0], self.consoleInput.size[1]),\
      background_color=(1.3,1.3,2,2))
    self.btn_run.bind(on_release = lambda inst:self.onConsoleInput(self.consoleInput, True))
    self.btn_run.pos = (W - self.btn_run.size[0], 0)
    self.screen.add_widget(self.btn_run)
      
    # output
    self.outputSV = ScrollView(size_hint=(None, None))
    self.screen.add_widget(self.outputSV)
    
    self.outputLayout = BoxLayout(orientation="vertical", size_hint=(None,None))
    self.outputSV.add_widget(self.outputLayout)
    
    def func_prev(inst):         
      if len(self.history) > 0:
        self.historyIndex -= 1
        if self.historyIndex < 0:
          self.historyIndex = len(self.history) - 1
        text = self.history[self.historyIndex]
        if text.find("\n") > -1:
          self.bIndentMode = True
        self.setInputText(text)
    btn_prev.bind(on_release = func_prev)
    
    def func_next(inst):
      if len(self.history) > 0:
        self.historyIndex += 1
        if self.historyIndex >= len(self.history):
          self.historyIndex = 0
        text = self.history[self.historyIndex]
        if text.find("\n") > -1:
          self.bIndentMode = True
        self.setInputText(text)
    btn_next.bind(on_release = func_next)    

    # show output layout
    self.displayText("Python " + sys.version.strip(), 0)
    self.isInit = True
    
  def setMode(self, mode):
    if mode == self.currentMode:
      return
      
    self.prevMode = self.currentMode
    self.currentMode = mode
    
    # restore..
    if self.prevMode == szConsole:
      self.reFocusInputText = False
      self.inputBoxForceFocus(False)
    
     # set mode layout  
    if mode == szConsole:
      gMyRoot.current_screen(self.screen)
      self.refreshLayout()
    elif mode == szEditor:
      gMyRoot.current_screen(self.editorLayout.screen)
    elif mode == szTutorial:
      gMyRoot.current_screen(self.tutorialLayout.screen)
    elif mode == szFileBrowserOpen:
      self.fileBrowser.showOpenLayout()
    elif mode == szFileBrowserSaveAs:
      self.fileBrowser.showSaveAsLayout()
    
  def setExitOnTouchPrev(self, bValue):
    self.bExitOnTouchPrev = bValue
  
  def start(self):
    self.show()
    
  def update(self, dt):
    pass
  
  def clearOutput(self):
      self.outputLayout.clear_widgets()
      self.outputLayout.size = (W, 0)
      
  def outputLayout_add_widget(self, widget):
    self.outputLayout.add_widget(widget)
    self.outputLayout.height += widget.height + widget.padding[1] + widget.padding[3]

  def displayText(self, text, scroll_y, background_color=(1,1,1,0)):
    if type(text) != str:
      text = str(text)
       
    output = TextInput(markup = True, text="", halign='left', valign='top', readonly=True, font_size="12dp", font_name = defaultFont,
      multiline=True, background_color=background_color, foreground_color=(1,1,1,1), size_hint=(None,None), size = (self.outputWidth, 0))
    output.text = text
    output.size = (self.outputWidth, output.minimum_height)
    
    self.outputLayout.add_widget(output)
    self.outputLayout.size = (self.outputWidth, self.outputLayout.size[1] + output.size[1])
    self.outputSV.scroll_x = 0
    self.outputSV.scroll_y = scroll_y
    
  def onConsoleInput(self, inst, bForceRun = False):
    self.reFocusInputText = True
    if inst.text.strip():
      bRunCode = len(inst.text) == self.consoleInput.cursor_index()
      lastLine_nonStrip = inst.text.split("\n")[-1]
      lastLine = lastLine_nonStrip.strip()
      # indent mode - continue input but not run
      if not bForceRun and lastLine and (lastLine[-1] in ("\\", ":") or self.bIndentMode or not bRunCode):
        self.bIndentMode = True
        # get indent space
        self.lastIndentSpace = ""
        if self.bIndentMode:
          for i in lastLine_nonStrip:
            if i in [" ", "\t"]:
              self.lastIndentSpace += i
            else:
              break
        inst.insert_text("\n" + self.lastIndentSpace)
        self.consoleInput.size = (W, self.consoleInput.minimum_height)
        return
      # check indent mode - run code
      self.bIndentMode = False
      # pop input text from history
      if len(self.history) > 0 and self.historyIndex > -1 \
        and self.historyIndex < len(self.history) and self.history[self.historyIndex] == inst.text:
          self.history.pop(self.historyIndex)
      # append item to history
      if self.currentMode == szConsole:
        self.history.append(inst.text.strip())
      # check history count
      if len(self.history) > self.historyCount:
        self.history = self.history[:self.historyCount]
      self.historyIndex = len(self.history)
      # display input text to output widget
      if self.currentMode == szConsole:
        lines = inst.text.split("\n")
        result = []
        for i, line in enumerate(lines):
          line = (">>> " if i == 0 else "... ") + line
          result.append(line)
        result = "\n".join(result)
        self.displayText(result, 0)
      elif self.currentMode == szEditor:
        currentDocument = ">>> Run Untitled.py"
        self.displayText("\n".join(["-" * len(currentDocument), currentDocument + " - " + time.ctime()]), 0)
      # run code
      self.repl.onConsoleInput(inst.text)
      # end message
      if self.currentMode == szEditor:
        self.displayText("Done.", 0)
        
      # clear text input
      if self.currentMode == szConsole:
        self.setInputText("")
      
  def refreshLayout(self):
    if self.currentMode == szConsole:  
      keyboardHeight = gMyRoot.getKeyboardHeight() if self.consoleInput.focus else 0
      limitHeight = (H - topMargin - keyboardHeight) * 0.5
      if self.consoleInput.minimum_height > limitHeight:
        height = limitHeight
      else:
        height = self.consoleInput.minimum_height
      self.screenMenuLayout.pos = (0, keyboardHeight)
      self.textInputSV.pos = (0, self.screenMenuLayout.top)
      self.textInputSV.size = (self.textInputWidth, height)
      self.consoleInput.size = (self.textInputWidth, self.consoleInput.minimum_height)
      self.btn_run.pos = (self.textInputSV.size[0], self.textInputSV.pos[1])
      self.btn_run.size = (W - self.textInputSV.size[0], self.textInputSV.size[1])
      self.consoleMenuLayout.pos = (0, self.textInputSV.top)
      self.outputSV.pos = (0, self.consoleMenuLayout.top)
      self.outputSV.size = (W, H - self.outputSV.pos[1] - topMargin)
      
  def setInputText(self, text):
    self.consoleInput.text = text
    if self.consoleInput.size[1] != self.consoleInput.minimum_height:
      self.refreshLayout()
  
  def insertInputText(self, text):
    self.consoleInput.insert_text(text)
    if self.consoleInput.size[1] != self.consoleInput.minimum_height:
      self.refreshLayout()
  
  def inputBoxForceFocus(self, bFocus):
    if bFocus != self.consoleInput.focus:
      self.consoleInput.focus = bFocus 
      
  def inputBoxFocus(self, inst, bFocus):
    bAlwaysPreserveFocus = True
    if not bFocus:
      if self.reFocusInputText:
        self.reFocusInputText = bAlwaysPreserveFocus
        inst.focus = True
    self.reFocusInputText = bAlwaysPreserveFocus
    self.refreshLayout()
    
  def update(self, dt):
    pass
    
  def touchPrev(self):
    if self.currentMode == szEditor:
      self.editorLayout.touchPrev()
    elif self.currentMode in (szFileBrowserOpen, szFileBrowserSaveAs):
      self.fileBrowser.touchPrev()
    elif self.currentMode == szTutorial:
      self.tutorialLayout.touchPrev()
    elif self.consoleInput.focus:
      self.reFocusInputText = False
      self.inputBoxForceFocus(False)
    else:
      self.exit()
      
  def toggle(self):
    if not self.isInit:
      self.init()
      
    if self.screen.name == gMyRoot.get_current_screen():
      self.close()
    else:
      self.show()
      
  def show(self):
    if not self.isInit:
      self.init()
      
    gMyRoot.add_screen(self.screen)
    gMyRoot.add_screen(self.editorLayout.screen)
    gMyRoot.add_screen(self.tutorialLayout.screen)
    gMyRoot.current_screen(self.screen)
    self.oldTouchPrev = gMyRoot.getTouchPrev()
    gMyRoot.setTouchPrev(self.touchPrev)
    self.setMode(szConsole)
  
  def close(self):
    gMyRoot.setTouchPrev(self.oldTouchPrev)
    gMyRoot.remove(self)
    gMyRoot.remove_screen(self.screen)
    gMyRoot.remove_screen(self.editorLayout.screen)
    gMyRoot.remove_screen(self.tutorialLayout.screen)
    if self.bExitOnTouchPrev:
      self.editorLayout.exit()
      gMyRoot.exit()
        
  def exit(self, *args):
    self.reFocusInputText = False
    self.inputBoxForceFocus(False)
    gMyRoot.popup("Exit Python?", "", self.close, None)