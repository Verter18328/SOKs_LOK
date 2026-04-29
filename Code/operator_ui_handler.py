"""Punkt wejścia aplikacji — okna i dialogi operatora.

Każda klasa jest wrapperem ładującym plik `.ui` i podłączającym odpowiednie sygnały.
Wspólna logika inicjalizacji okna wydzielona do `_setup_window()`.
"""

import sys

from PySide6.QtWidgets import QApplication, QDialog, QMainWindow
from PySide6.QtCore import QDateTime
from PySide6.QtGui import QIcon

from globals import Globals
Globals.set_main_directory()
import Resources.resources_rc
from signals_dialogs import SignalsKreatorKonkurencjiDialog, SignalsNewCompetitionDialog
from signals_operator_window import SignalsOperatorWindow


def _setup_window(widget, global_config: Globals, ui_key: str, title: str) -> None:
    """Wspólna inicjalizacja okna/dialogu: ładowanie UI, ustawienie tytułu i ikony.

    Parametry:
    - `widget` — instancja okna/dialogu, na której ustawiane jest pole `UI`
    - `global_config` — obiekt konfiguracji `Globals`
    - `ui_key` — klucz w `UI_PATHS_DICT` wskazujący plik `.ui`
    - `title` — tytuł wyświetlany na pasku okna
    """
    widget.ui = global_config.UI_LOADER.load(global_config.UI_PATHS_DICT[ui_key])
    widget.ui.setWindowTitle(title)
    widget.ui.setWindowIcon(QIcon(global_config.RESOURCES_PATHS_DICT["LOGO_IMAGE"]))


class KreatorKonkurencjiDialog(QDialog):
    """Dialog tworzenia konkurencji — wrapper ładujący UI i podłączający sygnały."""

    def __init__(self, global_config: Globals | None = None, parent=None) -> None:
        super().__init__(parent)
        global_config = global_config if global_config is not None else Globals()
        _setup_window(self, global_config, "KREATOR_KONKURENCJI_DIALOG", "Kreator konkurencji")
        self.signals = SignalsKreatorKonkurencjiDialog(self.ui, parent)

    def show_dialog(self) -> None:
        """Wyświetla dialog."""
        self.ui.show()


class NoweZawodyDialog(QDialog):
    """Dialog tworzenia zawodów — ustawia datę domyślną i podłącza sygnały."""

    def __init__(self, global_config: Globals | None = None, parent=None) -> None:
        super().__init__(parent)
        global_config = global_config if global_config is not None else Globals()
        _setup_window(self, global_config, "NEW_COMPETITION_DIALOG", "Stwórz nowe zawody")

        # Ustawienie domyślnej daty na teraz i zablokowanie dat przeszłych
        timestamp = QDateTime.currentDateTime()
        self.ui.dateTimeEdit_data_zawodow.setDateTime(timestamp)
        self.ui.dateTimeEdit_data_zawodow.setMinimumDateTime(timestamp)

        self.parent_window = parent
        self.signals = SignalsNewCompetitionDialog(self.ui, self.parent_window)

    def show_dialog(self) -> None:
        """Wyświetla dialog."""
        self.ui.show()


class OperatorWindow(QMainWindow):
    """Główne okno aplikacji dla operatora — wrapper ładujący UI i inicjalizujący logikę."""

    def __init__(self, global_config: Globals | None = None) -> None:
        super().__init__()
        global_config = global_config if global_config is not None else Globals()
        _setup_window(self, global_config, "OPERATOR_WINDOW", global_config.PROJECT_NAME)
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageTitle)
        self.signals = SignalsOperatorWindow(self.ui)

    def show_window(self) -> None:
        """Wyświetla okno główne."""
        self.ui.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OperatorWindow()
    window.show_window()
    sys.exit(app.exec())