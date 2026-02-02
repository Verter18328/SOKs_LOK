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
        
        try:
            # Parsuj datetime z formatu "HH:MM DD/MM/YYYY"
            zawody_datetime = datetime.datetime.strptime(self.dateTime, '%H:%M %d/%m/%Y')
            now = datetime.datetime.now()
            
            if zawody_datetime < now:
                return False, "Data i czas zawodów nie mogą być w przeszłości."
        except ValueError:
            return False, "Nieprawidłowy format daty i czasu."
        
        if not self.konkurencje:
            return False, "Należy wybrać co najmniej jedną konkurencję."
        if len(self.konkurencje) != len(set(self.konkurencje)):
            return False, "Wybrane konkurencje muszą być unikalne."
        return True, "Dane są poprawne."