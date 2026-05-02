"""Moduł zarządzający modelami danych i dostępem do bazy danych.

Zawiera klasy modelowe i menedżery danych wykorzystywane przez UI.

Klasy:
 - `Konkurencja`, `Zawody`, `Zawodnik`, `Seria` — proste modele danych
 - `KonkurencjaDataManager`, `ZawodyDataManager`, `ZawodnikDataManager`, `SeriaDataManager`, `WynikDataManager` — operacje DB
"""

import datetime

from globals import Globals

Globals.set_main_directory()


# ═══════════════════════════════════════════════════════════════════════
#  Model i menedżer: Konkurencja
# ═══════════════════════════════════════════════════════════════════════


class Wynik:
    """Reprezentuje wynik (numer strzału, punkty)."""
    def __init__(self, id: int, start_id: int, nr_strzalu: int, punkty: int) -> None:
        self.id = id
        self.start_id = start_id
        self.nr_strzalu = nr_strzalu
        self.punkty = punkty

class WynikDataManager:
    """Menedżer dostępu do tabeli starty.
    """
    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    def insert_wynik(self, seria_id: int, nr_strzalu: int, punkty: int) -> int | None:
        query = "INSERT INTO strzaly (start_id, nr_strzalu, punkty) VALUES (?, ?, ?)"
        latest_id = self.database.query(query, (seria_id, nr_strzalu, punkty))
        if not latest_id:
            return None
        return latest_id

    def get_all_wyniki_by_seria_id(self, seria_id: int) -> list[Wynik] | None:
        query = "SELECT id, start_id, nr_strzalu, punkty FROM strzaly WHERE start_id = ?"
        result = self.database.query(query, (seria_id,))
        if not result:
            return None
        return [Wynik(row[0], row[1], row[2], row[3]) for row in result]



wynik_data_manager = WynikDataManager()

class Seria:
    """Reprezentuje serię (numer serii, zawodnik, zawody, konkurencja)."""
    def __init__(
        self,
        number: int,
        zawodnik: Zawodnik,
        zawody: Zawody,
        konkurencja: Konkurencja,
        *,
        id: int | None = None,
    ) -> None:
        self.id = id
        self.number = number
        self.zawodnik = zawodnik
        self.zawody = zawody
        self.konkurencja = konkurencja


class SeriaDataManager:
    """Menedżer dostępu do tabeli `starty`.
    """
    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    def get_last_seria_number_for_konkurencja(self, konkurencja_id: int, zawody_id: int) -> int:
        query = "SELECT MAX(nr_serii) FROM starty WHERE konkurencja_id = ? AND zawody_id = ?"
        result = self.database.query(query, (konkurencja_id, zawody_id))
        if result is None or result[0][0] is None or result[0][0] == "":
            return 0
        return int(result[0][0])

    def insert_seria(self, number: int, zawodnik: Zawodnik, zawody: Zawody, konkurencja: Konkurencja) -> Seria:
        query = "INSERT INTO starty (nr_serii, zawodnik_id, zawody_id, konkurencja_id) VALUES (?, ?, ?, ?)"
        latest_id = self.database.query(query, (number, zawodnik.id, zawody.id, konkurencja.id))
        if not latest_id:
            return None
        return self.get_seria_by_id(latest_id)

    def does_seria_number_exist_for_konkurencja(self, seria_number: int, zawody_id: int, konkurencja_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM starty WHERE nr_serii = ? AND zawody_id = ? AND konkurencja_id = ?)"
        result = self.database.query(query, (seria_number, zawody_id, konkurencja_id))
        return bool(result[0][0]) if result else False

    def get_seria_by_id(self, seria_id: int) -> Seria | None:
        query = "SELECT id, nr_serii, zawodnik_id, zawody_id, konkurencja_id FROM starty WHERE id = ?"
        result = self.database.query(query, (seria_id,))
        if not result:
            return None
        row = result[0]
        return self._from_row(row[0], row[1], row[2], row[3], row[4])

    def get_seria_by_number_and_konkurencja_and_zawody(self, seria_number: int, zawody_id: int, konkurencja_id: int) -> Seria | None:
        query = "SELECT id FROM starty WHERE nr_serii = ? AND zawody_id = ? AND konkurencja_id = ?"
        result = self.database.query(query, (seria_number, zawody_id, konkurencja_id))
        if not result:
            return None
        return self.get_seria_by_id(result[0][0])
    
    def get_all_series_by_zawody_and_konkurencja(self, zawody_id: int, konkurencja_id: int) -> list[Seria] | None:
        query = "SELECT id, nr_serii, zawodnik_id, zawody_id, konkurencja_id FROM starty WHERE zawody_id = ? AND konkurencja_id = ?"
        result = self.database.query(query, (zawody_id, konkurencja_id))
        if not result:
            return None
        return [self._from_row(row[0], row[1], row[2], row[3], row[4]) for row in result]

    def _from_row(
        self,
        start_id: int,
        nr_serii: int,
        zawodnik_id: int,
        zawody_id: int,
        konkurencja_id: int,
    ) -> Seria:
        zawodnik = zawodnik_data_manager.get_zawodnik_by_id(zawodnik_id)
        zawody = zawody_data_manager.get_zawody_by_id(zawody_id)
        konkurencja = konkurencja_data_manager.get_konkurencja_by_id(konkurencja_id)
        if not zawodnik or not zawody or not konkurencja:
            return None
        return Seria(nr_serii, zawodnik, zawody, konkurencja, id=start_id)


