import os
import sys
from DatabaseConnection import Database_connection
from PySide6.QtUiTools import QUiLoader


class Globals:
    DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'Database_Files', 'Database.db')
    )
    PROJECT_NAME = 'SOKs_LOK'
    UI_LOADER = QUiLoader()
    UI_PATHS_DICT = {
        'OPERATOR_WINDOW': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'OperatorWindow.ui')
        ),
        'NEW_COMPETITION_DIALOG': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'NoweZawodyDialog.ui')
        )
    }
    RESOURCES_PATHS_DICT = {
        'LOGO_IMAGE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Resources', 'logo.jpeg')
        )
    }
    KONKURENCJE = {
            'kbks_50m_stojąc': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji stojącej',
            'kbks_50m_leżąc': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji leżącej',
            'karabinek_pneumatyczny_10m_stojąc': 'Strzelanie z karabinka pneumatycznego 10m w pozycji stojącej',
            'pistolet_pneumatyczny_10m_stojąc': 'Strzelanie z pistoletu pneumatycznego 10m w pozycji stojącej',
            'pistolet_bocznyZapłon_25m_stojąc': 'Strzelanie z pistoletu bocznego zapłonu 25m w pozycji stojącej',
            'kbks_50m_zapadki': 'Strzelanie z karabinka bocznego zapłonu 50m do zapadek',
            'karabinek_pneumatyczny_10m_zapadki': 'Strzelanie z karabinka pneumatycznego 10m do zapadek'
    }
    def __init__(self):
        self.database = Database_connection()
    
    @staticmethod
    def setMainDirectory():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
