"""Walidatory formularzy używane w dialogach aplikacji.

Zawiera proste klasy walidujące dane wejściowe dla:
- tworzenia zawodów (`NewZawodyDataValidation`)
- tworzenia konkurencji (`NewKonkurencjaDataValidation`)
- pojedynczych wpisów w tabeli wyników (`WynikiTabValidation`)

Każda klasa udostępnia atrybut `is_valid_result` — krotkę `(bool, str)`.
"""

import datetime

from data_manager import seria_data_manager, wynik_data_manager
from globals import Globals

Globals.set_main_directory()


# ─── Stałe walidacyjne ─────────────────────────────────────────────────

MAX_SHOTS: int = 99


class ZarejestrujSerieDataValidation:
    """Waliduje dane z formularza zarejestrowania serii."""
    def __init__(self, imie: str, nazwisko: str, rocznik: str) -> None:
        self.imie = Globals.imie_or_nazwisko_parser(imie)
        self.nazwisko = Globals.imie_or_nazwisko_parser(nazwisko)
        self.rocznik = rocznik
        self.is_valid_result: tuple[bool, str] = self.is_valid()
    
    def is_valid(self) -> tuple[bool, str]:
        """Sprawdza poprawność danych zarejestrowania serii."""
        if not self.imie.strip():
            return False, "Imię nie może być puste."
        if not self.nazwisko.strip():
            return False, "Nazwisko nie może być puste."
        if not self.rocznik.isdigit() or int(self.rocznik) <= 0:
            return False, "Rocznik musi być liczbą całkowitą."
        if int(self.rocznik) <= 0:
            return False, "Rocznik nie może być ujemny."
        return True, "Dane są poprawne."



class NewZawodyDataValidation:
    """Waliduje dane z formularza tworzenia zawodów.

    Atrybut `is_valid_result` zawiera krotkę `(bool, message)`.
    """

    def __init__(self, nazwa: str, date_time: str, konkurencje: dict) -> None:
        self.nazwa = nazwa
        self.date_time = date_time
        self.konkurencje = konkurencje
        self.is_valid_result: tuple[bool, str] = self.is_valid()

    def is_valid(self) -> tuple[bool, str]:
        """Sprawdza poprawność danych zawodów krok po kroku."""

        # 1. Nazwa nie może być pusta
        if not self.nazwa.strip():
            return False, "Nazwa zawodów nie może być pusta."

        # 2. Data/czas nie mogą być puste
        if not self.date_time.strip():
            return False, "Data i czas zawodów nie mogą być puste."

        # 3. Parsowanie daty — próba obu formatów (Python i Qt)
        zawody_datetime = None
        for fmt in (Globals.TIMESTAMP_FORMAT_PY, Globals.TIMESTAMP_FORMAT_QT):
            try:
                zawody_datetime = datetime.datetime.strptime(self.date_time, fmt)
                break
            except ValueError:
                continue
        if zawody_datetime is None:
            return False, "Nieprawidłowy format daty i czasu."

        # 4. Data nie może być w przeszłości
        if zawody_datetime < datetime.datetime.now():
            return False, "Data i czas zawodów nie mogą być w przeszłości."

        # 5. Musi być co najmniej jedna konkurencja
        if not self.konkurencje:
            return False, "Należy wybrać co najmniej jedną konkurencję."

        return True, "Dane są poprawne."


class NewKonkurencjaDataValidation:
    """Waliduje nazwę i liczbę strzałów dla nowej konkurencji."""

    def __init__(self, shots_quantity: int, name: str) -> None:
        self.shots_quantity = shots_quantity
        self.name = name
        self.is_valid_result: tuple[bool, str] = self.is_valid()

    def is_valid(self) -> tuple[bool, str]:
        """Sprawdza poprawność danych konkurencji."""
        if not isinstance(self.shots_quantity, int) or self.shots_quantity <= 0:
            return False, "Liczba strzałów musi być dodatnią liczbą całkowitą."
        if self.shots_quantity > MAX_SHOTS:
            return False, f"Liczba strzałów nie może przekraczać {MAX_SHOTS}."
        if not self.name.strip():
            return False, "Nazwa konkurencji nie może być pusta."
        return True, "Dane są poprawne."


class WynikiTabValidation:
    """Walidator pojedynczego pola w tabeli wyników.

    `is_shot_column=True` oznacza, że oczekujemy liczby całkowitej (wynik strzału).
    `is_shot_column=False` oznacza pole z numerem serii.
    """

    def __init__(self, value: str, is_shot_column: bool, zawody_id: int, konkurencja_id: int) -> None:
        self.value = value
        self.is_shot_column = is_shot_column
        self.zawody_id = zawody_id
        self.konkurencja_id = konkurencja_id
        self.is_valid_result: tuple[bool, str] = self.is_valid()

    def is_valid(self) -> tuple[bool, str]:
        """Sprawdza poprawność wpisanej wartości w zależności od typu kolumny."""
        if self.is_shot_column:
            # Kolumna strzału — oczekujemy nieujemnej liczby całkowitej
            if not self.value.isdigit():
                return False, "Wynik strzału musi być liczbą całkowitą."
            if int(self.value) < 0:
                return False, "Wynik strzału nie może być ujemny."
        else:
            if not self.value.isdigit():
                return False, "Numer serii musi być liczbą całkowitą."
            if int(self.value) == 0:
                return False, "Numer serii nie może być równy 0."
            if int(self.value) < 0:
                return False, "Numer serii nie może być ujemny."
            if not self.does_seria_number_exist_for_konkurencja(int(self.value)):
                return False, "Numer serii nie istnieje."
            seria = seria_data_manager.get_seria_by_number_and_konkurencja_and_zawody(
                int(self.value), self.zawody_id, self.konkurencja_id
            )
            if seria and wynik_data_manager.does_wynik_exist_for_seria_id(seria.id):
                return False, "Wynik dla tej serii już istnieje."
        return True, "Dane są poprawne."

    def does_seria_number_exist_for_konkurencja(self, seria_number: int) -> bool:
        return seria_data_manager.does_seria_number_exist_for_konkurencja(seria_number, self.zawody_id, self.konkurencja_id)
