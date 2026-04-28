import sqlite3
import threading


class Database_connection:
    def __init__(self, db_path=None, idle_timeout=2):
        from Globals import Globals
        self.connection = None
        self.db_path = db_path if db_path is not None else Globals.DB_PATH
        self.idle_timeout = idle_timeout
        self._idle_timer = None

    def _reset_idle_timer(self):
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        self._idle_timer = threading.Timer(self.idle_timeout, self._idle_disconnect)
        self._idle_timer.start()

    def _idle_disconnect(self):
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error:
                pass
            self.connection = None

    def connect(self):
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
            except sqlite3.Error as e:
                print(f"Database connection error: {e}")

    def disconnect(self):
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                print(f"Database disconnect error: {e}")
            self.connection = None

    def query(self, query, params=None):
        self.connect()
        if not self.connection:
            return None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
        except sqlite3.Error as e:
            print(f"Query error: {e}")
            return None

        first_word = query.strip().split()[0].upper()
        result = None
        if first_word == "SELECT":
            result = cursor.fetchall()
        else:
            try:
                self.connection.commit()
                result = cursor.lastrowid if first_word == "INSERT" else cursor.rowcount
            except sqlite3.Error as e:
                print(f"Commit error: {e}")
        self._reset_idle_timer()
        return result

