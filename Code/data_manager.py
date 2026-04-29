"""Moduł zarządzający modelami danych i dostępem do bazy danych.

Zawiera klasy modelowe i menedżery danych wykorzystywane przez UI.

Klasy:
 - `Konkurencja`, `Zawody` — proste modele danych
 - `KonkurencjaDataManager`, `ZawodyDataManager`, `ClientDataManager` — operacje DB
"""

import datetime

from globals import Globals

Globals.set_main_directory()


# ═══════════════════════════════════════════════════════════════════════
#  Model i menedżer: Konkurencja
# ═══════════════════════════════════════════════════════════════════════


class Konkurencja:
    """Reprezentuje konkurencję (nazwa oraz liczba strzałów)."""

    def __init__(self, name: str | None = None, shots_quantity: int | None = None) -> None:
        self.id: int | None = None
        self.name = name
        self.shots_quantity = shots_quantity

    def label(self) -> str:
        """Zwraca sformatowaną etykietę konkurencji do wyświetlenia w UI."""
        return f"{self.name} - {self.shots_quantity} strzałów"


class KonkurencjaDataManager:
    """Menedżer dostępu do tabeli `konkurencje_lista`.

    Metody zwracają obiekty `Konkurencja` lub `None`.
    """

    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    @staticmethod
    def _from_row(name: str, shots_quantity: int, konkurencja_id: int | None = None) -> Konkurencja:
        """Buduje obiekt `Konkurencja` z danych wiersza DB."""
        konkurencja = Konkurencja(name, shots_quantity)
        konkurencja.id = konkurencja_id
        return konkurencja

    def get_konkurencja_by_name(self, name: str) -> Konkurencja | None:
        """Wyszukuje konkurencję po nazwie."""
        query = "SELECT id, ilosc_strzalow FROM konkurencje_lista WHERE nazwa = ?"
        result = self.database.query(query, (name,))
        if result:
            return self._from_row(name, result[0][1], result[0][0])
        return None

    def get_konkurencja_by_id(self, konkurencja_id: int) -> Konkurencja | None:
        """Wyszukuje konkurencję po ID."""
        query = "SELECT nazwa, ilosc_strzalow FROM konkurencje_lista WHERE id = ?"
        result = self.database.query(query, (konkurencja_id,))
        if result:
            return self._from_row(result[0][0], result[0][1], konkurencja_id)
        return None

    def insert_konkurencja(self, name: str, shots_quantity: int) -> Konkurencja | None:
        """Wstawia nową konkurencję do bazy i zwraca utworzony obiekt."""
        query = "INSERT INTO konkurencje_lista (nazwa, ilosc_strzalow) VALUES (?, ?)"
        latest_id = self.database.query(query, (name, shots_quantity))
        if not latest_id:
            return None
        return self.get_konkurencja_by_id(latest_id)

    def get_all_konkurencje(self) -> dict[str, Konkurencja] | None:
        """Zwraca słownik `nazwa -> Konkurencja` dla wszystkich konkurencji."""
        query = "SELECT nazwa, ilosc_strzalow FROM konkurencje_lista"
        results = self.database.query(query)
        if not results:
            return None
        return {row[0]: self._from_row(row[0], row[1]) for row in results}


konkurencja_data_manager = KonkurencjaDataManager()


# ═══════════════════════════════════════════════════════════════════════
#  Model i menedżer: Zawody
# ═══════════════════════════════════════════════════════════════════════


class Zawody:
    """Reprezentuje zawody: nazwa, data/czas i przypisane konkurencje."""

    def __init__(self) -> None:
        self.id: int | None = None
        self.nazwa: str | None = None
        self.date_time: datetime.datetime | None = None
        self.konkurencje: dict[str, Konkurencja] = {}


