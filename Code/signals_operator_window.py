"""Obsługa sygnałów i logika UI głównego okna operatora."""

from globals import Globals

Globals.set_main_directory()

from PySide6.QtCore import Qt, QTimer, QStringListModel
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
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


class SignalsOperatorWindow:
    """Logika i obsługa sygnałów głównego okna operatora."""

    SEARCH_DEBOUNCE_MS: int = 500
    MIN_SEARCH_LENGTH: int = 3
    FONT_SIZE_ZAWODY_LABEL: int = 16

    def __init__(self, ui) -> None:
        self.ui = ui
        self.set_lista_zawodnikow_completer()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.connect_signals()

    def connect_signals(self) -> None:
        self.timer.timeout.connect(self.on_debounce_timeout)
        self.ui.actionLista_zawodnikow.triggered.connect(self.action_lista_zawodnikow_triggered)

        self.ui.exit_To_title_shortcut = QShortcut(QKeySequence("Esc"), self.ui)
        self.ui.exit_To_title_shortcut.activated.connect(self.exit_to_title_triggered)

        self.ui.actionNowe_zawody.triggered.connect(self.action_nowe_zawody_triggered)
        self.ui.actionZarzadzanie_zawodami.triggered.connect(self.zarzadzanie_zawodami_triggered)
        self.ui.button_dodaj_wynik.clicked.connect(self.dodaj_wynik_clicked)
        self.ui.lineEditWyszukiwanie_zawodnikow.textChanged.connect(
            lambda: self.clients_search_changed(self.ui.lineEditWyszukiwanie_zawodnikow)
        )
        self.ui.newZawodnik_pushButton.clicked.connect(self.zarejestruj_serie_triggered)

    def zarejestruj_serie_triggered(self) -> None:
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
        self.ui.pageZawody_managment.zawody_data = zawody_obj
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawody_managment)
        self.ui.tabWidget_zawody.clear()
        self.zawody_management_page_entered()

    def zawody_management_page_entered(self) -> None:
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

    def dodaj_wynik_clicked(self) -> None:
        table_widget = self.ui.tabWidget_zawody.currentWidget()
        row_count = table_widget.rowCount()
        table_widget.insertRow(row_count)
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        table_widget.lista_wynikow_do_sortowania = []

        for col in range(table_widget.columnCount()):
            table_widget.setItem(row_count, col, QTableWidgetItem(""))
        table_widget.setCurrentCell(row_count, 0)
        table_widget.editItem(table_widget.item(row_count, 0))
        table_widget.itemChanged.connect(
            lambda item: self.on_table_item_changed(table_widget, item, row_count)
        )

    def on_table_item_changed(self, table_widget, item, row: int) -> None:
        value = item.text()
        is_shot_column = table_widget.column(item) != 0
        if table_widget.column(item) == 0 and value != "":
            self.nr_serii = int(value)
        zawody_id = self.ui.pageZawody_managment.zawody_data.id
        if not zawody_id:
            QMessageBox.warning(table_widget, "Błąd", "Zawody nie znalezione")
            return
        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(
            self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex())
        )
        if not konkurencja:
            QMessageBox.warning(table_widget, "Błąd", "Konkurencja nie znaleziona")
            return
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
            table_widget.blockSignals(False)
            table_widget.itemChanged.disconnect()
            table_widget.clearSelection()
            table_widget.clearFocus()
            return

        if is_shot_column:
            table_widget.lista_wynikow_do_sortowania.append(int(value))
        table_widget.blockSignals(True)
        table_widget.setCurrentCell(row, next_col)
        table_widget.editItem(table_widget.item(row, next_col))
        table_widget.blockSignals(False)

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


