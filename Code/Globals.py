import os
from Code.DatabaseConnection import DatabaseConnection


class Globals:
    DB_PATH = os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'Database_Files', 'Database.db')
    )
    UI_PATHS_DICT = {}
    def __init__(self):
        self.database = DatabaseConnection()
