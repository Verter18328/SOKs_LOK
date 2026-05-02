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
├─ Database_Files/      # lokalna baza danych SQLite (katalog tworzony przy pierwszym starcie)
├─ requirements.txt   # zależności Python (pip install -r requirements.txt)
└─ README.md
```

## Szybki start (po sklonowaniu z GitHuba)

Wymagania: **Python 3.11 lub nowszy** (64-bit zalecany na Windows), dostęp do internetu przy pierwszej instalacji pakietów.

### 1. Repozytorium i środowisko wirtualne (zalecane)

Z katalogu, w którym trzymasz projekty:

```bash
git clone <adres HTTPS repozytorium z GitHuba>
cd SOKs_LOK
python -m venv .venv
```

**Windows (PowerShell)** — aktywacja venv:

```powershell
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
source .venv/bin/activate
```

### 2. Instalacja zależności

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

(Instalowany jest m.in. **PySide6**.)

### 3. Uruchomienie aplikacji

Uruchamiaj z **korzenia repozytorium** (katalog `SOKs_LOK`, tam gdzie leży `README.md`):

```bash
python Code/operator_ui_handler.py
```

Na Windows, jeśli polecenie `python` nie działa, spróbuj:

```powershell
py -3.11 Code/operator_ui_handler.py
```

Po uruchomieniu aplikacja:

- ładuje interfejs z plików `.ui`,
- inicjalizuje połączenie z bazą danych,
- tworzy katalog `Database_Files` i plik bazy, jeśli jeszcze nie istnieją,
- tworzy wymagane tabele w SQLite przy pierwszym połączeniu.

### Typowe problemy

| Objaw | Co zrobić |
|--------|-----------|
| `ModuleNotFoundError: No module named 'PySide6'` | Upewnij się, że aktywowałeś `.venv` i wykonałeś `pip install -r requirements.txt` w tym samym środowisku. |
| `No module named 'data_manager'` / `Resources` | Uruchom skrypt z katalogu głównego projektu (`python Code/operator_ui_handler.py`), nie kopiuj plików `.py` poza strukturę repo. |
| PowerShell blokuje `Activate.ps1` | Jednorazowo: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

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
