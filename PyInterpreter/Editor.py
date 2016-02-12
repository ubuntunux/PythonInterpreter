import Utility as Util
from Utility import *

import ConfigParser, tempfile, traceback
from glob import glob

from Constants import *
from collections import OrderedDict
from pygments.lexers import CythonLexer
from toast import toast

global gEditorLayout

#---------------------#
# CLASS : Editor
#---------------------#
class Editor(CodeInput):
  ui = None
  run_on_enter = None
  dirty = False
  parentTap = None
  
  def __init__(self, ui, parentTap, *args, **kargs):
    CodeInput.__init__(self, *args, **kargs)
    self.ui = ui
    self.old_text = ""
    self.parentTap = parentTap
    self.filename = ""
    
  def setFilename(self, filename):
    self.filename = filename
    if self.parentTap:
      if self.filename:
        self.parentTap.text = os.path.split(filename)[1]
      else:
        self.parentTap.text = "Untitled"
      if self.dirty:
        self.parentTap.text += "*"
    
  def setDirty(self, dirty):
    if self.dirty != dirty:
      self.dirty = dirty
      if dirty:
        self.parentTap.text += "*"
      else:
        if self.filename and self.parentTap:
          self.parentTap.text = os.path.split(self.filename)[1]
        else:
          self.parentTap.text = "Untitled"
    
  def loadFile(self, filename):
    try:
      # open file
      f = open(filename, "r")
      lines = list(f)
      f.close()
      self.old_text = self.text = "".join(lines)
      self.setFilename(filename)
      self.setDirty(False)
      toast("Loaded : " + self.parentTap.text)
    except:
      toast("Failed to load the file : " + os.path.split(filename)[1])
      log(traceback.format_exc())
      return False
    return True
      
  def saveFile(self, force = False):
    if self.dirty or force:
      if self.filename:
        try:
          f = open(self.filename, "w")
          f.write(self.text)
          f.close()
          self.setDirty(False)
          # check already opened document then close
          gEditorLayout.closeSameDocument(self)
          toast("Saved : " + self.parentTap.text)
        except:
          toast("Failed to save the file : " + os.path.split(filename)[1])
          log(traceback.format_exc())
      else:
        # untitled.document
        gEditorLayout.setMode(szFileBrowserSaveAs)
  
  def saveAsFile(self, filename):
    def do_save():
      self.filename = filename
      self.saveFile(force = True)
    # check overwrite
    if self.filename != filename and os.path.isfile(filename):
      gMyRoot.popup("File already exists. Overwrite?", os.path.split(filename)[1], do_save, None)
    else:
      do_save()
  '''  
  def paste(self):
    self.insert_text(gMyRoot.getClipboard())
    if self.run_on_enter:
      self.run_on_enter()
  ''' 
  def keyboard_on_key_down(self, window, keycode, text, modifiers):
    TextInput.keyboard_on_key_down(self, window, keycode, text, modifiers)
    enterKey = 13
    backspaceKey = 8
    key, key_str = keycode
    # set dirty mark
    if not self.dirty and self.old_text != self.text:
      self.setDirty(True)
      self.old_text = self.text
    if self.run_on_enter and key in (enterKey, backspaceKey):
      self.run_on_enter()
     
