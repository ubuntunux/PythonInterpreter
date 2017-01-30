# PythonInterpreter

GooglePlay : https://play.google.com/store/apps/details?id=enurisoft.com.pythoninterpreter
SourceCode : https://github.com/terrorgun/Python_Interpreter

This is Python interpreter for Android.  
This is Python REPL.  
This is Python IDE and contain some tutorial.  

This offers a great learning experience for Python beginners.  
It is written in python using the Kivy framework. (http://kivy.org)  
Kivy is cross platform greate NUI framwork.  

You can test kivy like this.

'''
  # import kivy modules
  import kivy
  from kivy.core.window import Window
  from kivy.uix.button import Button

  # get root
  root = Window.get_parent_window()

  # creat button
  btn = Button(text="button test", pos=(200,500), size_hint=(None, None), size=(300,150))

  # show button
  root.add_widget(btn)
'''
