"""Lekki wrapper do połączeń SQLite z mechanizmem auto-disconnect (idle timeout).

Ten moduł udostępnia klasę `Database_connection` z metodami:
- `connect()`/`disconnect()` — jawne połączenie/rozłączenie
- `query(sql, params)` — wykonywanie zapytań SQL z prostą obsługą SELECT/INSERT/DML

Klasa używana jest w całej aplikacji jako punkt dostępu do bazy.
"""

import sqlite3
import threading


class Database_connection:
    """Prosty menedżer połączenia SQLite z auto-disconnect po okresie bezczynności.

    Parametry:
    - `db_path` — ścieżka do pliku DB (domyślnie `Globals.DB_PATH`)
    - `idle_timeout` — czas w sekundach po którym następuje automatyczne rozłączenie
    """

    def __init__(self, db_path=None, idle_timeout=2):
        from Globals import Globals
        self.connection = None
        self.db_path = db_path if db_path is not None else Globals.DB_PATH
        self.idle_timeout = idle_timeout
        self._idle_timer = None

    def _reset_idle_timer(self):
        """Restartuje timer auto-disconnect."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        self._idle_timer = threading.Timer(self.idle_timeout, self._idle_disconnect)
        self._idle_timer.start()

    def _idle_disconnect(self):
        """Zamyka połączenie gdy timer wygaśnie."""
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error:
                pass
            self.connection = None

    def connect(self):
        """Nawiązuje połączenie jeśli jeszcze nie istnieje."""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
            except sqlite3.Error as e:
                # Logowanie błędu — w przyszłości zastąpić loggerem
                print(f"Database connection error: {e}")

    def disconnect(self):
        """Zamyka połączenie i zatrzymuje timer."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                print(f"Database disconnect error: {e}")
            self.connection = None

    def query(self, query, params=None):
        """Wykonuje zapytanie SQL i zwraca wyniki.

        - SELECT zwraca listę wierszy
        - INSERT zwraca `lastrowid`
        - Inne DML zwracają `rowcount`
        """
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

