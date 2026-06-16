from globals import Globals
Globals.set_main_directory()

from PySide6.QtWidgets import QApplication, QTableWidgetItem
from PySide6.QtGui import QHeaderView
from PySide6.QtCore import QTimer

from data_manager import (
    Zawody,
    Konkurencja,
    wynik_data_manager, 
    seria_data_manager,
)

class PlebsDisplay:

    def __init__(self) -> None:
        self.timer = QTimer()
        self.timer.setInterval(5000)
        self.timer.timeout.connect(self._update_loop)
        self.display_running = False 
        self.window = None
        self.current_zawody = None
        self.current_konkurencja = None

    def _setup_window(self) -> None:
        self.window = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['TEMPORARY_DISPLAY'])
        self.window.setGeometry(self.tv_screen.geometry())
        self.window.show()

    def enable_display(self, zawody: Zawody, konkurencja: Konkurencja) -> tuple[bool, str | None]:
        if len(QApplication.screens()) < 2:
            return False, "Brak drugiego ekranu"
        self.tv_screen = QApplication.screens()[1]
        if zawody is not None and zawody != self.current_zawody:
            self.current_zawody = zawody
        if konkurencja is not None and konkurencja != self.current_konkurencja:
            self.current_konkurencja = konkurencja
        if self.window is None:
            self._setup_window()
        self.window.setScreen(self.tv_screen)

        self.window.showFullScreen()
        self.display_running = True
        self._setup_table(self.current_konkurencja)
        self.timer.start()  
        return True, None

    
    def disable_display(self) -> tuple[bool, str | None]:
        if self.window is None:
            return False, "Okno nie znalezione"
        self.display_running = False
        self.timer.stop()
        self.window.close()
        self.window = None
        self.current_zawody = None
        self.current_konkurencja = None
        return True, None

    def _setup_table(self, konkurencja: Konkurencja) -> None:
        tableWidget = self.window.tableWidget
        tableWidget.setColumnCount(konkurencja.shots_quantity + 2)
        tableWidget.setHorizontalHeaderLabels(
            ["Zawodnik"] + [f"Strzał {i + 1}" for i in range(konkurencja.shots_quantity)] + ["Razem"]
        )
        for col in range(tableWidget.columnCount()):
            tableWidget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)

    def _update_display(self) -> tuple[bool, str | None]:
        if self.current_zawody is None:
            return False, "Zawody nie znalezione"
        if self.current_konkurencja is None:
            return False, "Konkurencja nie znaleziona"
        if self.window is None:
            return False, "Okno nie znalezione"
        self.window.name_label.setText(self.current_zawody.nazwa)
        self.window.tableWidget.clearContents()
        self.window.tableWidget.setRowCount(0)
        all_serie = seria_data_manager.get_all_series_by_zawody_and_konkurencja(self.current_zawody.id, self.current_konkurencja.id)
        if not all_serie:
            return False, "Serie nie znalezione"
        for seria in all_serie:
            wyniki = wynik_data_manager.get_all_wyniki_by_seria_id(seria.id)
            if not wyniki:
                continue
            self.window.tableWidget.insertRow(self.window.tableWidget.rowCount())
            zawodnik = seria.zawodnik
            item = QTableWidgetItem(zawodnik.label)
            self.window.tableWidget.setItem(self.window.tableWidget.rowCount() - 1, 0, item)
            for wynik in wyniki:
                item = QTableWidgetItem(str(wynik.punkty))
                self.window.tableWidget.setItem(self.window.tableWidget.rowCount() - 1, wynik.nr_strzalu, item)
            item = QTableWidgetItem(str(sum(wynik.punkty for wynik in wyniki)))
            self.window.tableWidget.setItem(self.window.tableWidget.rowCount() - 1, self.window.tableWidget.columnCount() - 1, item)
        return True, None
    
    def _update_loop(self, zawody: Zawody | None = None, konkurencja: Konkurencja | None = None) -> None:
        if not self.display_running:
            self.timer.stop()
            return
        is_success, message = self._update_display()
        if not is_success:
            self.display_running = False
            self.timer.stop()
            print(message)
            return
    