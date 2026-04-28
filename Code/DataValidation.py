import datetime

from Globals import Globals
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
        for fmt in (Globals.TIMESTAMP_FORMAT_PY, Globals.TIMESTAMP_FORMAT_QT):
            try:
                zawody_datetime = datetime.datetime.strptime(self.dateTime, fmt)
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


class Wyniki_tab_validation:
    def __init__(self, value, is_shot_column):
        self.value = value
        self.is_shot_column = is_shot_column
        self.is_valid_result = self.is_valid()

    def is_valid(self):
        if self.is_shot_column:
            if not self.value.isdigit():
                return False, "Wynik strzału musi być liczbą całkowitą."
            if int(self.value) < 0:
                return False, "Wynik strzału nie może być ujemny."
        else:
            if not self.value.strip():
                return False, "Nazwa zawodnika nie może być pusta."
            if self.value.isdigit():
                return False, "Nazwa zawodnika nie może być liczbą."
        return True, "Dane są poprawne."
