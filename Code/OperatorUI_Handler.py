import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Globals import Globals
Globals.setMainDirectory()
import Resources.resources_rc

class Operator_Window(QMainWindow):
    def __init__(self):
        super().__init__()
        name = Globals.PROJECT_NAME
        logo = Globals.RESOURCES_PATHS_DICT['LOGO_IMAGE']
        self.UI = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['MAIN_WINDOW'])
        self.UI.setWindowTitle(name)
        self.UI.setWindowIcon(QIcon(logo))
    def show_window(self):
        self.UI.show()


app = QApplication(sys.argv)
window = Operator_Window()
window.show_window()
sys.exit(app.exec())