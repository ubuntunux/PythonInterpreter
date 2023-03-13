import traceback
import Utility as Util
from Utility import *
from PyInterpreter import PyInterpreter

if __name__ == '__main__':
  try:
    gMyRoot.show_debug(False)
    instance = PyInterpreter.PyInterpreter.instance()
    gMyRoot.run( instance )
  except:
    print(traceback.format_exc())


