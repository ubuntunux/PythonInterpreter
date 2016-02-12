import Utility as Util
from Utility import *

from Constants import *
from collections import OrderedDict

#---------------------#
# CLASS : Tutorial layout class
#---------------------#    
class TutorialLayout:
  def __init__(self, ui):
    self.ui = ui
    self.tutorialMap = OrderedDict({})
    layout_height = 0
    
    self.screen = Screen(name=szTutorial)
    
    # screen menu layout
    self.screenMenuLayout = BoxLayout(orientation="horizontal", size_hint=(1, None), height="35dp")
    btn_console = Button(text="Console", background_color=[1.5,0.8,0.8,2])
    btn_editor = Button(text="Code Editor", background_color=[0.8,1.5,0.8,2])
    btn_tutorial = Button(text="Python Tutorial", background_color=[0.8,0.8,1.5,2])
    btn_console.bind(on_release=lambda inst:self.ui.setMode(szConsole))
    btn_editor.bind(on_release=lambda inst:self.ui.setMode(szEditor))
    self.screenMenuLayout.add_widget(btn_console)
    self.screenMenuLayout.add_widget(btn_editor)
    self.screenMenuLayout.add_widget(btn_tutorial)
    self.screen.add_widget(self.screenMenuLayout)
    
    self.tutorialSV = ScrollView(size_hint=(1, None), size=(W,H - self.screenMenuLayout.size[1]), pos=(0, self.screenMenuLayout.top))
    with self.tutorialSV.canvas.before:
      Color(0.1, 0.1, 0.2, 1)
      Rectangle(size=WH)
    self.tutorialLayout = BoxLayout(orientation="vertical", size_hint_y = None)
    
    self.tutorialSV.add_widget(self.tutorialLayout)
    self.screen.add_widget(self.tutorialSV)
    
    # add title header
    image = Image(source=pythonLogo, allow_stretch=True, keep_ratio=True, size_hint_x=None)
    label_Title = Label(text = "Python Tutorials", font_size="30dp", bold=True, color=[1.0,0.7,0.4,1])
    titleLayout = BoxLayout(orientation="horizontal", padding=[metrics.dp(20),0,0,0], size_hint=(1, 50.0/30.0)) 
    titleLayout.add_widget(image)
    titleLayout.add_widget(label_Title)
    self.tutorialLayout.add_widget(titleLayout)
    layout_height += metrics.dp(50)
    
    # add python tutorial url
    self.tutorialLayout.add_widget(Label(text="Excepts from https://docs.python.org/2.7/tutorial", font_size="12dp", color=[1.0,0.85,0.7,1]))
    layout_height += metrics.dp(30)
    
    # add my comment
    self.tutorialLayout.add_widget(Label(text="I will update more tutorial.", font_size="15dp", color=[1.0,0.85,0.7,1]))
    self.tutorialLayout.add_widget(Label(text=" ", font_size="12dp"))
    layout_height += metrics.dp(50)
    
    # create tutorial buttons  
    for dirpath, dirnames, filenames in os.walk(tutorialDir):
      # add category label
      if filenames:
        label_category = Label(text = os.path.split(dirpath)[-1], font_size="18dp", halign="left", bold=True, color=[1.0,0.85,0.7,1], size_hint_y=40.0/30.0)
        self.tutorialLayout.add_widget(label_category)
        layout_height += metrics.dp(40)
      # add tutorials
      for filename in filenames:
        # load tutorial file
        f = open(os.path.join(dirpath, filename), "r")
        lines = list(f)
        f.close()
        desc = "".join(lines)
        # add a button
        btn = Button(text=desc[:desc.find("\n")], font_size="15dp", size_hint_y=1, background_color=[0.8, 0.8, 1.5, 1])
        btn.bind(on_release = self.chooseTutorial)
        self.tutorialMap[btn] = desc
        self.tutorialLayout.add_widget(btn)
        layout_height += metrics.dp(30)
    # refresh height
    self.tutorialLayout.height = layout_height
  
  def chooseTutorial(self, btn):
    if btn in self.tutorialMap:
      self.ui.clearOutput()
      desc = self.tutorialMap[btn]
      self.ui.displayText("\n-------------------------", 1)
      # split desc by line
      lines = desc.split("\n")
      # show title
      if lines:
        self.ui.displayText("Tutorial : " + lines.pop(0), 1)
      # show tutorial body
      textList = []
      isInCode = False
      for line in lines:
        if line.startswith("[code]"):
          self.ui.displayText("\n".join(textList), 1)
          textList = []
        elif line.startswith("[/code]"):
          self.ui.displayText("\n".join(textList), 1, background_color=(0.5, 0.5, 1, 0.35))
          textList = []
        else:
          textList.append(line)
      else:
        if isInCode:
          self.ui.displayText("\n".join(textList), 1, background_color=(0.5, 0.5, 1, 0.35))
        else:
          self.ui.displayText("\n".join(textList), 1)
      # end of tutorial body
      self.ui.displayText("------------------------\n\nLet's try this!!\n", 1)
      # next, prev tutorial buttons
      padding = kivy.metrics.dp(20)
      fontSize = kivy.metrics.dp(14)
      spacing = kivy.metrics.dp(20)
      layout = BoxLayout(size_hint=(1,None), height="70dp", spacing=spacing, padding=[0, padding, 0, padding])
      maxCharacter = int(math.ceil((W-spacing) / fontSize)) - 2
      buttons = self.tutorialMap.keys()
      curIndex = buttons.index(btn)
      btnColor = [0.8, 0.8, 1.5, 1]
      btn_prev = Button(text="----", font_size=fontSize, background_color=btnColor)
      btn_next = Button(text="----", font_size=fontSize, background_color=btnColor)
      if curIndex > 0:
        btn_prevTutorial = buttons[curIndex - 1]
        if len(btn_prevTutorial.text) >= maxCharacter:
          btn_prev.text = btn_prevTutorial.text[:maxCharacter-3] + "..."
        else:
          btn_prev.text = btn_prevTutorial.text
        btn_prev.bind(on_release = lambda inst:self.chooseTutorial(btn_prevTutorial))
      if curIndex < len(buttons) - 1:
        btn_nextTutorial = buttons[curIndex + 1]
        if len(btn_nextTutorial.text) >= maxCharacter:  
          btn_next.text = btn_nextTutorial.text[:maxCharacter-3] + "..."
        else:
          btn_next.text = btn_nextTutorial.text
        btn_next.bind(on_release = lambda inst:self.chooseTutorial(btn_nextTutorial))
      layout.add_widget(btn_prev)
      layout.add_widget(btn_next)
      self.ui.outputLayout_add_widget(layout)
      self.ui.setMode(szConsole)
      
  def touchPrev(self):
    self.ui.setMode(szConsole)
      