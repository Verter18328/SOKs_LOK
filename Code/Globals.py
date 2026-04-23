import os
import sys
from DatabaseConnection import Database_connection
from PySide6.QtUiTools import QUiLoader
import datetime

# TODO: 
# - Dodać creator zawodów !!!!!!!!!!!!
# - Dodać wyszukiwanie zawodów po nazwie i dacie w 'Zarządzaj zawodami'
# - Obsługa wyników zawodów (tworzenie tabel dla zawodów w db(może inne rozwiązanie???))
# - Ustawić maksymalną ilość wyników wyszukiwania zawodników i dodać przycisk 'Pokaż więcej wyników'
# - Dodać dynamiczny rozmiar spacera w zależności od ilości wyników wyszukiwania zawodników
# - Naprawić display zawodów w 'Zarządzaj zawodami' (jakoś tak kurwa dziwnie to wygląda)
# - Obsługa dogrywek



class Globals:
    DATE_FORMAT_PY = '%d/%m/%Y'
    DATE_FORMAT_QT = 'dd/MM/yyyy'
    TIME_FORMAT_PY = '%H:%M:%S'
    TIME_FORMAT_QT = 'HH:mm:ss'
    TIMESTAMP_FORMAT_PY = '%H:%M:%S %d/%m/%Y'
    TIMESTAMP_FORMAT_QT = 'HH:mm:ss dd/MM/yyyy'
    TODAY_DATE = datetime.datetime.now().strftime(DATE_FORMAT_PY)

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
        ),
        'KREATOR_KONKURENCJI_DIALOG': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Ui_Files', 'KreatorKonkurencji.ui')
        )
    }
    RESOURCES_PATHS_DICT = {
        'LOGO_IMAGE': os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'Resources', 'logo.jpeg')
        )
    }
    


    
    def __init__(self):
        self.database = Database_connection()
    
    @staticmethod
    def setMainDirectory():
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

    @staticmethod
    def set_timestamp_format(timestamp):
        try:
            timestamp_obj = datetime.datetime.strptime(timestamp, Globals.TIMESTAMP_FORMAT_PY)
            return timestamp_obj.strftime(Globals.TIMESTAMP_FORMAT_PY)
        except ValueError:
            timestamp_obj = datetime.datetime.strptime(timestamp, Globals.TIMESTAMP_FORMAT_QT)
            return timestamp_obj.strftime(Globals.TIMESTAMP_FORMAT_QT)
    @staticmethod
    def set_date_format(date):
        try:
            date_obj = datetime.datetime.strptime(date, Globals.DATE_FORMAT_PY)
            return date_obj.strftime(Globals.DATE_FORMAT_PY)
        except ValueError:
            date_obj = datetime.datetime.strptime(date, Globals.DATE_FORMAT_QT)
            return date_obj.strftime(Globals.DATE_FORMAT_QT)
    @staticmethod
    def set_time_format(time):
        try:
            time_obj = datetime.datetime.strptime(time, Globals.TIME_FORMAT_PY)
            return time_obj.strftime(Globals.TIME_FORMAT_PY)
        except ValueError:
            time_obj = datetime.datetime.strptime(time, Globals.TIME_FORMAT_QT)
            return time_obj.strftime(Globals.TIME_FORMAT_QT)
    
    





