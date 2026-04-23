from Globals import Globals
Globals.setMainDirectory()

class Konkurencja:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
        self.id = None
        self.nazwa = None
        self.ilosc_strzalow = None
    
    
class Konkurencja_data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    def get_konkurencja_by_name(self, nazwa):
        query = "SELECT id, ilosc_strzalow FROM konkurencje_lista WHERE nazwa = ?"
        params = (nazwa,)
        result = self.database.query(query, params)
        if result:
            setattr(self, f'{nazwa}_obj', Konkurencja(self.database))  # Inicjalizacja atrybutu o nazwie konkurencji
            getattr(self, f'{nazwa}_obj').id = result[0][0]
            getattr(self, f'{nazwa}_obj').nazwa = nazwa
            getattr(self, f'{nazwa}_obj').ilosc_strzalow = result[0][1]
            return getattr(self, f'{nazwa}_obj')
        else:
            return None
    def get_konkurencja_by_id(self, id):
        query = "SELECT nazwa, ilosc_strzalow FROM konkurencje_lista WHERE id = ?"
        params = (id,)
        result = self.database.query(query, params)
        if result:
            nazwa = result[0][0]
            ilosc_strzalow = result[0][1]
            setattr(self, f'{nazwa}_obj', Konkurencja(self.database))  # Inicjalizacja atrybutu o nazwie konkurencji
            getattr(self, f'{nazwa}_obj').id = id
            getattr(self, f'{nazwa}_obj').nazwa = nazwa
            getattr(self, f'{nazwa}_obj').ilosc_strzalow = ilosc_strzalow
            return getattr(self, f'{nazwa}_obj')
        else:
            return None
        
    def insert_konkurencja(self, nazwa, ilosc_strzalow):
        query = "INSERT INTO konkurencje_lista (nazwa, ilosc_strzalow) VALUES (?, ?)"
        params = (nazwa, ilosc_strzalow)
        latest_id = self.database.query(query, params)
        print(latest_id)
        if not latest_id:
            return None
        konkurencja = self.get_konkurencja_by_id(latest_id)
        return konkurencja

konkurencja_data_manager = Konkurencja_data_manager()



class Zawody:
    def __init__(self):
        self.id = None
        self.nazwa = None
        self.dateTime = None
        self.konkurencje = {}





class Zawody_data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    
    def get_zawody_by_id(self, id_zawodow):
        query = "SELECT nazwa, data, godzina FROM zawody_lista WHERE id = ?"
        params = (id_zawodow,)
        result = self.database.query(query, params)
        if result:
            nazwa = result[0][0]
            data = result[0][1]
            godzina = result[0][2]
            zawody = Zawody()
            zawody.id = id_zawodow
            
            zawody.nazwa = nazwa
            import datetime
            zawody.dateTime = datetime.datetime.strptime(f"{godzina} {data}", Globals.TIMESTAMP_FORMAT_PY)
            zawody.konkurencje = self.get_konkurencje_assigned_to_zawody(id_zawodow)
            return zawody
        else:
            return None
    
    def get_zawody_by_name(self, nazwa):
        query = "SELECT id, data, godzina FROM zawody_lista WHERE nazwa = ?"
        params = (nazwa,)
        result = self.database.query(query, params)
        if result:
            id_zawodow = result[0][0]
            data = result[0][1]
            godzina = result[0][2]
            zawody = Zawody(self.database)
            zawody.id = id_zawodow
            zawody.nazwa = nazwa
            import datetime
            zawody.dateTime = datetime.datetime.strptime(f"{godzina} {data}", Globals.TIMESTAMP_FORMAT_PY)
            zawody.konkurencje = self.get_konkurencje_assigned_to_zawody(id_zawodow)
            return zawody
        else:
            return None


    def get_all_zawody(self):
        query = "SELECT id FROM zawody_lista"
        results = self.database.query(query)
        zawody_list = {}
        if results:
            for row in results:
                id_zawodow = row[0]
                zawody = self.get_zawody_by_id(id_zawodow)
                if zawody:
                    zawody_list[zawody.nazwa] = zawody
            return zawody_list
        else:
            return None
                
        
    def insert_zawody(self, nazwa, dateTime, konkurencje):
        import datetime
        dateTime = datetime.datetime.strptime(dateTime, Globals.TIMESTAMP_FORMAT_PY)
        date_str = dateTime.strftime(Globals.DATE_FORMAT_PY)
        time_str = dateTime.strftime(Globals.TIME_FORMAT_PY)
        query = "INSERT INTO zawody_lista (nazwa, data, godzina) VALUES (?, ?, ?)"
        params = (nazwa, date_str, time_str)
        latest_id = self.database.query(query, params)
        if not latest_id:
            return None
        for konkurencja in konkurencje.values():
            query = "INSERT INTO \"zawody-konkurencje_link\" (id_zawodow, id_konkurencji) VALUES (?, ?)"
            params = (latest_id, konkurencja.id)
            self.database.query(query, params)

        zawody = self.get_zawody_by_id(latest_id)
        if zawody:
            return zawody
        else:
            return None
    def get_konkurencje_assigned_to_zawody(self, id_zawodow):
        query = "SELECT id_konkurencji FROM \"zawody-konkurencje_link\" WHERE id_zawodow = ?"
        params = (id_zawodow,)
        result = self.database.query(query, params)
        konkurencje = {}
        if result:
            for row in result:
                id_konkurencji = row[0]
                konkurencja = konkurencja_data_manager.get_konkurencja_by_id(id_konkurencji)
                if konkurencja:
                    konkurencje[konkurencja.nazwa] = konkurencja
        return konkurencje


zawody_data_manager = Zawody_data_manager()

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
        


            
        
client_data_manager = Client_data_manager()
