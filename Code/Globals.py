import os
import sys
from DatabaseConnection import Database_connection
from PySide6.QtUiTools import QUiLoader
import datetime


class Globals:
    DATE_FORMAT = '%d-%m-%Y'
    TIME_FORMAT = '%H:%M:%S'
    TODAY_DATE = datetime.datetime.now().strftime(DATE_FORMAT)
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
        ),
        '5_SHOOTS_TABLE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'Tabelka5Strzałów.ui')
        ),
        '10_SHOOTS_TABLE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'Tabelka10Strzałów.ui')
        ),
        'ZAPADKI_TABLE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'TabelkaZapadki.ui')
        )
    }
    RESOURCES_PATHS_DICT = {
        'LOGO_IMAGE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Resources', 'logo.jpeg')
        )
    }
    KONKURENCJE = {
            'kbks_50m_stojąc_10strz': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji stojącej - 10 strzałów',
            'kbks_50m_stojąc_5strz': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji stojącej - 5 strzałów',
            'kbks_50m_leżąc_10strz': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji leżącej - 10 strzałów',
            'kbks_50m_leżąc_5strz': 'Strzelanie z karabinka bocznego zapłonu 50m w pozycji leżącej - 5 strzałów',
            'karabinek_pneumatyczny_10m_stojąc_10strz': 'Strzelanie z karabinka pneumatycznego 10m w pozycji stojącej - 10 strzałów',
            'karabinek_pneumatyczny_10m_stojąc_5strz': 'Strzelanie z karabinka pneumatycznego 10m w pozycji stojącej - 5 strzałów',
            'pistolet_pneumatyczny_10m_stojąc_10strz': 'Strzelanie z pistoletu pneumatycznego 10m w pozycji stojącej - 10 strzałów',
            'pistolet_pneumatyczny_10m_stojąc_5strz': 'Strzelanie z pistoletu pneumatycznego 10m w pozycji stojącej - 5 strzałów',
            'pistolet_bocznyZapłon_25m_stojąc_10strz': 'Strzelanie z pistoletu bocznego zapłonu 25m w pozycji stojącej - 10 strzałów',
            'pistolet_bocznyZapłon_25m_stojąc_5strz': 'Strzelanie z pistoletu bocznego zapłonu 25m w pozycji stojącej - 5 strzałów',
            'kbks_50m_zapadki': 'Strzelanie z karabinka bocznego zapłonu 50m do zapadek',
            'karabinek_pneumatyczny_10m_zapadki': 'Strzelanie z karabinka pneumatycznego 10m do zapadek'
    }
    def __init__(self):
        self.database = Database_connection()
    
    @staticmethod
    def setMainDirectory():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
