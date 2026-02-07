from Globals import Globals
Globals.setMainDirectory()

class New_zawody:
    def __init__(self, nazwa, dateTime, konkurencje, db=None, data_manager=None):
        self.zawody_data_manager = data_manager if data_manager is not None else zawody_data_manager
        self.database = db if db is not None else Globals().database
        self.nazwa = nazwa
        self.dateTime = dateTime
        self.konkurencje_ids_dict = {
            konkurencja: self.zawody_data_manager.get_competition_id_by_name(konkurencja)
            for konkurencja in konkurencje
        }
        result = self.insery_into_zawody_lista()
        if result[0]:
            self.id_zawodow = result[1]
            self.assign_zawody_to_konkurencje()
        else:
            print("Error inserting new event into database")
    def insery_into_zawody_lista(self):
        query = "INSERT INTO zawody_lista (nazwa, data, godzina) VALUES (?, ?, ?)"
        params = (self.nazwa, self.dateTime.split(' ')[1], self.dateTime.split(' ')[0])
        result = self.database.query(query, params)
        if result:
            return True, result
        else:
            return False, None
    def assign_zawody_to_konkurencje(self):
        for konkurencja in self.konkurencje_ids_dict.keys():
            konkurencja_id = self.konkurencje_ids_dict.get(konkurencja)
            query = "INSERT INTO zawody_konkurencje_link (id_zawodow, id_konkurencji) VALUES (?, ?)"
            params = (self.id_zawodow, konkurencja_id)
            result = self.database.query(query, params)
            if result is None:
                print(f"Error inserting competition {konkurencja} for event {self.nazwa}")


class Loaded_zawody:
    """Klasa do reprezentacji zawodów wczytanych z bazy danych (nie tworzy nowych rekordów)"""
    def __init__(self, id_zawodow, nazwa, dateTime, konkurencje, db=None, data_manager=None):
        self.zawody_data_manager = data_manager if data_manager is not None else zawody_data_manager
        self.database = db if db is not None else Globals().database
        self.id_zawodow = id_zawodow
        self.nazwa = nazwa
        self.dateTime = dateTime
        self.konkurencje_ids_dict = {
            konkurencja: self.zawody_data_manager.get_competition_id_by_name(konkurencja)
            for konkurencja in konkurencje
        }

class Client_data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    def get_clients(self, filter=None):
        query = '''SELECT * FROM zawodnicy
                    WHERE imie || ' ' || nazwisko LIKE ?
                    ORDER BY nazwisko, imie
                    LIMIT 30''' if filter else "SELECT * FROM zawodnicy"
        params = (f'%{filter}%',) if filter else ()
        klienci = []
        results = self.database.query(query, params)
        if results:
            for row in results:
                id = row[0]
                imie = row[1]
                nazwisko = row[2]
                rocznik = row[3]
                setattr(self, f'{imie} {nazwisko}', {
                    'id': id,
                    'imie': imie,
                    'nazwisko': nazwisko,
                    'rocznik': rocznik
                })
                klienci.append(getattr(self, f'{imie} {nazwisko}'))
            return klienci
        else:
            return None
    def get_id_from_name(self, imie, nazwisko):
        query = "SELECT id FROM zawodnicy WHERE imie = ? AND nazwisko = ?"
        params = (imie, nazwisko)
        results = self.database.query(query, params)
        if results:
            return results[0][0]
        else:
            return None
    def get_name_from_id(self, id):
        query = "SELECT imie, nazwisko FROM zawodnicy WHERE id = ?"
        params = (id,)
        results = self.database.query(query, params)
        if results:
            imie, nazwisko = results[0]
            return {'imie': imie, 'nazwisko': nazwisko}
        else:
            return None
        

class Zawody_data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    def get_competition_id_by_name(self, nazwa):
        query = "SELECT id FROM konkurencje_lista WHERE nazwa_log = ?"
        params = (nazwa,)
        results = self.database.query(query, params)
        if results:
            return results[0][0]
        else:
            return None
    
    def get_zawody_by_id(self, id_zawodow):
        # Pobierz podstawowe dane zawodów
        query = "SELECT nazwa, data, godzina FROM zawody_lista WHERE id = ?"
        params = (id_zawodow,)
        result = self.database.query(query, params)
        if not result:
            return None
        
        nazwa, data, godzina = result[0]
        dateTime = f"{godzina} {data}"
        
        # Pobierz konkurencje związane z zawodami
        query_konkurencje = """
            SELECT kl.nazwa_log 
            FROM konkurencje_lista kl
            JOIN zawody_konkurencje_link zkl ON kl.id = zkl.id_konkurencji
            WHERE zkl.id_zawodow = ?
        """
        konkurencje_results = self.database.query(query_konkurencje, params)
        konkurencje = [row[0] for row in konkurencje_results] if konkurencje_results else []
        
        # Utwórz obiekt zawodów (bez wstawiania do bazy)
        return Loaded_zawody(id_zawodow, nazwa, dateTime, konkurencje, db=self.database, data_manager=self)
    def get_all_zawody(self):
        query = "SELECT * FROM zawody_lista"
        results = self.database.query(query)
        zawody_list = []
        
        if results:
            for row in results:
                id = row[0]
                nazwa = row[1]
                data = row[2]
                godzina = row[3]
                zawody_list.append({
                    'id': id,
                    'nazwa': nazwa,
                    'data': data,
                    'godzina': godzina
                })
            return zawody_list
        else:
            return None
            
        
zawody_data_manager = Zawody_data_manager()
client_data_manager = Client_data_manager()
