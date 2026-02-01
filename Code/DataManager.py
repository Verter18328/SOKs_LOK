from Globals import Globals
Globals.setMainDirectory()

class New_zawody:
    def __init__(self):
        pass


class Data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    def get_clients(self):
        query = "SELECT * FROM zawodnicy"
        klienci = []
        results = self.database.query(query)
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
        

data_manager = Data_manager()
