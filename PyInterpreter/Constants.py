import kivy
import os

directory = os.path.split(__file__)[0]
configFile = os.path.join(directory, "pyinterpreter.cfg")
tempDirectory = os.path.join(directory, "temp")
pythonLogo = os.path.join(directory, "python_logo.png")
defaultFont = kivy.resources.resource_find(os.path.join(directory, "fonts", "DroidSansMonoDotted.ttf"))
tutorialDir = os.path.join(directory, "tutorials")

szConsole = "python console"
szEditor = "python editor"
szTutorial = "python tutorial"
szFileBrowserOpen = "python filebrowser open layout"
szFileBrowserSaveAs = "python filebrowser saveas layout"

topMargin = kivy.metrics.dp(35)
min_space = kivy.metrics.dp(35)

gray = [1, 1, 1, 1]
brightBlue = [1.5, 1.5, 2.0, 2]
darkGray = [0.4, 0.4, 0.4, 2]