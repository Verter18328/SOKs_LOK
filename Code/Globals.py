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
    @classmethod
    def load_competitions(cls):
        query = "select * from konkurencje"
        results = cls().database.query(query)
        if results:
            for row in results:
                id = row[0]
                key = row[1]
                value = row[2]
                cls.KONKURENCJE[key] = value
    
    KONKURENCJE = {}
    
    def __init__(self):
        self.database = Database_connection()
    
    @staticmethod
    def setMainDirectory():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Automatycznie załaduj konkurencje przy imporcie modułu
Globals.load_competitions()

