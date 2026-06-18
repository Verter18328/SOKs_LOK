# Komponenty osób trzecich

Oprogramowanie SOKs_LOK korzysta z poniższych komponentów zewnętrznych.
Niniejszy plik nie zastępuje pełnych tekstów licencji tych projektów.

## PySide6 (Qt for Python)

- **Zastosowanie:** interfejs graficzny (QtWidgets, QtCore, QtGui, QtUiTools)
- **Licencja:** GNU Lesser General Public License v3 (LGPL-3.0)
- **Strona:** https://www.qt.io/qt-for-python
- **Tekst licencji LGPL:** https://www.gnu.org/licenses/lgpl-3.0.html

Zgodnie z wymogami LGPL, przy dystrybucji skompilowanej wersji aplikacji
(np. pakiet EXE z PyInstaller) należy:

1. poinformować użytkownika, że aplikacja korzysta z Qt/PySide6 na licencji LGPL;
2. umożliwić wymianę bibliotek Qt powiązanych dynamicznie z aplikacją;
3. na żądanie udostępnić odpowiedni kod źródłowy Qt lub wskazać sposób jego pozyskania.

Kod własny SOKs_LOK (poza powyższymi bibliotekami) pozostaje na licencji
własnościowej — patrz plik `LICENSE`.

## SQLite

- **Zastosowanie:** lokalna baza danych (moduł `sqlite3` biblioteki standardowej Pythona)
- **Licencja:** public domain (SQLite jest samodzielną biblioteką C; Python łączy się z nią standardowo)

## Python

- **Zastosowanie:** język programowania i środowisko uruchomieniowe
- **Licencja:** Python Software Foundation License
- **Strona:** https://www.python.org/psf/license/