seria_data_manager = SeriaDataManager()


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
        query = "SELECT id, nazwa, ilosc_strzalow FROM konkurencje_lista"
        results = self.database.query(query)
        if not results:
            return None
        return {row[1]: self._from_row(row[1], row[2], row[0]) for row in results}


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
        link_query = "INSERT INTO zawody_konkurencje_link (zawody_id, konkurencja_id) VALUES (?, ?)"

        for konkurencja in konkurencje.values():
            self.database.query(link_query, (latest_id, konkurencja.id))

        return self.get_zawody_by_id(latest_id)

    def get_konkurencje_assigned_to_zawody(self, zawody_id: int) -> dict[str, Konkurencja]:
        """Zwraca słownik przypisanych konkurencji dla podanego `zawody_id`."""
        query = "SELECT konkurencja_id FROM zawody_konkurencje_link WHERE zawody_id = ?"
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
#  Model i menedżer: Zawodnik
# ═══════════════════════════════════════════════════════════════════════


class Zawodnik:
    """Reprezentuje wiersz z tabeli `zawodnicy` (id, imię, nazwisko, rocznik)."""

    def __init__(
        self,
        imie: str | None = None,
        nazwisko: str | None = None,
        rocznik: str | None = None,
    ) -> None:
        self.id: int | None = None
        self.imie = imie if imie is not None else ""
        self.nazwisko = nazwisko if nazwisko is not None else ""
        self.rocznik = rocznik if rocznik is not None else ""

    def label(self) -> str:
        """Etykieta do list i pola wyszukiwania: „Imię Nazwisko”."""
        return f"{self.imie} {self.nazwisko}".strip()

    @staticmethod
    def _from_row(row_id: int, imie: str, nazwisko: str, rocznik: str) -> "Zawodnik":
        z = Zawodnik(imie, nazwisko, rocznik)
        z.id = row_id
        return z


class ZawodnikDataManager:
    """Menedżer operacji na tabeli `zawodnicy`.

    Metody zwracają obiekty `Zawodnik` lub `None` / listę modeli tam, gdzie to ma sens.
    """

    def __init__(self, db=None) -> None:
        self.database = db if db is not None else Globals().database

    def get_zawodnicy(self, filter_text: str | None = None) -> list[Zawodnik] | None:
        """Pobiera listę zawodników, opcjonalnie filtrowaną po imieniu/nazwisku."""
        if filter_text:
            query = """SELECT * FROM zawodnicy
                       WHERE imie || ' ' || nazwisko LIKE ?
                       ORDER BY nazwisko, imie
                       LIMIT 30"""
            params = (f"%{filter_text}%",)
        else:
            query = "SELECT * FROM zawodnicy ORDER BY nazwisko, imie"
            params = ()
        results = self.database.query(query, params)
        if not results:
            return None
        return [Zawodnik._from_row(row[0], row[1], row[2], row[3]) for row in results]

    def get_id_from_name_and_birth_year(self, imie: str, nazwisko: str, rocznik: str) -> int | None:
        """Zwraca ID zawodnika na podstawie imienia, nazwiska i roku urodzenia."""
        query = "SELECT id FROM zawodnicy WHERE imie = ? AND nazwisko = ? AND rocznik = ?"
        results = self.database.query(query, (imie, nazwisko, rocznik))
        if not results:
            return None
        return int(results[0][0])

    def get_zawodnik_by_id(self, zawodnik_id: int) -> Zawodnik | None:
        """Zwraca pełny rekord zawodnika po ID lub None."""
        query = "SELECT id, imie, nazwisko, rocznik FROM zawodnicy WHERE id = ?"
        results = self.database.query(query, (zawodnik_id,))
        if not results:
            return None
        row = results[0]
        return Zawodnik._from_row(row[0], row[1], row[2], row[3])

    def insert_zawodnik(self, imie: str, nazwisko: str, rocznik: str) -> Zawodnik | None:
        """Wstawia nowego zawodnika do bazy i zwraca utworzony obiekt."""
        query = "INSERT INTO zawodnicy (imie, nazwisko, rocznik) VALUES (?, ?, ?)"
        latest_id = self.database.query(query, (imie, nazwisko, rocznik))
        if not latest_id:
            return None
        return self.get_zawodnik_by_id(latest_id)


zawodnik_data_manager = ZawodnikDataManager()
