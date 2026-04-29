"""Moduł zarządzający modelami danych i dostępem do bazy danych.
Zawiera klasy modelowe i menedżery danych wykorzystywane przez UI.

Klasy:
 - `Konkurencja`, `Zawody` - proste modele danych
 - `Konkurencja_data_manager`, `Zawody_data_manager`, `Client_data_manager` - operacje DB
"""

import datetime

from Globals import Globals
Globals.setMainDirectory()


class Konkurencja:
    """Reprezentuje konkurencję (nazwa oraz liczba strzałów)."""

    def __init__(self, name=None, shots_quantity=None):
        self.id = None
        self.name = name
        self.shots_quantity = shots_quantity


class Konkurencja_data_manager:
    """Menedżer dostępu do tabeli `konkurencje_lista`.

    Metody zwracają obiekty `Konkurencja` lub `None`.
    """

    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database

    def get_konkurencja_by_name(self, name):
        query = "SELECT id, ilosc_strzalow FROM konkurencje_lista WHERE nazwa = ?"
        result = self.database.query(query, (name,))
        if result:
            obj = Konkurencja(name, result[0][1])
            obj.id = result[0][0]
            return obj
        return None

    def get_konkurencja_by_id(self, konkurencja_id):
        query = "SELECT nazwa, ilosc_strzalow FROM konkurencje_lista WHERE id = ?"
        result = self.database.query(query, (konkurencja_id,))
        if result:
            obj = Konkurencja(result[0][0], result[0][1])
            obj.id = konkurencja_id
            return obj
        return None

    def insert_konkurencja(self, name, shots_quantity):
        query = "INSERT INTO konkurencje_lista (nazwa, ilosc_strzalow) VALUES (?, ?)"
        latest_id = self.database.query(query, (name, shots_quantity))
        if not latest_id:
            return None
        return self.get_konkurencja_by_id(latest_id)

    def get_all_konkurencje(self):
        query = "SELECT nazwa, ilosc_strzalow FROM konkurencje_lista"
        results = self.database.query(query)
        if not results:
            return None
        return {row[0]: Konkurencja(row[0], row[1]) for row in results}


konkurencja_data_manager = Konkurencja_data_manager()


class Zawody:
    """Reprezentuje zawody: nazwa, data/czas i przypisane konkurencje."""

    def __init__(self):
        self.id = None
        self.nazwa = None
        self.dateTime = None
        self.konkurencje = {}


class Zawody_data_manager:
    """Menedżer dostępu do tabeli `zawody_lista` i linków do konkurencji."""

    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database

    def get_zawody_by_id(self, zawody_id):
        query = "SELECT nazwa, data, godzina FROM zawody_lista WHERE id = ?"
        result = self.database.query(query, (zawody_id,))
        if not result:
            return None
        zawody = Zawody()
        zawody.id = zawody_id
        zawody.nazwa = result[0][0]
        # Tworzymy obiekt datetime na podstawie pól godzina i data
        zawody.dateTime = datetime.datetime.strptime(f"{result[0][2]} {result[0][1]}", Globals.TIMESTAMP_FORMAT_PY)
        zawody.konkurencje = self.get_konkurencje_assigned_to_zawody(zawody_id)
        return zawody

    def get_zawody_by_name(self, nazwa):
        query = "SELECT id, data, godzina FROM zawody_lista WHERE nazwa = ?"
        result = self.database.query(query, (nazwa,))
        if not result:
            return None
        zawody = Zawody()
        zawody.id = result[0][0]
        zawody.nazwa = nazwa
        zawody.dateTime = datetime.datetime.strptime(f"{result[0][2]} {result[0][1]}", Globals.TIMESTAMP_FORMAT_PY)
        zawody.konkurencje = self.get_konkurencje_assigned_to_zawody(zawody.id)
        return zawody

    def get_all_zawody(self):
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

    def insert_zawody(self, nazwa, dateTime, konkurencje):
        """Dodaje nowe zawody i linkuje wybrane konkurencje."""

        dt = datetime.datetime.strptime(dateTime, Globals.TIMESTAMP_FORMAT_PY)
        query = "INSERT INTO zawody_lista (nazwa, data, godzina) VALUES (?, ?, ?)"
        latest_id = self.database.query(query, (nazwa, dt.strftime(Globals.DATE_FORMAT_PY), dt.strftime(Globals.TIME_FORMAT_PY)))
        if not latest_id:
            return None
        link_query = "INSERT INTO \"zawody-konkurencje_link\" (id_zawodow, id_konkurencji) VALUES (?, ?)"
        for konkurencja in konkurencje.values():
            self.database.query(link_query, (latest_id, konkurencja.id))
        return self.get_zawody_by_id(latest_id)

    def get_konkurencje_assigned_to_zawody(self, zawody_id):
        """Zwraca słownik przypisanych konkurencji dla podanego `zawody_id`."""

        query = "SELECT id_konkurencji FROM \"zawody-konkurencje_link\" WHERE id_zawodow = ?"
        result = self.database.query(query, (zawody_id,))
        if not result:
            return {}
        konkurencje = {}
        for row in result:
            konkurencja = konkurencja_data_manager.get_konkurencja_by_id(row[0])
            if konkurencja:
                konkurencje[konkurencja.name] = konkurencja
        return konkurencje


zawody_data_manager = Zawody_data_manager()


class Client_data_manager:
    """Menedżer operacji na tabeli `zawodnicy`.

    `get_clients(filter)` zwraca listę słowników z polami: id, imie, nazwisko, rocznik.
    """

    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database

    def get_clients(self, filter=None):
        if filter:
            query = """SELECT * FROM zawodnicy
                       WHERE imie || ' ' || nazwisko LIKE ?
                       ORDER BY nazwisko, imie
                       LIMIT 30"""
            params = (f'%{filter}%',)
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

    def get_id_from_name(self, imie, nazwisko):
        query = "SELECT id FROM zawodnicy WHERE imie = ? AND nazwisko = ?"
        results = self.database.query(query, (imie, nazwisko))
        return results[0][0] if results else None

    def get_name_from_id(self, client_id):
        query = "SELECT imie, nazwisko FROM zawodnicy WHERE id = ?"
        results = self.database.query(query, (client_id,))
        if results:
            return {'imie': results[0][0], 'nazwisko': results[0][1]}
        return None


client_data_manager = Client_data_manager()