class ZawodyDataManager:
    """Menedżer dostępu do tabeli `zawody_lista` i linków do konkurencji."""

    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    def _build_zawody(self, zawody_id: int, nazwa: str, data: str, godzina: str) -> Zawody:
        """Buduje obiekt `Zawody` z danych wiersza DB (wspólna logika dla get_by_id/name)."""
        zawody = Zawody()
        zawody.id = zawody_id
        zawody.nazwa = nazwa
        zawody.date_time = datetime.datetime.strptime(
            f"{godzina} {data}", Globals.TIMESTAMP_FORMAT_PY
        )
        zawody.konkurencje = self.get_konkurencje_assigned_to_zawody(zawody_id)
        return zawody

    def get_zawody_by_id(self, zawody_id: int) -> Zawody | None:
        """Pobiera zawody po ID."""
        query = "SELECT nazwa, data, godzina FROM zawody_lista WHERE id = ?"
        result = self.database.query(query, (zawody_id,))
        if not result:
            return None
        return self._build_zawody(zawody_id, result[0][0], result[0][1], result[0][2])

    def get_zawody_by_name(self, nazwa: str) -> Zawody | None:
        """Pobiera zawody po nazwie."""
        query = "SELECT id, data, godzina FROM zawody_lista WHERE nazwa = ?"
        result = self.database.query(query, (nazwa,))
        if not result:
            return None
        return self._build_zawody(result[0][0], nazwa, result[0][1], result[0][2])

    def get_all_zawody(self) -> dict[str, Zawody] | None:
        """Zwraca słownik `nazwa -> Zawody` dla wszystkich zawodów."""
        results = self.database.query("SELECT id FROM zawody_lista")
        if not results:
            return None
        zawody_dict = {}
        for row in results:
            zawody = self.get_zawody_by_id(row[0])
            if zawody:
                zawody_dict[zawody.nazwa] = zawody
        return zawody_dict

    def insert_zawody(self, nazwa: str, date_time: str, konkurencje: dict) -> Zawody | None:
        """Dodaje nowe zawody i linkuje wybrane konkurencje."""
        dt = datetime.datetime.strptime(date_time, Globals.TIMESTAMP_FORMAT_PY)
        query = "INSERT INTO zawody_lista (nazwa, data, godzina) VALUES (?, ?, ?)"
        latest_id = self.database.query(
            query, (nazwa, dt.strftime(Globals.DATE_FORMAT_PY), dt.strftime(Globals.TIME_FORMAT_PY))
        )
        if not latest_id:
            return None
        # Linkowanie konkurencji do nowo utworzonych zawodów
        link_query = "INSERT INTO \"zawody_konkurencje_link\" (zawody_id, konkurencja_id) VALUES (?, ?)"
        for konkurencja in konkurencje.values():
            self.database.query(link_query, (latest_id, konkurencja.id))
        return self.get_zawody_by_id(latest_id)

    def get_konkurencje_assigned_to_zawody(self, zawody_id: int) -> dict[str, Konkurencja]:
        """Zwraca słownik przypisanych konkurencji dla podanego `zawody_id`."""
        query = "SELECT konkurencja_id FROM \"zawody_konkurencje_link\" WHERE zawody_id = ?"
        result = self.database.query(query, (zawody_id,))
        if not result:
            return {}
        konkurencje = {}
        for row in result:
            konkurencja = konkurencja_data_manager.get_konkurencja_by_id(row[0])
            if konkurencja:
                konkurencje[konkurencja.name] = konkurencja
        return konkurencje


zawody_data_manager = ZawodyDataManager()


# ═══════════════════════════════════════════════════════════════════════
#  Menedżer: Zawodnicy (klienci)
# ═══════════════════════════════════════════════════════════════════════


class ClientDataManager:
    """Menedżer operacji na tabeli `zawodnicy`.

    `get_clients(filter_text)` zwraca listę słowników z polami: id, imie, nazwisko, rocznik.
    """

    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    def get_clients(self, filter_text: str | None = None) -> list[dict] | None:
        """Pobiera listę zawodników, opcjonalnie filtrowaną po imieniu/nazwisku."""
        if filter_text:
            query = """SELECT * FROM zawodnicy
                       WHERE imie || ' ' || nazwisko LIKE ?
                       ORDER BY nazwisko, imie
                       LIMIT 30"""
            params = (f"%{filter_text}%",)
        else:
            query = "SELECT * FROM zawodnicy"
            params = ()
        results = self.database.query(query, params)
        if not results:
            return None
        return [
            {'id': row[0], 'imie': row[1], 'nazwisko': row[2], 'rocznik': row[3]}
            for row in results
        ]

    def get_id_from_name(self, imie: str, nazwisko: str) -> int | None:
        """Zwraca ID zawodnika na podstawie imienia i nazwiska."""
        query = "SELECT id FROM zawodnicy WHERE imie = ? AND nazwisko = ?"
        results = self.database.query(query, (imie, nazwisko))
        return results[0][0] if results else None

    def get_name_from_id(self, client_id: int) -> dict[str, str] | None:
        """Zwraca słownik `{imie, nazwisko}` dla podanego ID zawodnika."""
        query = "SELECT imie, nazwisko FROM zawodnicy WHERE id = ?"
        results = self.database.query(query, (client_id,))
        if results:
            return {'imie': results[0][0], 'nazwisko': results[0][1]}
        return None


client_data_manager = ClientDataManager()
