from Globals import Globals
Globals.setMainDirectory()


class New_zawody_data_validation:
    def __init__(self, nazwa, konkurencje):
        self.nazwa = nazwa
        self.konkurencje = konkurencje
        self.is_valid_result = self.is_valid()
    def is_valid(self):
        if not self.nazwa.strip():
            return False, "Nazwa zawodów nie może być pusta."
        if not self.konkurencje:
            return False, "Należy wybrać co najmniej jedną konkurencję."
        if len(self.konkurencje) != len(set(self.konkurencje)):
            return False, "Wybrane konkurencje muszą być unikalne."
        return True, "Dane są poprawne."