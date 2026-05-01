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
        self._schema_initialized: bool = False

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
                self._schema_initialized = False
                self._configure_connection()
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
            self._schema_initialized = False

    def _configure_connection(self) -> None:
        """Konfiguruje połączenie i dba o wymagane tabele aplikacji."""
        if not self.connection:
            return
        try:
            cursor = self.connection.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            if not self._schema_initialized:
                self._ensure_required_tables(cursor)
                self.connection.commit()
                self._schema_initialized = True
        except sqlite3.Error as e:
            print(f"Database configuration error: {e}")

    @staticmethod
    def _ensure_required_tables(cursor: sqlite3.Cursor) -> None:
        """Tworzy wymagane tabele, jeśli jeszcze nie istnieją."""
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS konkurencje_lista (
                id INTEGER PRIMARY KEY,
                nazwa VARCHAR(50) NOT NULL,
                ilosc_strzalow INTEGER NOT NULL CHECK (ilosc_strzalow > 0),
                UNIQUE(nazwa)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS zawodnicy (
                id INTEGER PRIMARY KEY,
                imie VARCHAR(50) NOT NULL DEFAULT '',
                nazwisko VARCHAR(50) NOT NULL DEFAULT '',
                rocznik VARCHAR(50) NOT NULL DEFAULT ''
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS zawody_lista (
                id INTEGER PRIMARY KEY,
                nazwa VARCHAR(50) NOT NULL DEFAULT '',
                data VARCHAR(50) NOT NULL DEFAULT '',
                godzina VARCHAR(50) NOT NULL DEFAULT ''
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS zawody_konkurencje_link (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                UNIQUE(zawody_id, konkurencja_id),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE NO ACTION ON DELETE NO ACTION,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE NO ACTION ON DELETE NO ACTION
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS starty (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                zawodnik_id INTEGER NOT NULL,
                nr_serii INTEGER NOT NULL CHECK (nr_serii > 0),
                UNIQUE(zawody_id, konkurencja_id, zawodnik_id, nr_serii),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE NO ACTION ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE NO ACTION ON DELETE RESTRICT,
                FOREIGN KEY (zawodnik_id) REFERENCES zawodnicy(id) ON UPDATE NO ACTION ON DELETE RESTRICT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS strzaly (
                id INTEGER PRIMARY KEY,
                start_id INTEGER NOT NULL,
                nr_strzalu INTEGER NOT NULL CHECK (nr_strzalu > 0),
                punkty INTEGER NOT NULL CHECK (punkty >= 0),
                UNIQUE(start_id, nr_strzalu),
                FOREIGN KEY (start_id) REFERENCES starty(id) ON UPDATE NO ACTION ON DELETE CASCADE
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_starty_zawodnik_id ON starty(zawodnik_id)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_starty_zawody_konkurencja ON starty(zawody_id, konkurencja_id)
            """
        )

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
