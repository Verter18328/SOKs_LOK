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
                print("Disconnected from database (idle timeout)")
            except sqlite3.Error:
                pass
            self.connection = None

    def connect(self):
        """Establish a connection to the SQLite database if not already connected."""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
                print("Connected to database")
            except sqlite3.Error as e:
                print(f"An error occurred while connecting to the database: {e}")

    def disconnect(self):
        """Close the connection to the SQLite database."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        if self.connection:
            try:
                self.connection.close()
                print("Disconnected from database")
            except sqlite3.Error as e:
                print(f"An error occurred while disconnecting from the database: {e}")
            self.connection = None

    def query(self, query, params=None):
        """Execute a query on the SQLite database."""
        self.connect()
        if not self.connection:
            print("No active database connection")
            return None
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
        except sqlite3.Error as e:
            print(f"An error occurred while executing the query: {e}")
            return None
        result = None
        first_word = query.strip().split()[0].upper()
        if first_word == "SELECT":
            result = cursor.fetchall()
        elif first_word == "INSERT":
            try:
                self.connection.commit()
                result = cursor.lastrowid
            except sqlite3.Error as e:
                print(f"An error occurred while committing the transaction: {e}")
                result = None
        else:
            try:
                self.connection.commit()
                result = cursor.rowcount
            except sqlite3.Error as e:
                print(f"An error occurred while committing the transaction: {e}")
                result = None
        self._reset_idle_timer()
        return result
    


