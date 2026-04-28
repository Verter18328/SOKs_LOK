import sys

from PySide6.QtWidgets import QApplication, QDialog, QMainWindow
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QIcon

from Globals import Globals
Globals.setMainDirectory()
import Resources.resources_rc
from Signals import Signals_operator_window, Signals_new_competition_dialog, Signals_kreator_konkurencji_dialog


class Kreator_konkurencji_dialog(QDialog):
    def __init__(self, global_config=None, parent=None):
        super().__init__(parent)
        global_config = global_config if global_config is not None else Globals()
        self.UI = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT['KREATOR_KONKURENCJI_DIALOG'])
        self.UI.setWindowTitle("Kreator konkurencji")
        self.UI.setWindowIcon(QIcon(global_config.RESOURCES_PATHS_DICT['LOGO_IMAGE']))
        self.signals = Signals_kreator_konkurencji_dialog(self.UI, parent)

    def show_dialog(self):
        self.UI.show()


class Nowe_zawody_dialog(QDialog):
    def __init__(self, global_config=None, parent=None):
        super().__init__(parent)
        global_config = global_config if global_config is not None else Globals()
        self.UI = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT['NEW_COMPETITION_DIALOG'])
        self.UI.setWindowTitle("Stwórz nowe zawody")
        self.UI.setWindowIcon(QIcon(global_config.RESOURCES_PATHS_DICT['LOGO_IMAGE']))
        timestamp = QDateTime.currentDateTime()
        self.UI.dateTimeEdit_data_zawodow.setDateTime(timestamp)
        self.UI.dateTimeEdit_data_zawodow.setMinimumDateTime(timestamp)
        self.parent_window = parent
        self.signals = Signals_new_competition_dialog(self.UI, self.parent_window)

    def show_dialog(self):
        self.UI.show()


class Operator_Window(QMainWindow):
    def __init__(self, global_config=None):
        super().__init__()
        global_config = global_config if global_config is not None else Globals()
        self.UI = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT['OPERATOR_WINDOW'])
        self.UI.setWindowTitle(global_config.PROJECT_NAME)
        self.UI.setWindowIcon(QIcon(global_config.RESOURCES_PATHS_DICT['LOGO_IMAGE']))
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageTitle)
        self.signals = Signals_operator_window(self.UI)

    def show_window(self):
        self.UI.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Operator_Window()
    window.show_window()
    sys.exit(app.exec())