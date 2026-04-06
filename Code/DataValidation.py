from Globals import Globals
import datetime
Globals.setMainDirectory()


class New_zawody_data_validation:
    def __init__(self, nazwa, dateTime, konkurencje):
        self.nazwa = nazwa
        self.dateTime = dateTime
        self.konkurencje = konkurencje
        self.is_valid_result = self.is_valid()
    def is_valid(self):
        if not self.nazwa.strip():
            return False, "Nazwa zawodów nie może być pusta."
        if not self.dateTime.strip():
            return False, "Data i czas zawodów nie mogą być puste."
        zawody_datetime = None
        for format in (Globals.TIMESTAMP_FORMAT_PY, Globals.TIMESTAMP_FORMAT_QT):
            try:
                zawody_datetime = datetime.datetime.strptime(self.dateTime, format)
                break
            except ValueError:
                continue
        if zawody_datetime is None:
            return False, "Nieprawidłowy format daty i czasu."
        if zawody_datetime < datetime.datetime.now():
            return False, "Data i czas zawodów nie mogą być w przeszłości."
        
        if not self.konkurencje:
            return False, "Należy wybrać co najmniej jedną konkurencję."
        return True, "Dane są poprawne."

class New_konkurencja_data_validation:
    def __init__(self, shots_quantity, name):
        self.shots_quantity = shots_quantity
        self.name = name
        self.is_valid_result = self.is_valid()
    
    def is_valid(self):
        if not isinstance(self.shots_quantity, int) or self.shots_quantity <= 0:
            return False, "Liczba strzałów musi być dodatnią liczbą całkowitą."
        if self.shots_quantity > 99:
            return False, "Liczba strzałów nie może przekraczać 99."
        if not self.name.strip():
            return False, "Nazwa konkurencji nie może być pusta."
        return True, "Dane są poprawne."
    

