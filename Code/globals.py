"""Moduł konfiguracji globalnej aplikacji SOKs_LOK.

Zawiera klasę `Globals` przechowującą:
- formaty dat/czasu używane w całej aplikacji
- ścieżki do plików UI i zasobów
- metody pomocnicze do parsowania i formatowania dat
"""

import os
import sys
import datetime

from database_connection import DatabaseConnection
from PySide6.QtUiTools import QUiLoader


def _dev_project_root() -> str:
    """Katalog główny repozytorium (uruchomienie z kodu źródłowego)."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _frozen_exe_dir() -> str:
    """Folder zawierający `SOKs_LOK.exe` (onedir)."""
    return os.path.dirname(os.path.abspath(sys.executable))


def _bundled_assets_root() -> str:
    """Katalog z `Ui_Files` i `Resources` — w PyInstaller 6 zwykle `_internal`, nie obok `.exe`."""
    if not getattr(sys, "frozen", False):
        return _dev_project_root()
    marker = os.path.join("Ui_Files", "OperatorWindow.ui")
    candidates: list[str] = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates.append(meipass)
    exe_dir = _frozen_exe_dir()
    candidates.append(os.path.join(exe_dir, "_internal"))
    candidates.append(exe_dir)
    for root in candidates:
        if os.path.isfile(os.path.join(root, marker)):
            return root
    return exe_dir


def _writable_app_root() -> str:
    """Katalog na dane zapisywalne przez użytkownika (baza): repo albo folder z `.exe`."""
    if getattr(sys, "frozen", False):
        return _frozen_exe_dir()
    return _dev_project_root()


def _asset_path(*parts: str) -> str:
    return os.path.abspath(os.path.join(_bundled_assets_root(), *parts))


def _user_data_path(*parts: str) -> str:
    return os.path.abspath(os.path.join(_writable_app_root(), *parts))


# TODO:
# - Dodać wyszukiwanie zawodów po nazwie i dacie w 'Zarządzaj zawodami'
# - Ustawić maksymalną ilość wyników wyszukiwania zawodników i dodać przycisk 'Pokaż więcej wyników'
# - Dodać dynamiczny rozmiar spacera w zależności od ilości wyników wyszukiwania zawodników
# - Naprawić display zawodów w 'Zarządzaj zawodami'
# - Obsługa dogrywek


class Globals:
    """Centralna konfiguracja aplikacji — formaty, ścieżki, połączenie z bazą danych."""

    # ─── Formaty dat i czasu ───────────────────────────────────────────

    DATE_FORMAT_PY = '%d/%m/%Y'
    DATE_FORMAT_QT = 'dd/MM/yyyy'
    TIME_FORMAT_PY = '%H:%M:%S'
    TIME_FORMAT_QT = 'HH:mm:ss'
    TIMESTAMP_FORMAT_PY = '%H:%M:%S %d/%m/%Y'
    TIMESTAMP_FORMAT_QT = 'HH:mm:ss dd/MM/yyyy'
    TODAY_DATE = datetime.datetime.now().strftime(DATE_FORMAT_PY)

    # ─── Ścieżki i zasoby ─────────────────────────────────────────────

    DB_PATH = _user_data_path('Database_Files', 'Database.db')
    PROJECT_NAME = 'SOKs_LOK'
    UI_LOADER = QUiLoader()

    UI_PATHS_DICT = {
        'OPERATOR_WINDOW': _asset_path('Ui_Files', 'OperatorWindow.ui'),
        'NEW_COMPETITION_DIALOG': _asset_path('Ui_Files', 'NoweZawodyDialog.ui'),
        '5_SHOOTS_TABLE': _asset_path('Ui_Files', 'Tabelka5Strzałów.ui'),
        '10_SHOOTS_TABLE': _asset_path('Ui_Files', 'Tabelka10Strzałów.ui'),
        'ZAPADKI_TABLE': _asset_path('Ui_Files', 'TabelkaZapadki.ui'),
        'KREATOR_KONKURENCJI_DIALOG': _asset_path('Ui_Files', 'KreatorKonkurencji.ui'),
        'ZAREJESTRUJ_SERIE_DIALOG': _asset_path('Ui_Files', 'ZarejestrujSerie.ui'),
        'TEMPORARY_DISPLAY': _asset_path('Ui_Files', 'TemporaryDisplay.ui'),
        'WAITING_DISPLAY': _asset_path('Ui_Files', 'Waiting.ui'),
    }

    RESOURCES_PATHS_DICT = {
        'LOGO_IMAGE': _asset_path('Resources', 'logo.jpeg'),
    }

    def __init__(self) -> None:
        """Inicjalizuje zasoby globalne używane przez aplikację."""
        self._ensure_database_path()
        self.database = DatabaseConnection()
        self.database.connect()
        self.database.disconnect()

    @classmethod
    def _ensure_database_path(cls) -> None:
        """Tworzy katalog i plik bazy, jeśli nie istnieją."""
        db_dir = os.path.dirname(cls.DB_PATH)
        os.makedirs(db_dir, exist_ok=True)
        if not os.path.exists(cls.DB_PATH):
            with open(cls.DB_PATH, "a", encoding="utf-8"):
                pass

    @staticmethod
    def project_root() -> str:
        """Katalog zapisywalny (baza): repo albo folder obok `SOKs_LOK.exe`."""
        return _writable_app_root()

    @staticmethod
    def set_main_directory() -> None:
        """Dodaje katalogi do `sys.path` (import `Resources` itd.)."""
        if getattr(sys, "frozen", False):
            for d in (_writable_app_root(), _bundled_assets_root()):
                if d not in sys.path:
                    sys.path.insert(0, d)
        else:
            main_dir = _dev_project_root()
            if main_dir not in sys.path:
                sys.path.insert(0, main_dir)

    # ─── Parsowanie i formatowanie dat ─────────────────────────────────

    @staticmethod
    def _parse_with_formats(value: str, formats: tuple[str, ...]) -> str | None:
        """Próbuje sparsować `value` kolejnymi formatami z `formats`.

        Zwraca sformatowany łańcuch przy pierwszym dopasowaniu lub `None`.
        """
        for fmt in formats:
            try:
                return datetime.datetime.strptime(value, fmt).strftime(fmt)
            except ValueError:
                continue
        return None

    @staticmethod
    def set_timestamp_format(timestamp: str) -> str | None:
        """Parsuje i formatuje timestamp (czas + data)."""
        return Globals._parse_with_formats(
            timestamp, (Globals.TIMESTAMP_FORMAT_PY, Globals.TIMESTAMP_FORMAT_QT)
        )

    @staticmethod
    def set_date_format(date: str) -> str | None:
        """Parsuje i formatuje datę."""
        return Globals._parse_with_formats(
            date, (Globals.DATE_FORMAT_PY, Globals.DATE_FORMAT_QT)
        )

    @staticmethod
    def set_time_format(time: str) -> str | None:
        """Parsuje i formatuje czas."""
        return Globals._parse_with_formats(
            time, (Globals.TIME_FORMAT_PY, Globals.TIME_FORMAT_QT)
        )

    @staticmethod
    def imie_or_nazwisko_parser(imie_or_nazwisko: str) -> str:
        """Zwraca imię lub nazwisko w postaci kanonicznej (trim, pierwsza litera wielka).

        Ujednolica zapis i porównania niezależnie od wielkości liter w polu tekstowym.
        Przy wielu segmentach oddzielonych ``-`` każdy segment jest formatowany osobno.
        """
        raw = imie_or_nazwisko.strip()
        if not raw:
            return ""
        parts = [p for p in raw.split("-") if p.strip()]
        if len(parts) >= 2:
            return "-".join(p.strip().lower().capitalize() for p in parts)
        return raw.lower().capitalize()

