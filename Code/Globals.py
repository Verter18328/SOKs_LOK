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
    KONKURENCJE = [
            'kbks_50m_stojąc',
            'kbks_50m_leżąc',
            'karabinek_pneumatyczny_10m_stojąc',
            'pistolet_pneumatyczny_10m_stojąc',
            'pistolet_bocznyZapłon_25m_stojąc',
            'kbks_50m_zapadki',
            'karabinek_pneumatyczny_10m_zapadki'
        ]
    def __init__(self):
        self.database = Database_connection()
    
    @staticmethod
    def setMainDirectory():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
