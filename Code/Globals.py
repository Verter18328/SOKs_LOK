import os
from Code.DatabaseConnection import DatabaseConnection
from PySide6.QtUiTools import QUiLoader


class Globals:
    DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'Database_Files', 'Database.db')
    )
    PROJECT_NAME = 'SOKs_LOK'
    UI_LOADER = QUiLoader()
    UI_PATHS_DICT = {
        'MAIN_WINDOW': None
    }
    def __init__(self):
        self.database = DatabaseConnection()