#---------------------#
# CLASS : EditorLayout
#---------------------#   
class EditorLayout():
  documentMap = OrderedDict({})
  currentDocumentTap = None
  textInputSV = None
  editorInput = None
  
  def __init__(self, ui):
    global gEditorLayout
    gEditorLayout = self
    self.ui = ui
    self.reFocusInputText = False
    self.screen = Screen(name = szEditor)
    # document list
    height = kivy.metrics.dp(45)
    self.documentTitleSV = ScrollView(orientation="horizontal", size_hint=(None, None), size=(W, height), pos=(0, H-height))
    self.documentTitleLayout = BoxLayout(size_hint=(None, 1))
    self.documentTitleSV.add_widget(self.documentTitleLayout)
    self.screen.add_widget(self.documentTitleSV)
    
    # menu layout
    height = kivy.metrics.dp(35)
    self.menuLayout = BoxLayout(size_hint=(1, None), height=height)
    self.screen.add_widget(self.menuLayout)
    self.menuDropDown = DropDown(size=(0,0), auto_dismiss=True)
    btn_menu = Button(text="Menu", size_hint_y=None, height=height, background_color=darkGray)
    def menuOpen(inst):
      self.inputBoxForceFocus(False)
      self.menuDropDown.open(inst)
    btn_menu.bind(on_release = menuOpen)
    btn_new = Button(text="New", size_hint_y=None, height=height, background_color=darkGray)
    btn_new.bind(on_release = self.createDocument, on_press=self.menuDropDown.dismiss)
    btn_open = Button(text="Open", size_hint_x=0.3, size_hint_y=None, height=height, background_color=darkGray)
    btn_open.bind(on_release=lambda inst:self.setMode(szFileBrowserOpen), on_press=self.menuDropDown.dismiss)
    btn_close = Button(text="Close", size_hint_y=None, height=height, background_color=darkGray)
    btn_close.bind(on_release=lambda inst:self.closeDocument(self.editorInput), on_press=self.menuDropDown.dismiss)
    btn_delete = Button(text="Delete", size_hint_y=None, height=height, background_color=darkGray)
    btn_delete.bind(on_release=lambda inst:self.deleteDocument(self.editorInput), on_press=self.menuDropDown.dismiss)
    btn_save = Button(text="Save", size_hint_y=None, height=height, background_color=darkGray)
    btn_save.bind(on_release=lambda inst:self.editorInput.saveFile(), on_press=self.menuDropDown.dismiss)
    btn_saveas = Button(text="Save As", size_hint_y=None, height=height, background_color=darkGray)
    btn_saveas.bind(on_release=lambda inst:self.setMode(szFileBrowserSaveAs), on_press=self.menuDropDown.dismiss)
    self.menuDropDown.add_widget(btn_new)
    self.menuDropDown.add_widget(btn_open)
    self.menuDropDown.add_widget(btn_close)
    self.menuDropDown.add_widget(btn_save)
    self.menuDropDown.add_widget(btn_saveas)
    self.menuDropDown.add_widget(btn_delete)
    self.menuLayout.add_widget(self.menuDropDown)
    
    btn_undo = Button(text="Undo", background_color=darkGray)
    btn_undo.bind(on_release=lambda inst:self.editorInput.do_undo())
    btn_redo = Button(text="Redo", background_color=darkGray)
    btn_redo.bind(on_release=lambda inst:self.editorInput.do_redo())
    btn_run = Button(text="Run", background_color=darkGray)
    btn_run.bind(on_release = self.runCode)
    self.menuLayout.add_widget(btn_menu)
    self.menuLayout.add_widget(btn_undo)
    self.menuLayout.add_widget(btn_redo)
    self.menuLayout.add_widget(btn_run)
    
    # screen menu layout
    self.screenMenuLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height="35dp")
    btn_console = Button(text="Console", background_color=[1.5,0.8,0.8,2])
    btn_editor = Button(text="Code Editor", background_color=[0.8,1.5,0.8,2])
    btn_tutorial = Button(text="Python Tutorial", background_color=[0.8,0.8,1.5,2])
    btn_console.bind(on_release=lambda inst:self.setMode(szConsole))
    btn_tutorial.bind(on_release=lambda inst:self.setMode(szTutorial))
    self.screenMenuLayout.add_widget(btn_console)
    self.screenMenuLayout.add_widget(btn_editor)
    self.screenMenuLayout.add_widget(btn_tutorial)
    self.screen.add_widget(self.screenMenuLayout)
    
    # load last opened document
    self.load_config()
    
    # create document
    if len(self.documentMap) == 0:
      self.createDocument()
    self.refreshLayout()
    
  def exit(self):
    self.save_config()
    
  def load_config(self):
    if not os.path.isfile(configFile):
      return
    parser = ConfigParser.SafeConfigParser()
    parser.read(configFile)
    
    # load document section
    doc_section = "Documents"
    temp_section = "Tempfiles"
    
    if parser.has_section(doc_section):
      for opt in parser.options(doc_section):
        filename = parser.get(doc_section, opt)       
        # open document
        if os.path.isfile(filename):
          self.open_file(filename)
          
        # remove tempfile
        if parser.has_option(temp_section, filename) and self.editorInput and self.editorInput.filename == filename:
          originFileName = parser.get(temp_section, filename)
          self.editorInput.setFilename(originFileName)
          self.editorInput.setDirty(True)
          
    # clear temp folder
    for filename in glob(os.path.join(tempDirectory, "*")):
      if os.path.splitext(filename)[1] == "":
        try:
          os.remove(filename)
        except:
          log(traceback.format_exc())
    
  def save_config(self):
    # make section
    if len(self.documentMap) > 0:
      parser = ConfigParser.SafeConfigParser()
      doc_section = "Documents"
      temp_section = "Tempfiles"
      parser.add_section(doc_section)
      parser.add_section(temp_section)
      for i, fileTap in enumerate(self.documentMap):
        editorInput = self.documentMap[fileTap][1]
        # save temp
        if editorInput.dirty:
          try:
            f = tempfile.NamedTemporaryFile(dir = tempDirectory, delete = False)
            f.write(editorInput.text)
            f.close()
            parser.set(doc_section, 'filename%d' % i, f.name)
            parser.set(temp_section, f.name, editorInput.filename)
          except:
            log(traceback.format_exc())
        else:
          parser.set(doc_section, 'filename%d' % i, editorInput.filename)
      # save config file 
      with open(configFile, 'w') as f:
        parser.write(f)
    
  def createDocument(self, *args):
    # add docjment tap
    font_size = kivy.metrics.dp(16)
    btn_tap = Button(text="Untitled", size_hint=(None,1), background_color = darkGray)
    btn_tap.width = (len(btn_tap.text) + 2) * font_size
    btn_tap.bind(on_release = self.changeDocument)
    self.documentTitleLayout.width += btn_tap.width
    self.documentTitleLayout.add_widget(btn_tap)
    self.documentTitleSV.scroll_x = 1
    
    # text input
    editorInput = Editor(ui=self, parentTap=btn_tap, text = "text", lexer=CythonLexer(), multiline=True, size_hint=(2, None), font_name=defaultFont, auto_indent = True,
      background_color=(.9, .9, .9, 1), font_size="14dp", padding_x="20dp", padding_y="15dp")  
    editorInput.height = editorInput.minimum_height
    editorInput.text = ""
    def refreshEditorInputSize(*args):
      if editorInput.size[1] != editorInput.minimum_height:
        self.refreshLayout()
    editorInput.run_on_enter = refreshEditorInputSize
    editorInput.bind(focus = self.inputBoxFocus)
    
    # textinput scroll view
    textInputSV = ScrollView(size_hint=(None, None), size = (W, editorInput.minimum_height))
    textInputSV.add_widget(editorInput)
    textInputSV.scroll_y = 0
    # add to map
    self.documentMap[btn_tap] = (textInputSV, editorInput)
    # show document
    self.changeDocument(btn_tap)
    
  def closeDocument(self, editorInput, force = False):
    if editorInput:
      tap = editorInput.parentTap
      if tap in self.documentMap:
        def close():
          tapIndex = self.documentMap.keys().index(tap)
          scrollView = self.documentMap.pop(tap)[0]
          if tap in self.documentTitleLayout.children:
            self.documentTitleLayout.remove_widget(tap)
            self.documentTitleLayout.width -= tap.width
          if scrollView.parent:
            scrollView.parent.remove_widget(scrollView)
          if len(self.documentMap) == 0:
            self.createDocument()
          # if current doc, select next document
          elif self.editorInput == editorInput:
            tapIndex = min(tapIndex, len(self.documentMap) -1)
            self.changeDocument(self.documentMap.keys()[tapIndex])
        # do close
        if force or not editorInput.dirty:
          close()
        elif editorInput.dirty:
          gMyRoot.popup("File has unsaved changes.", "Really close file?", close, None)  
  
  def closeSameDocument(self, editorInput):
    for fileTap in self.documentMap:
      curEditorInput = self.documentMap[fileTap][1]
      if curEditorInput != editorInput and curEditorInput.filename == editorInput.filename:
        self.closeDocument(curEditorInput, force = True)
        break
        
  def deleteDocument(self, editorInput):
    if not os.path.isfile(editorInput.filename):
      return 
    filename = os.path.split(editorInput.filename)[1]
    # delete file
    def deleteFile():
      try:
        self.closeDocument(editorInput)
        os.remove(editorInput.filename)
        toast("Delete the file : " + filename)
      except:
        log(traceback.format_exc())
    # ask delete?
    gMyRoot.popup("Delete selected file?", filename, deleteFile, None)
      
  def changeDocument(self, inst):
    if inst in self.documentMap and inst != self.currentDocumentTap:
      # remove keyboard
      self.inputBoxForceFocus(False)
      # old tap restore color
      if self.currentDocumentTap:
        self.currentDocumentTap.background_color = darkGray
      # new tap color
      inst.background_color = brightBlue
      # set new tap to current tap
      self.currentDocumentTap = inst
      if self.textInputSV and self.textInputSV.parent:
        self.textInputSV.parent.remove_widget(self.textInputSV)
      self.textInputSV, self.editorInput = self.documentMap[inst]
      self.screen.add_widget(self.textInputSV)
      self.refreshLayout()
      
  def open_file(self, filename):
    try:
      def loadFile():
        result = self.editorInput.loadFile(filename)
        if not result:
          self.closeDocument(self.editorInput, True)
      # check opened document
      for fileTap in self.documentMap:
        editorInput = self.documentMap[fileTap][1]
        if editorInput.filename == filename:
          self.changeDocument(fileTap)
          if editorInput.dirty:
            gMyRoot.popup("File has unsaved changes.", "Really open file?", loadFile, None)
          break
      else:
        self.createDocument()
        loadFile() 
    except:
      log("open file error")  
  
  def save_as(self, filename):
    self.editorInput.saveAsFile(filename)
    
  def runCode(self, inst):
    if self.editorInput.text.strip():
      self.ui.onConsoleInput(self.editorInput, True)
      self.setMode(szConsole)
    
  def touchPrev(self):
    if self.editorInput and self.editorInput.focus:
      self.inputBoxForceFocus(False)
    else:
      self.setMode(szConsole)
    
  def setMode(self, mode):
    self.menuDropDown.dismiss()
    self.reFocusInputText = False
    self.inputBoxForceFocus(False)
    self.ui.setMode(mode)
  
  def inputBoxForceFocus(self, bFocus):
    if self.editorInput and bFocus != self.editorInput.focus:
      self.reFocusInputText = False
      self.editorInput.focus = bFocus 
      
  def inputBoxFocus(self, inst, bFocus):
    bAlwaysPreserveFocus = True
    if not bFocus:
      if self.reFocusInputText:
        self.reFocusInputText = bAlwaysPreserveFocus
        inst.focus = True
    self.reFocusInputText = bAlwaysPreserveFocus
    self.refreshLayout()
    
  def refreshLayout(self):
    keyboardHeight = gMyRoot.getKeyboardHeight() if self.editorInput.focus else 0
    height = H - (keyboardHeight + self.menuLayout.height + self.screenMenuLayout.height + self.documentTitleSV.height + topMargin)
    self.documentTitleSV.top = H - topMargin
    self.screenMenuLayout.pos = (0, keyboardHeight)
    self.menuLayout.pos = (0, self.screenMenuLayout.top)
    self.textInputSV.pos = (0, self.menuLayout.top)
    self.textInputSV.size = (W, height)
    self.editorInput.height = max(height, self.editorInput.minimum_height)
    