import datetime
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from Globals import Globals
Globals.setMainDirectory()
import Resources.resources_rc
from Signals import Signals_operator_window, Signals_new_competition_dialog

class Nowe_zawody_dialog(QDialog):
    def __init__(self, global_config=None, parent=None):
        super().__init__(parent)
        global_config = global_config if global_config is not None else Globals()
        self.UI = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT['NEW_COMPETITION_DIALOG'])
        self.UI.setWindowTitle("Stwórz nowe zawody")
        self.UI.setWindowIcon(QIcon(global_config.RESOURCES_PATHS_DICT['LOGO_IMAGE']))
        self.KONKURENCJE = global_config.KONKURENCJE
        self.init_konkurencje(self.UI.comboBox_konkurencja1)
        for i in range(len(self.KONKURENCJE) - 1):
            layout = QHBoxLayout()

            label = QLabel('<b>Konkurencja: </b>')
            font = label.font()
            font.setPointSize(12)
            label.setFont(font)

            comboBox = QComboBox()
            size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            comboBox.setSizePolicy(size_policy)
            self.init_konkurencje(comboBox)

            layout.addWidget(label)
            layout.addWidget(comboBox)
            self.UI.inputs_layout.addLayout(layout)
            label.hide()
            comboBox.hide()
            setattr(self.UI, f'konkurencja_layout{i + 2}', layout)
            setattr(self.UI, f'label_{i + 2}', label)
            setattr(self.UI, f'comboBox_konkurencja{i + 2}', comboBox)

            
        timestamp = QDateTime.currentDateTime()
        self.UI.dateTime_input.setDateTime(timestamp)
        self.UI.dateTime_input.setMinimumDateTime(timestamp)
        self.signals = Signals_new_competition_dialog(self.UI)


    def init_konkurencje(self, comboBox):
        comboBox.addItem("Puste")
        comboBox.addItems(list(self.KONKURENCJE.values()))
        

    def show_dialog(self):
        self.UI.show()

class Operator_Window(QMainWindow):
    def __init__(self, global_config=None,):
        super().__init__()
        global_config = global_config if global_config is not None else Globals()
        name = global_config.PROJECT_NAME
        logo = global_config.RESOURCES_PATHS_DICT['LOGO_IMAGE']
        self.UI = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT['OPERATOR_WINDOW'])
        self.UI.setWindowTitle(name)
        self.UI.setWindowIcon(QIcon(logo))
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageTitle)
        self.signals = Signals_operator_window(self.UI)
    def show_window(self):
        self.UI.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Operator_Window()
    window.show_window()
    sys.exit(app.exec())