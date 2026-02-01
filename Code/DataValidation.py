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
        if self.dateTime.strip() < datetime.datetime.now().strftime(Globals.TIMESTAMP_FORMAT):
            return False, "Data i czas zawodów nie mogą być w przeszłości."
        if not self.konkurencje:
            return False, "Należy wybrać co najmniej jedną konkurencję."
        if len(self.konkurencje) != len(set(self.konkurencje)):
            return False, "Wybrane konkurencje muszą być unikalne."
        return True, "Dane są poprawne."