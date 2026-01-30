import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Globals import Globals

class Operator_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        name = Globals.PROJECT_NAME
        self.setWindowTitle(name)
        self.UI = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['MAIN_WINDOW'])
    def show_window(self):
        self.UI.show()


app = QApplication(sys.argv)
window = Operator_Window()
window.show_window()
sys.exit(app.exec())