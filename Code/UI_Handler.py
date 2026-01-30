from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Code.Globals import Globals

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        name = Globals.PROJECT_NAME
        self.setWindowTitle(name)
        self.UI = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['MAIN_WINDOW'])