"""Obsługa sygnałów i logika UI głównego okna operatora."""

from functools import partial

from globals import Globals

Globals.set_main_directory()

from PySide6.QtCore import QEvent, QObject, Qt, QTimer, QStringListModel
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCompleter,
    QHeaderView,
    QListWidgetItem,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
)

from data_manager import konkurencja_data_manager, zawody_data_manager, zawodnik_data_manager, Seria, seria_data_manager, wynik_data_manager
from data_validation import WynikiTabValidation
from ranking_utils import sort_wyniki_grid


class _WynikRowEscapeFilter(QObject):
    """Esc na edytorze komórki — pierwszy Esc anuluje cały wiersz (bez połykania przez QLineEdit)."""

    def __init__(self, owner: "SignalsOperatorWindow") -> None:
        super().__init__(owner.ui)
        self._owner = owner

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() != QEvent.Type.KeyPress or event.key() != Qt.Key.Key_Escape:
            return False
        o = self._owner
        if o._wynik_edit_table is None:
            return False
        if o.ui.stackedWidget.currentWidget() != o.ui.pageZawody_managment:
            return False
        QTimer.singleShot(0, o._cancel_incomplete_wynik_row)
        return True


class SignalsOperatorWindow:
    """Logika i obsługa sygnałów głównego okna operatora."""

    SEARCH_DEBOUNCE_MS: int = 500
    MIN_SEARCH_LENGTH: int = 3
    FONT_SIZE_ZAWODY_LABEL: int = 16

    def __init__(self, ui) -> None:
        self.ui = ui
        self.sort_order: bool = False
        self._wynik_edit_table: QTableWidget | None = None
        self._wynik_edit_row: int | None = None
        self._wynik_edit_tab_index: int = 0
        self._wynik_item_changed_handler = None
        self._wynik_esc_filter = _WynikRowEscapeFilter(self)
        self._esc_filter_targets: list[QWidget] = []
        self.set_lista_zawodnikow_completer()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.connect_signals()

    def connect_signals(self) -> None:
        self.timer.timeout.connect(self.on_debounce_timeout)
        self.ui.actionLista_zawodnikow.triggered.connect(self.action_lista_zawodnikow_triggered)

        self.ui.exit_To_title_shortcut = QShortcut(QKeySequence("Esc"), self.ui)
        self.ui.exit_To_title_shortcut.activated.connect(self._escape_shortcut_triggered)

        self.ui.actionNowe_zawody.triggered.connect(self.action_nowe_zawody_triggered)
        self.ui.actionZarzadzanie_zawodami.triggered.connect(self.zarzadzanie_zawodami_triggered)
        self.ui.button_dodaj_wynik.clicked.connect(self.dodaj_wynik_clicked)
        self.ui.lineEditWyszukiwanie_zawodnikow.textChanged.connect(
            lambda: self.clients_search_changed(self.ui.lineEditWyszukiwanie_zawodnikow)
        )
        self.ui.newZawodnik_pushButton.clicked.connect(self.zarejestruj_serie_triggered)
        self.ui.sort_seria_button.clicked.connect(self.sort_seria_button_clicked)
        self.ui.sort_miejsce_button.clicked.connect(self.sort_miejsce_button_clicked)
        self.ui.tabWidget_zawody.currentChanged.connect(self._tab_zawody_changed_while_editing)

    def _escape_shortcut_triggered(self) -> None:
        if (
            self._wynik_edit_table is not None
            and self.ui.stackedWidget.currentWidget() == self.ui.pageZawody_managment
        ):
            self._cancel_incomplete_wynik_row()
            return
        self.exit_to_title_triggered()

    def _tab_zawody_changed_while_editing(self, index: int) -> None:
        if self._wynik_edit_table is None:
            return
        if self.ui.tabWidget_zawody.widget(index) is self._wynik_edit_table:
            return
        self.ui.tabWidget_zawody.blockSignals(True)
        self.ui.tabWidget_zawody.setCurrentIndex(self._wynik_edit_tab_index)
        self.ui.tabWidget_zawody.blockSignals(False)

    def _wynik_row_item_changed(self, table_widget: QTableWidget, row: int, item: QTableWidgetItem) -> None:
        self.on_table_item_changed(table_widget, item, row)

    def _detach_esc_filter_from_targets(self) -> None:
        for w in self._esc_filter_targets:
            try:
                w.removeEventFilter(self._wynik_esc_filter)
            except (RuntimeError, TypeError):
                pass
        self._esc_filter_targets = []

    def _attach_esc_filter_to_focus(self) -> None:
        if self._wynik_edit_table is None:
            return
        self._detach_esc_filter_from_targets()
        tw = self._wynik_edit_table
        targets: list[QWidget] = [tw]
        fw = QApplication.focusWidget()
        if fw is not None and fw is not tw:
            targets.append(fw)
        for t in targets:
            t.installEventFilter(self._wynik_esc_filter)
        self._esc_filter_targets = targets

    def _wynik_edit_lock_ui(self) -> None:
        self.ui.button_dodaj_wynik.setEnabled(False)
        self.ui.newZawodnik_pushButton.setEnabled(False)
        self.ui.sort_seria_button.setEnabled(False)
        self.ui.sort_miejsce_button.setEnabled(False)
        self.ui.tabWidget_zawody.tabBar().setEnabled(False)
        for name in (
            "actionNowe_zawody",
            "actionZarzadzanie_zawodami",
            "actionLista_zawodnikow",
            "actionRozpocznij_wyswietlanie",
            "actionZakoncz_wyswietlanie",
        ):
            act = getattr(self.ui, name, None)
            if act is not None:
                act.setEnabled(False)
        self.ui.exit_To_title_shortcut.setEnabled(False)

    def _wynik_edit_unlock_ui(self) -> None:
        self.ui.button_dodaj_wynik.setEnabled(True)
        self.ui.newZawodnik_pushButton.setEnabled(True)
        self.ui.sort_seria_button.setEnabled(True)
        self.ui.sort_miejsce_button.setEnabled(True)
        self.ui.tabWidget_zawody.tabBar().setEnabled(True)
        for name in (
            "actionNowe_zawody",
            "actionZarzadzanie_zawodami",
            "actionLista_zawodnikow",
            "actionRozpocznij_wyswietlanie",
            "actionZakoncz_wyswietlanie",
        ):
            act = getattr(self.ui, name, None)
            if act is not None:
                act.setEnabled(True)
        self.ui.exit_To_title_shortcut.setEnabled(True)

    def _wynik_edit_begin(self, table_widget: QTableWidget, row: int, handler) -> None:
        self._wynik_edit_table = table_widget
        self._wynik_edit_row = row
        self._wynik_item_changed_handler = handler
        self._wynik_edit_tab_index = self.ui.tabWidget_zawody.currentIndex()
        self._wynik_edit_lock_ui()
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)

    def _wynik_edit_end(self) -> None:
        self._detach_esc_filter_from_targets()
        self._wynik_edit_table = None
        self._wynik_edit_row = None
        self._wynik_item_changed_handler = None
        self._wynik_edit_unlock_ui()

    def _disconnect_wynik_item_changed(self, table_widget: QTableWidget) -> None:
        h = self._wynik_item_changed_handler
        if h is not None:
            try:
                table_widget.itemChanged.disconnect(h)
            except (TypeError, RuntimeError):
                table_widget.itemChanged.disconnect()
        self._wynik_item_changed_handler = None

    def _cancel_incomplete_wynik_row(self) -> None:
        if self._wynik_edit_table is None or self._wynik_edit_row is None:
            return
        self._detach_esc_filter_from_targets()
        tw = self._wynik_edit_table
        row = self._wynik_edit_row
        self._disconnect_wynik_item_changed(tw)
        tw.removeRow(row)
        self._wynik_edit_end()
        if hasattr(self, "nr_serii"):
            delattr(self, "nr_serii")
        self.ui.button_dodaj_wynik.setFocus()

    def _abandon_wynik_edit_state(self) -> None:
        """Rozłącza sygnały edycji wiersza bez usuwania wiersza (np. przed clear() zakładek)."""
        if self._wynik_edit_table is None:
            return
        self._detach_esc_filter_from_targets()
        tw = self._wynik_edit_table
        self._disconnect_wynik_item_changed(tw)
        self._wynik_edit_end()
        if hasattr(self, "nr_serii"):
            delattr(self, "nr_serii")

    def zarejestruj_serie_triggered(self) -> None:
        if self._wynik_edit_table is not None:
            return
        from operator_ui_handler import ZarejestrujSerieDialog
        zawody = self.ui.pageZawody_managment.zawody_data
        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex()))
        if zawody and konkurencja:
            self.zarejestruj_serie_dialog = ZarejestrujSerieDialog(parent=self.ui, zawody=zawody, konkurencja=konkurencja)
            self.zarejestruj_serie_dialog.show_dialog()
    
    def exit_to_title_triggered(self) -> None:
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageTitle)

    def action_lista_zawodnikow_triggered(self, filter_text: str | None = None) -> None:
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawodnicy)
        zawodnicy = zawodnik_data_manager.get_zawodnicy(filter_text=filter_text)
        if zawodnicy is None:
            return
        zawodnicy.sort(key=lambda z: (z.nazwisko, z.imie))
        self.ui.listaZawodnikow.clear()
        for zawodnik in zawodnicy:
            self.ui.listaZawodnikow.addItem(zawodnik.label())

    def action_nowe_zawody_triggered(self) -> None:
        from operator_ui_handler import NoweZawodyDialog

        self.nowe_zawody_dialog = NoweZawodyDialog(parent=self.ui)
        self.nowe_zawody_dialog.signals.zawody_created.connect(self.on_zawody_created)
        self.nowe_zawody_dialog.show_dialog()

    def on_zawody_created(self, zawody_obj) -> None:
        self._abandon_wynik_edit_state()
        self.ui.pageZawody_managment.zawody_data = zawody_obj
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawody_managment)
        self.ui.tabWidget_zawody.clear()
        self.zawody_management_page_entered()

    def zarzadzanie_zawodami_triggered(self) -> None:
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageLista_zawodow)
        list_widget = self.ui.listWidget_lista_zawodow
        list_widget.clear()
        lista_zawodow = zawody_data_manager.get_all_zawody()
        if not lista_zawodow:
            return
        for zawody in lista_zawodow.values():
            item = QListWidgetItem(f"{zawody.nazwa} - {zawody.date_time.strftime(Globals.DATE_FORMAT_PY)}")
            item.setData(Qt.UserRole, zawody.id)
            list_widget.addItem(item)

        if not hasattr(self, "lista_zawodow_menu"):
            from context_menus import ListaZawodowContextMenu

            self.lista_zawodow_menu = ListaZawodowContextMenu(self.ui)
            self.lista_zawodow_menu.zawody_selected.connect(self.on_zawody_selected)

    def on_zawody_selected(self, zawody_obj) -> None:
        self._abandon_wynik_edit_state()
        self.ui.pageZawody_managment.zawody_data = zawody_obj
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawody_managment)
        self.ui.tabWidget_zawody.clear()
        self.zawody_management_page_entered()


    def sort_seria_button_clicked(self) -> None:
        if self._wynik_edit_table is not None:
            return
        self.sort_order = False
        self.sort_wyniki(self.ui.tabWidget_zawody.currentWidget(), self.sort_order)

    def sort_miejsce_button_clicked(self) -> None:
        if self._wynik_edit_table is not None:
            return
        self.sort_order = True
        self.sort_wyniki(self.ui.tabWidget_zawody.currentWidget(), self.sort_order)

    def zawody_management_page_entered(self) -> None:
        self._abandon_wynik_edit_state()
        zawody = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if not zawody:
            return

        font = self.ui.label_zawody_nazwa.font()
        font.setPointSize(self.FONT_SIZE_ZAWODY_LABEL)
        self.ui.label_zawody_nazwa.setFont(font)
        self.ui.label_zawody_nazwa.setText(f"<b>{zawody.nazwa}</b>")

        for konkurencja in zawody.konkurencje.values():
            table_widget = QTableWidget()
            self.ui.tabWidget_zawody.addTab(table_widget, konkurencja.name)
            table_widget.setColumnCount(konkurencja.shots_quantity + 2)
            table_widget.setHorizontalHeaderLabels(
                ["Nr serii"] + [f"Strzał {i + 1}" for i in range(konkurencja.shots_quantity)] + ["Razem"]
            )
            for col in range(table_widget.columnCount()):
                table_widget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
            all_serie = seria_data_manager.get_all_series_by_zawody_and_konkurencja(zawody.id, konkurencja.id)
            if not all_serie:
                continue
            for seria in all_serie:
                wyniki = wynik_data_manager.get_all_wyniki_by_seria_id(seria.id)
                if not wyniki:
                    continue
                row = table_widget.rowCount()
                table_widget.insertRow(row)
                table_widget.setItem(row, 0, QTableWidgetItem(str(seria.number)))
                for wynik in wyniki:
                    table_widget.setItem(row, wynik.nr_strzalu, QTableWidgetItem(str(wynik.punkty)))
                table_widget.setItem(row, table_widget.columnCount() - 1, QTableWidgetItem(str(sum(wynik.punkty for wynik in wyniki))))
            self.sort_order = False
            self.sort_wyniki(table_widget, self.sort_order)
    def dodaj_wynik_clicked(self) -> None:
        if self._wynik_edit_table is not None:
            return
        table_widget = self.ui.tabWidget_zawody.currentWidget()
        if not isinstance(table_widget, QTableWidget):
            return
        row_count = table_widget.rowCount()
        table_widget.insertRow(row_count)
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        table_widget.lista_wynikow_do_sortowania = []

        for col in range(table_widget.columnCount()):
            table_widget.setItem(row_count, col, QTableWidgetItem(""))
        table_widget.setCurrentCell(row_count, 0)
        table_widget.editItem(table_widget.item(row_count, 0))
        handler = partial(self._wynik_row_item_changed, table_widget, row_count)
        table_widget.itemChanged.connect(handler)
        self._wynik_edit_begin(table_widget, row_count, handler)

    def on_table_item_changed(self, table_widget, item, row: int) -> None:
        value = item.text()
        is_shot_column = table_widget.column(item) != 0

        zawody = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if not zawody or not getattr(zawody, "id", None):
            QMessageBox.warning(table_widget, "Błąd", "Zawody nie znalezione")
            return
        zawody_id = zawody.id
        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(
            self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex())
        )
        if not konkurencja:
            QMessageBox.warning(table_widget, "Błąd", "Konkurencja nie znaleziona")
            return

        validator = WynikiTabValidation(value, is_shot_column, zawody_id, konkurencja.id)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(table_widget, "Błąd", message)
            table_widget.blockSignals(True)
            item.setText("")
            table_widget.setCurrentCell(row, table_widget.column(item))
            table_widget.editItem(item)
            table_widget.blockSignals(False)
            QTimer.singleShot(0, self._attach_esc_filter_to_focus)
            return
        if table_widget.column(item) == 0 and value != "":
            self.nr_serii = int(value)
        seria = None
        if hasattr(self, "nr_serii") and self.nr_serii is not None:
            seria = seria_data_manager.get_seria_by_number_and_konkurencja_and_zawody(self.nr_serii, zawody_id, konkurencja.id)
        if not seria and hasattr(self, "nr_serii") and self.nr_serii is not None:
            QMessageBox.warning(table_widget, "Błąd", "Seria nie znaleziona")
            return

        if table_widget.row(item) != row:
            return

        cur_col = table_widget.column(item)
        next_col = cur_col + 1
        last_shot_col = table_widget.columnCount() - 2

        if next_col > last_shot_col:
            table_widget.lista_wynikow_do_sortowania.append(int(value))
            table_widget.lista_wynikow_do_sortowania.sort(reverse=True)
            score = 0
            table_widget.blockSignals(True)
            for col in range(1, table_widget.columnCount() - 1):
                sorted_value = str(table_widget.lista_wynikow_do_sortowania[col - 1])
                table_widget.item(row, col).setText(sorted_value)
                score += int(sorted_value)
                wynik_id = wynik_data_manager.insert_wynik(seria.id, col, sorted_value)
            table_widget.setItem(row, table_widget.columnCount() - 1, QTableWidgetItem(str(score)))
            self._disconnect_wynik_item_changed(table_widget)
            table_widget.blockSignals(False)
            table_widget.clearSelection()
            table_widget.clearFocus()
            self._wynik_edit_end()
            self.sort_wyniki(table_widget, self.sort_order)
            if hasattr(self, "nr_serii"):
                delattr(self, "nr_serii")
            return

        if is_shot_column:
            table_widget.lista_wynikow_do_sortowania.append(int(value))
        table_widget.blockSignals(True)
        table_widget.setCurrentCell(row, next_col)
        table_widget.editItem(table_widget.item(row, next_col))
        table_widget.blockSignals(False)
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)


    def sort_wyniki(self, table_widget: QTableWidget, sort_order: bool) -> None:
        """Sortuje wiersze tabeli wyników.

        - ``sort_order`` False — rosnąco po numerze serii (kolumna 0).
        - ``sort_order`` True — malejąco po sumie (ostatnia kolumna); przy remisie sum
          porównanie leksykograficzne strzałów w kolumnach 1…N (już od najlepszego do
          najgorszego — ten sam układ co przed zapisem do DB).
        """
        rows = table_widget.rowCount()
        cols = table_widget.columnCount()
        if rows < 2 or cols < 2:
            return

        grid: list[list[str]] = []
        for r in range(rows):
            row_texts: list[str] = []
            for c in range(cols):
                cell = table_widget.item(r, c)
                row_texts.append(cell.text() if cell is not None else "")
            grid.append(row_texts)

        grid = sort_wyniki_grid(grid, by_ranking=sort_order)

        was_sorting = table_widget.isSortingEnabled()
        table_widget.setSortingEnabled(False)
        table_widget.blockSignals(True)
        try:
            for r in range(rows):
                for c in range(cols):
                    table_widget.setItem(r, c, QTableWidgetItem(grid[r][c]))
        finally:
            table_widget.blockSignals(False)
            table_widget.setSortingEnabled(was_sorting)

    def set_lista_zawodnikow_completer(self) -> None:
        self.lista_zawodnikow_model = QStringListModel()
        self.lista_zawodnikow_completer = QCompleter(self.lista_zawodnikow_model)
        self.lista_zawodnikow_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.lista_zawodnikow_completer.setFilterMode(Qt.MatchContains)
        self.ui.lineEditWyszukiwanie_zawodnikow.setCompleter(self.lista_zawodnikow_completer)

        layout = self.ui.pageZawodnicy.layout()
        self.lista_zawodnikow_popup_spacer = QWidget()
        self.lista_zawodnikow_popup_spacer.setFixedHeight(30)
        layout.removeWidget(self.ui.listaZawodnikow)
        layout.addWidget(self.lista_zawodnikow_popup_spacer, 2, 0, 1, 1)
        layout.addWidget(self.ui.listaZawodnikow, 3, 0, 1, 1)
        self.lista_zawodnikow_popup_spacer.hide()

    def clients_search_changed(self, line_edit) -> None:
        text = line_edit.text()
        if len(text) < self.MIN_SEARCH_LENGTH:
            self.lista_zawodnikow_model.setStringList([])
            self.timer.stop()
            self.lista_zawodnikow_popup_spacer.hide()
            self.action_lista_zawodnikow_triggered(filter_text=None)
            return

        zawodnicy = zawodnik_data_manager.get_zawodnicy(filter_text=text) or []
        names = [z.label() for z in zawodnicy]
        self.lista_zawodnikow_model.setStringList(names)
        self.lista_zawodnikow_popup_spacer.setVisible(bool(zawodnicy))
        self.action_lista_zawodnikow_triggered(filter_text=text)

        self.timer.stop()
        self.timer.start(self.SEARCH_DEBOUNCE_MS)

    def on_debounce_timeout(self) -> None:
        if self.ui.stackedWidget.currentWidget() == self.ui.pageZawodnicy:
            self.ui.lineEditWyszukiwanie_zawodnikow.textEdited.connect(
                lambda: self.clients_search_changed(self.ui.lineEditWyszukiwanie_zawodnikow)
            )


