"""Lekki wrapper do połączeń SQLite z mechanizmem auto-disconnect (idle timeout).

Udostępnia klasę `DatabaseConnection` z metodami:
- `connect()`/`disconnect()` — jawne połączenie/rozłączenie
- `query(sql, params)` — wykonywanie zapytań SQL z prostą obsługą SELECT/INSERT/DML

Wzorzec auto-disconnect: po każdym zapytaniu uruchamiany jest timer, który
automatycznie zamyka połączenie po `idle_timeout` sekundach bezczynności.
Następne zapytanie ponownie nawiąże połączenie.
"""

import sqlite3
import threading


class DatabaseConnection:
    """Menedżer połączenia SQLite z auto-disconnect po okresie bezczynności.

    Parametry:
    - `db_path` — ścieżka do pliku DB (domyślnie `Globals.DB_PATH`)
    - `idle_timeout` — czas w sekundach po którym następuje automatyczne rozłączenie
    """

    _DEFAULT_IDLE_TIMEOUT: int = 2

    def __init__(self, db_path: str | None = None, idle_timeout: int = _DEFAULT_IDLE_TIMEOUT) -> None:
        from globals import Globals
        self.connection: sqlite3.Connection | None = None
        self.db_path: str = db_path if db_path is not None else Globals.DB_PATH
        self.idle_timeout: int = idle_timeout
        self._idle_timer: threading.Timer | None = None

    # ─── Zarządzanie połączeniem ───────────────────────────────────────

    def _reset_idle_timer(self) -> None:
        """Restartuje timer auto-disconnect."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        self._idle_timer = threading.Timer(self.idle_timeout, self._idle_disconnect)
        self._idle_timer.start()

    def _idle_disconnect(self) -> None:
        """Zamyka połączenie gdy timer wygaśnie."""
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error:
                pass
            self.connection = None

    def connect(self) -> None:
        """Nawiązuje połączenie jeśli jeszcze nie istnieje."""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(self.db_path)
            except sqlite3.Error as e:
                # TODO: zastąpić loggerem
                print(f"Database connection error: {e}")

    def disconnect(self) -> None:
        """Zamyka połączenie i zatrzymuje timer."""
        if self._idle_timer is not None:
            self._idle_timer.cancel()
        if self.connection:
            try:
                self.connection.close()
            except sqlite3.Error as e:
                print(f"Database disconnect error: {e}")
            self.connection = None

    # ─── Wykonywanie zapytań ───────────────────────────────────────────

    def query(self, query: str, params: tuple | None = None) -> list | int | None:
        """Wykonuje zapytanie SQL i zwraca wyniki.

        Typ zwracanej wartości zależy od rodzaju zapytania:
        - SELECT → lista wierszy (`list[tuple]`)
        - INSERT → identyfikator nowego wiersza (`lastrowid`)
        - Inne DML (UPDATE/DELETE) → liczba zmienionych wierszy (`rowcount`)
        - Błąd → `None`
        """
        self.connect()
        if not self.connection:
            return None

        # Wykonanie zapytania
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
        except sqlite3.Error as e:
            print(f"Query error: {e}")
            return None

        # Rozpoznanie typu zapytania na podstawie pierwszego słowa SQL
        first_word = query.strip().split()[0].upper()
        result = None

        if first_word == "SELECT":
            result = cursor.fetchall()
        else:
            # DML — zatwierdzamy transakcję i zwracamy odpowiedni wynik
            try:
                self.connection.commit()
                result = cursor.lastrowid if first_word == "INSERT" else cursor.rowcount
            except sqlite3.Error as e:
                print(f"Commit error: {e}")

        self._reset_idle_timer()
        return result
