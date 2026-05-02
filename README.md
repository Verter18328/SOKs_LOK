# SOKs_LOK

System obsługi konkurencji strzeleckich oparty o `PySide6` i `SQLite`.
Aplikacja wspiera organizację zawodów, rejestrację serii i wprowadzanie wyników
z poziomu desktopowego interfejsu operatora.

## Co to jest?

`SOKs_LOK` to aplikacja desktopowa do pracy operacyjnej podczas zawodów
strzeleckich. Projekt skupia się na prostym i szybkim workflow:

- tworzenie zawodów i konkurencji,
- przypisywanie zawodników do serii,
- wprowadzanie wyników strzałów,
- prezentowanie i porządkowanie wyników.

## Najważniejsze funkcje

- Zarządzanie zawodami (nazwa, data i godzina).
- Definiowanie konkurencji wraz z liczbą strzałów.
- Rejestracja serii zawodników.
- Walidacja danych wejściowych podczas edycji wyników.
- Obsługa rankingu/sortowania wyników w UI.
- Lokalna baza `SQLite` tworzona automatycznie przy starcie.

## Technologie

- Python 3.11+
- PySide6 (interfejs graficzny)
- SQLite (lokalna baza danych)
- Qt Designer `.ui` (widoki)

## Struktura projektu

```text
SOKs_LOK/
├─ Code/                # logika aplikacji (UI handlers, sygnały, data manager)
├─ Ui_Files/            # pliki widoków Qt (.ui)
├─ Resources/           # zasoby statyczne (np. logo)
├─ Database_Files/      # lokalna baza danych SQLite
├─ requirements-dev.txt # zależności projektu
└─ README.md
```

## Szybki start

### 1. Instalacja zależności

```bash
pip install -r requirements-dev.txt
```

### 2. Uruchomienie aplikacji

```bash
python Code/operator_ui_handler.py
```

Po uruchomieniu aplikacja:

- ładuje interfejs z plików `.ui`,
- inicjalizuje połączenie z bazą danych,
- tworzy wymagane tabele, jeśli jeszcze nie istnieją.

## Baza danych

Domyślna lokalizacja bazy:

`Database_Files/Database.db`

Schemat obejmuje m.in. tabele:

- `konkurencje_lista`
- `zawodnicy`
- `zawody_lista`
- `zawody_konkurencje_link`
- `starty`
- `strzaly`

## Uwagi dla dewelopera

- Projekt korzysta z podejścia modularnego: logika UI, walidacja i dostęp do
  danych są rozdzielone na osobne moduły.
- Główny punkt wejścia aplikacji znajduje się w `Code/operator_ui_handler.py`.
- Plik bazy danych (`Database.db`) jest ignorowany przez Git.

## Status projektu

Projekt jest rozwijany i zawiera aktywną listę usprawnień (TODO) w kodzie.
Najlepiej traktować go jako aplikację roboczą, gotową do dalszej iteracji.
