"""Lekki wrapper do połączeń SQLite z mechanizmem auto-disconnect (idle timeout).

Udostępnia klasę `DatabaseConnection` z metodami:
- `connect()`/`disconnect()` — jawne połączenie/rozłączenie
- `query(sql, params)` — wykonywanie zapytań SQL z prostą obsługą SELECT/INSERT/DML

Wzorzec auto-disconnect: po każdym zapytaniu uruchamiany jest timer, który
automatycznie zamyka połączenie po `idle_timeout` sekundach bezczynności.
Następne zapytanie ponownie nawiąże połączenie.

Polityka FK (CRUD): kaskada ``ON DELETE CASCADE`` / ``ON UPDATE CASCADE`` na
relacjach rodzic → dziecko, żeby usuwanie i aktualizacja ID nie kończyły się
``FOREIGN KEY constraint failed``:

- ``zawody_lista`` → ``zawody_konkurencje_link``, ``starty``
- ``konkurencje_lista`` → ``zawody_konkurencje_link``, ``starty``
- ``zawodnicy`` → ``starty``
- ``starty`` → ``strzaly``
"""

import sqlite3
import threading
from collections import defaultdict


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
                nazwisko VARCHAR(50) NOT NULL DEFAULT ''
            )
            """
        )
        DatabaseConnection._migrate_zawodnicy_drop_rocznik(cursor)
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
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE
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
                UNIQUE(zawody_id, nr_serii),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (zawodnik_id) REFERENCES zawodnicy(id) ON UPDATE CASCADE ON DELETE CASCADE
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
                FOREIGN KEY (start_id) REFERENCES starty(id) ON UPDATE CASCADE ON DELETE CASCADE
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

        DatabaseConnection._migrate_starty_unique_nr_per_konkurencja(cursor)
        DatabaseConnection._migrate_starty_unique_nr_per_zawody(cursor)
        DatabaseConnection._migrate_crud_cascade_foreign_keys(cursor)

    @staticmethod
    def _table_sql(cursor: sqlite3.Cursor, table_name: str) -> str:
        cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else ""

    @staticmethod
    def _migrate_crud_cascade_foreign_keys(cursor: sqlite3.Cursor) -> None:
        """Przebudowuje tabele z relacjami FK na kaskadę (CRUD bez błędów constraint)."""
        DatabaseConnection._migrate_zawody_konkurencje_link_cascade(cursor)
        DatabaseConnection._migrate_starty_cascade_fks(cursor)
        DatabaseConnection._migrate_strzaly_cascade_fks(cursor)

    @staticmethod
    def _migrate_zawody_konkurencje_link_cascade(cursor: sqlite3.Cursor) -> None:
        link_sql = DatabaseConnection._table_sql(cursor, "zawody_konkurencje_link")
        if not link_sql:
            return
        compact = "".join(link_sql.split())
        if "ONDELETE CASCADE" in compact and "ONUPDATE CASCADE" in compact:
            return
        if "ON DELETE CASCADE" in link_sql and "ON UPDATE CASCADE" in link_sql:
            return

        cursor.execute("SELECT id, zawody_id, konkurencja_id FROM zawody_konkurencje_link")
        rows = cursor.fetchall()

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE zawody_konkurencje_link_new (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                UNIQUE(zawody_id, konkurencja_id),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        if rows:
            cursor.executemany(
                "INSERT INTO zawody_konkurencje_link_new (id, zawody_id, konkurencja_id) VALUES (?,?,?)",
                rows,
            )
        cursor.execute("DROP TABLE zawody_konkurencje_link")
        cursor.execute("ALTER TABLE zawody_konkurencje_link_new RENAME TO zawody_konkurencje_link")
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_starty_cascade_fks(cursor: sqlite3.Cursor) -> None:
        starty_sql = DatabaseConnection._table_sql(cursor, "starty")
        if not starty_sql:
            return
        if (
            "REFERENCES zawodnicy(id) ON UPDATE CASCADE ON DELETE CASCADE" in starty_sql
            and "REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE" in starty_sql
        ):
            return

        cursor.execute(
            "SELECT id, zawody_id, konkurencja_id, zawodnik_id, nr_serii FROM starty ORDER BY id"
        )
        rows = cursor.fetchall()

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE starty_new (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                zawodnik_id INTEGER NOT NULL,
                nr_serii INTEGER NOT NULL CHECK (nr_serii > 0),
                UNIQUE(zawody_id, nr_serii),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (zawodnik_id) REFERENCES zawodnicy(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        if rows:
            cursor.executemany(
                "INSERT INTO starty_new (id, zawody_id, konkurencja_id, zawodnik_id, nr_serii) VALUES (?,?,?,?,?)",
                rows,
            )
        cursor.execute("DROP TABLE starty")
        cursor.execute("ALTER TABLE starty_new RENAME TO starty")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawodnik_id ON starty(zawodnik_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawody_konkurencja ON starty(zawody_id, konkurencja_id)"
        )
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_strzaly_cascade_fks(cursor: sqlite3.Cursor) -> None:
        strzaly_sql = DatabaseConnection._table_sql(cursor, "strzaly")
        if not strzaly_sql:
            return
        if "ON UPDATE CASCADE ON DELETE CASCADE" in strzaly_sql:
            return

        cursor.execute("SELECT id, start_id, nr_strzalu, punkty FROM strzaly ORDER BY id")
        rows = cursor.fetchall()

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE strzaly_new (
                id INTEGER PRIMARY KEY,
                start_id INTEGER NOT NULL,
                nr_strzalu INTEGER NOT NULL CHECK (nr_strzalu > 0),
                punkty INTEGER NOT NULL CHECK (punkty >= 0),
                UNIQUE(start_id, nr_strzalu),
                FOREIGN KEY (start_id) REFERENCES starty(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        if rows:
            cursor.executemany(
                "INSERT INTO strzaly_new (id, start_id, nr_strzalu, punkty) VALUES (?,?,?,?)",
                rows,
            )
        cursor.execute("DROP TABLE strzaly")
        cursor.execute("ALTER TABLE strzaly_new RENAME TO strzaly")
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_zawodnicy_drop_rocznik(cursor: sqlite3.Cursor) -> None:
        """Stare bazy: usuwa kolumnę ``rocznik`` z tabeli ``zawodnicy`` (przebudowa tabeli, zachowanie ``id``)."""
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='zawodnicy'")
        row = cursor.fetchone()
        if not row or not row[0]:
            return
        if "rocznik" not in row[0].lower():
            return

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE zawodnicy_new (
                id INTEGER PRIMARY KEY,
                imie VARCHAR(50) NOT NULL DEFAULT '',
                nazwisko VARCHAR(50) NOT NULL DEFAULT ''
            )
            """
        )
        cursor.execute(
            "INSERT INTO zawodnicy_new (id, imie, nazwisko) SELECT id, imie, nazwisko FROM zawodnicy"
        )
        cursor.execute("DROP TABLE zawodnicy")
        cursor.execute("ALTER TABLE zawodnicy_new RENAME TO zawodnicy")
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_starty_unique_nr_per_konkurencja(cursor: sqlite3.Cursor) -> None:
        """Stare bazy: UNIQUE po (zawody, konkurencja, zawodnik, nr) — pośredni krok: nr unikalny w obrębie konkurencji na zawodach.

        Przenumerowuje ``nr_serii`` na 1..N wg ``id`` w każdej grupie (zawody_id, konkurencja_id), bez zmiany ``id`` (FK z ``strzaly``).
        """
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='starty'")
        row = cursor.fetchone()
        if not row or not row[0]:
            return
        compact = "".join(row[0].split())
        old_u = "UNIQUE(zawody_id,konkurencja_id,zawodnik_id,nr_serii)"
        new_u = "UNIQUE(zawody_id,konkurencja_id,nr_serii)"
        if new_u in compact and old_u not in compact:
            return
        if old_u not in compact:
            return

        cursor.execute(
            "SELECT id, zawody_id, konkurencja_id, zawodnik_id, nr_serii FROM starty ORDER BY zawody_id, konkurencja_id, id"
        )
        fetched = cursor.fetchall()
        by_zk: dict[tuple[int, int], list[tuple[int, int, int, int, int]]] = defaultdict(list)
        for rid, zid, kid, zawid, nr in fetched:
            by_zk[(zid, kid)].append((rid, zid, kid, zawid, nr))

        rebuilt: list[tuple[int, int, int, int, int]] = []
        for _key, group in by_zk.items():
            group_sorted = sorted(group, key=lambda t: t[0])
            for new_nr, (rid, zid, kid, zawid, _old_nr) in enumerate(group_sorted, start=1):
                rebuilt.append((rid, zid, kid, zawid, new_nr))

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE starty_new (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                zawodnik_id INTEGER NOT NULL,
                nr_serii INTEGER NOT NULL CHECK (nr_serii > 0),
                UNIQUE(zawody_id, konkurencja_id, nr_serii),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (zawodnik_id) REFERENCES zawodnicy(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        cursor.executemany(
            "INSERT INTO starty_new (id, zawody_id, konkurencja_id, zawodnik_id, nr_serii) VALUES (?,?,?,?,?)",
            rebuilt,
        )
        cursor.execute("DROP TABLE starty")
        cursor.execute("ALTER TABLE starty_new RENAME TO starty")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawodnik_id ON starty(zawodnik_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawody_konkurencja ON starty(zawody_id, konkurencja_id)"
        )
        cursor.execute("PRAGMA foreign_keys = ON")

    @staticmethod
    def _migrate_starty_unique_nr_per_zawody(cursor: sqlite3.Cursor) -> None:
        """Nr serii wspólny dla całego obiektu zawodów (nie osobno per konkurencja).

        Przenumerowuje ``nr_serii`` na 1..N wg ``id`` w każdej grupie ``zawody_id``, bez zmiany ``id`` (FK z ``strzaly``).
        """
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='starty'")
        row = cursor.fetchone()
        if not row or not row[0]:
            return
        compact = "".join(row[0].split())
        per_konk_u = "UNIQUE(zawody_id,konkurencja_id,nr_serii)"
        per_zawody_u = "UNIQUE(zawody_id,nr_serii)"
        if per_zawody_u in compact and per_konk_u not in compact:
            return
        if per_konk_u not in compact:
            return

        cursor.execute(
            "SELECT id, zawody_id, konkurencja_id, zawodnik_id, nr_serii FROM starty ORDER BY zawody_id, id"
        )
        fetched = cursor.fetchall()
        by_zawody: dict[int, list[tuple[int, int, int, int, int]]] = defaultdict(list)
        for rid, zid, kid, zawid, nr in fetched:
            by_zawody[zid].append((rid, zid, kid, zawid, nr))

        rebuilt: list[tuple[int, int, int, int, int]] = []
        for _zid, group in by_zawody.items():
            group_sorted = sorted(group, key=lambda t: t[0])
            for new_nr, (rid, zid, kid, zawid, _old_nr) in enumerate(group_sorted, start=1):
                rebuilt.append((rid, zid, kid, zawid, new_nr))

        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute(
            """
            CREATE TABLE starty_new (
                id INTEGER PRIMARY KEY,
                zawody_id INTEGER NOT NULL,
                konkurencja_id INTEGER NOT NULL,
                zawodnik_id INTEGER NOT NULL,
                nr_serii INTEGER NOT NULL CHECK (nr_serii > 0),
                UNIQUE(zawody_id, nr_serii),
                FOREIGN KEY (zawody_id) REFERENCES zawody_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (konkurencja_id) REFERENCES konkurencje_lista(id) ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (zawodnik_id) REFERENCES zawodnicy(id) ON UPDATE CASCADE ON DELETE CASCADE
            )
            """
        )
        cursor.executemany(
            "INSERT INTO starty_new (id, zawody_id, konkurencja_id, zawodnik_id, nr_serii) VALUES (?,?,?,?,?)",
            rebuilt,
        )
        cursor.execute("DROP TABLE starty")
        cursor.execute("ALTER TABLE starty_new RENAME TO starty")
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawodnik_id ON starty(zawodnik_id)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_starty_zawody_konkurencja ON starty(zawody_id, konkurencja_id)"
        )
        cursor.execute("PRAGMA foreign_keys = ON")

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
            cursor.execute("PRAGMA foreign_keys = ON")
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
