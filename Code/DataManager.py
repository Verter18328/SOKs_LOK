from Globals import Globals
Globals.setMainDirectory()

class Data_manager:
    def __init__(self, db=None):
        self.database = db if db is not None else Globals().database
    def getClients(self):
        query = "SELECT * FROM zawodnicy"
        klienci = []
        results = self.database.query(query)
        if results:
            for row in results:
                klientDict = {
                    'id': None,
                    'imie': None,
                    'nazwisko': None,
                    'rocznik': None
                }
                klientDict['id'] = row[0]
                klientDict['imie'] = row[1]
                klientDict['nazwisko'] = row[2]
                klientDict['rocznik'] = row[3]
                klienci.append(klientDict)
            return klienci
        else:
            return None
        

data_manager = Data_manager()
