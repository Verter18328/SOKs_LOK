"""Obsługa sygnałów i logika UI głównego okna operatora.

Odpowiada m.in. za:
- nawigację między stronami (stacked widget),
- wyszukiwanie zawodników z debounce,
- zarządzanie zawodami i tabelami wyników per konkurencja,
- tryb edycji wiersza wyniku (blokada UI, Esc, przenoszenie między zakładkami).
"""

from functools import partial
import subprocess
from globals import Globals
from context_menus import ZawodnicyListContextMenu

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
from sort_methods import WynikiSorter


class _WynikRowEscapeFilter(QObject):
    """Filtr zdarzeń: Esc podczas edycji komórki anuluje cały wiersz wyniku.

    QLineEdit domyślnie połyka Esc (czyści tylko tekst komórki). Filtr przechwytuje
    klawisz wcześniej i deleguje anulowanie do ``SignalsOperatorWindow``.
    """

    def __init__(self, owner: "SignalsOperatorWindow") -> None:
        super().__init__(owner.ui)
        self._owner = owner

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        """Przechwytuje Esc tylko na stronie zarządzania zawodami w trakcie edycji wiersza."""
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

    SEARCH_DEBOUNCE_MS: int = 500  # opóźnienie przed ponownym podpięciem sygnału wyszukiwania
    MIN_SEARCH_LENGTH: int = 3  # minimalna długość frazy do filtrowania listy zawodników
    FONT_SIZE_ZAWODY_LABEL: int = 16

    def __init__(self, ui) -> None:
        """Inicjalizuje stan okna, completer wyszukiwania i podłącza sygnały Qt."""
        self.ui = ui
        self.sort_order: bool = False  # False = po nr serii, True = po miejscu (suma + tie-break)
        self._wyniki_sorter = WynikiSorter()
        # Stan sesji edycji pojedynczego wiersza wyniku (dodawanie strzałów kolumna po kolumnie):
        self._wynik_edit_table: QTableWidget | None = None
        self._wynik_edit_row: int | None = None
        self._wynik_edit_tab_index: int = 0  # zakładka, na której rozpoczęto edycję
        self._wynik_programmatic_tab_switch: bool = False  # True przy zmianie zakładki z kodu (np. przeniesienie wiersza)
        self._wynik_item_changed_handler = None
        self._wynik_edit_mode: str | None = None  # 'add' — nowy wiersz, 'edit' — istniejący wynik
        self._wynik_edit_row_snapshot: list[str] | None = None
        self._wynik_edit_cell_original: str | None = None
        self._wynik_esc_filter = _WynikRowEscapeFilter(self)
        self._esc_filter_targets: list[QWidget] = []  # widgety z aktywnym filtrem Esc
        self.set_lista_zawodnikow_completer()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.connect_signals()
        self.zawodnicy_list_context_menu = ZawodnicyListContextMenu(self.ui)
        self.zawodnicy_list_context_menu.zawodnik_updated.connect(self._refresh_lista_zawodnikow)

    def connect_signals(self) -> None:
        """Podłącza wszystkie sygnały UI do metod obsługi zdarzeń."""
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
        if hasattr(self.ui, "zamknij_zawody_button"):
            self.ui.zamknij_zawody_button.setEnabled(False)
            self.ui.zamknij_zawody_button.setToolTip(
                "Zamykanie zawodów (blokada edycji, druk) — funkcja w przygotowaniu."
            )
        self.ui.start_button.clicked.connect(self.lista_startow_clicked)

    def _escape_shortcut_triggered(self) -> None:
        """Esc globalny: anuluje edycję wyniku albo wraca na ekran tytułowy."""
        if (
            self._wynik_edit_table is not None
            and self.ui.stackedWidget.currentWidget() == self.ui.pageZawody_managment
        ):
            self._cancel_incomplete_wynik_row()
            return
        self.exit_to_title_triggered()

    def _tab_zawody_changed_while_editing(self, index: int) -> None:
        """Blokuje ręczną zmianę zakładki konkurencji w trakcie edycji wiersza wyniku."""
        if self._wynik_edit_table is None:
            return
        if self._wynik_programmatic_tab_switch:
            self._wynik_edit_tab_index = index
            return
        if self.ui.tabWidget_zawody.widget(index) is self._wynik_edit_table:
            return
        self.ui.tabWidget_zawody.blockSignals(True)
        self.ui.tabWidget_zawody.setCurrentIndex(self._wynik_edit_tab_index)
        self.ui.tabWidget_zawody.blockSignals(False)

    def _tab_index_for_konkurencja(self, konkurencja_name: str) -> int | None:
        """Zwraca indeks zakładki o podanej nazwie konkurencji lub ``None``."""
        for i in range(self.ui.tabWidget_zawody.count()):
            if self.ui.tabWidget_zawody.tabText(i) == konkurencja_name:
                return i
        return None

    def _move_wynik_edit_to_konkurencja_tab(
        self,
        source_table: QTableWidget,
        source_row: int,
        target_tab_index: int,
        nr_serii: int,
    ) -> None:
        """Przenosi niedokończony wiersz wyniku do zakładki właściwej konkurencji serii.

        Wywoływane, gdy operator wpisze nr serii należący do innej konkurencji niż bieżąca
        zakładka — wiersz jest usuwany ze źródła i kontynuowany od kolumny pierwszego strzału.
        """
        self._disconnect_wynik_item_changed(source_table)
        source_table.blockSignals(True)
        source_table.removeRow(source_row)
        source_table.blockSignals(False)

        self._wynik_programmatic_tab_switch = True
        self.ui.tabWidget_zawody.setCurrentIndex(target_tab_index)
        self._wynik_programmatic_tab_switch = False

        target_table = self.ui.tabWidget_zawody.widget(target_tab_index)
        if not isinstance(target_table, QTableWidget):
            self._wynik_edit_end()
            return

        row = target_table.rowCount()
        target_table.insertRow(row)
        target_table.setSelectionMode(QAbstractItemView.SingleSelection)
        target_table.setSelectionBehavior(QAbstractItemView.SelectItems)
        target_table.lista_wynikow_do_sortowania = []
        for col in range(target_table.columnCount()):
            target_table.setItem(row, col, QTableWidgetItem(""))
        target_table.item(row, 0).setText(str(nr_serii))

        handler = partial(self._wynik_row_item_changed, target_table, row)
        target_table.itemChanged.connect(handler)
        self._wynik_edit_table = target_table
        self._wynik_edit_row = row
        self._wynik_edit_tab_index = target_tab_index
        self._wynik_item_changed_handler = handler

        target_table.blockSignals(True)
        target_table.setCurrentCell(row, 1)
        target_table.editItem(target_table.item(row, 1))
        target_table.blockSignals(False)
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)

    def _wynik_row_item_changed(self, table_widget: QTableWidget, row: int, item: QTableWidgetItem) -> None:
        """Mostek dla ``partial`` — przekazuje edycję komórki do ``on_table_item_changed``."""
        self.on_table_item_changed(table_widget, item, row)

    def _detach_esc_filter_from_targets(self) -> None:
        """Usuwa filtr Esc ze wszystkich widgetów, na których był zainstalowany."""
        for w in self._esc_filter_targets:
            try:
                w.removeEventFilter(self._wynik_esc_filter)
            except (RuntimeError, TypeError):
                pass
        self._esc_filter_targets = []

    def _attach_esc_filter_to_focus(self) -> None:
        """Instaluje filtr Esc na tabeli i aktywnym edytorze komórki (QLineEdit)."""
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
        """Wyłącza elementy UI, które mogłyby przerwać edycję wiersza wyniku."""
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
        """Przywraca dostępność elementów UI po zakończeniu lub anulowaniu edycji."""
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
        """Rozpoczyna sesję edycji wiersza: zapisuje stan, blokuje UI, aktywuje filtr Esc."""
        self._wynik_edit_table = table_widget
        self._wynik_edit_row = row
        self._wynik_item_changed_handler = handler
        self._wynik_edit_tab_index = self.ui.tabWidget_zawody.currentIndex()
        self._wynik_edit_lock_ui()
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)

    def _wynik_edit_end(self) -> None:
        """Kończy sesję edycji wiersza i czyści powiązany stan wewnętrzny."""
        self._detach_esc_filter_from_targets()
        self._wynik_edit_table = None
        self._wynik_edit_row = None
        self._wynik_item_changed_handler = None
        self._wynik_edit_mode = None
        self._wynik_edit_row_snapshot = None
        self._wynik_edit_cell_original = None
        self._wynik_edit_unlock_ui()

    def _disconnect_wynik_item_changed(self, table_widget: QTableWidget) -> None:
        """Odłącza handler ``itemChanged`` powiązany z bieżącą edycją wiersza."""
        h = self._wynik_item_changed_handler
        if h is not None:
            try:
                table_widget.itemChanged.disconnect(h)
            except (TypeError, RuntimeError):
                table_widget.itemChanged.disconnect()
        self._wynik_item_changed_handler = None

    def _cancel_incomplete_wynik_row(self) -> None:
        """Anuluje edycję wyniku (Esc): usuwa nowy wiersz albo przywraca stary."""
        if self._wynik_edit_table is None or self._wynik_edit_row is None:
            return
        self._detach_esc_filter_from_targets()
        tw = self._wynik_edit_table
        row = self._wynik_edit_row
        self._disconnect_wynik_item_changed(tw)
        if self._wynik_edit_mode == "edit" and self._wynik_edit_row_snapshot is not None:
            tw.blockSignals(True)
            for col, text in enumerate(self._wynik_edit_row_snapshot):
                cell = tw.item(row, col)
                if cell is not None:
                    cell.setText(text)
                else:
                    tw.setItem(row, col, self._wynik_table_item(text, editable=col not in (0, tw.columnCount() - 1)))
            tw.blockSignals(False)
        else:
            tw.removeRow(row)
            if hasattr(self, "nr_serii"):
                delattr(self, "nr_serii")
        self._wynik_edit_end()
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
        """Otwiera dialog rejestracji serii dla bieżących zawodów i konkurencji."""
        if self._wynik_edit_table is not None:
            return
        from operator_ui_handler import ZarejestrujSerieDialog
        zawody = self.ui.pageZawody_managment.zawody_data
        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex()))
        if zawody and konkurencja:
            self.zarejestruj_serie_dialog = ZarejestrujSerieDialog(parent=self.ui, zawody=zawody, konkurencja=konkurencja)
            self.zarejestruj_serie_dialog.show_dialog()
    
    def exit_to_title_triggered(self) -> None:
        """Przełącza stacked widget na ekran tytułowy."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageTitle)

    def action_lista_zawodnikow_triggered(self, filter_text: str | None = None) -> None:
        """Wyświetla listę zawodników, opcjonalnie filtrowaną po tekście wyszukiwania."""

        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawodnicy)
        zawodnicy = zawodnik_data_manager.get_zawodnicy(filter_text=filter_text)
        if zawodnicy is None:
            return
        zawodnicy.sort(key=lambda z: (z.nazwisko, z.imie))
        self.ui.listaZawodnikow.clear()
        for zawodnik in zawodnicy:
            item = QListWidgetItem(zawodnik.label())
            item.setData(Qt.UserRole, zawodnik.id)
            self.ui.listaZawodnikow.addItem(item)

    def _refresh_lista_zawodnikow(self) -> None:
        """Odświeża listę zawodników z zachowaniem aktywnego filtra wyszukiwania."""
        text = self.ui.lineEditWyszukiwanie_zawodnikow.text()
        filter_text = text if len(text) >= self.MIN_SEARCH_LENGTH else None
        self.action_lista_zawodnikow_triggered(filter_text=filter_text)

    def action_nowe_zawody_triggered(self) -> None:
        """Otwiera dialog tworzenia nowych zawodów."""
        from operator_ui_handler import NoweZawodyDialog

        self.nowe_zawody_dialog = NoweZawodyDialog(parent=self.ui)
        self.nowe_zawody_dialog.signals.zawody_created.connect(self.on_zawody_created)
        self.nowe_zawody_dialog.show_dialog()

    def on_zawody_created(self, zawody_obj) -> None:
        """Po utworzeniu zawodów — przełącza na stronę zarządzania i buduje zakładki wyników."""
        self._abandon_wynik_edit_state()
        self.ui.pageZawody_managment.zawody_data = zawody_obj
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawody_managment)
        self.ui.tabWidget_zawody.clear()
        self.zawody_management_page_entered()

    def lista_startow_clicked(self) -> None:
        """Wyświetla stronę listy startów i podłącza menu kontekstowe (leniwie)."""
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageLista_starty)
        self._refresh_lista_startow()
        if not hasattr(self, "starty_list_menu"):
            from context_menus import StartyListContextMenu

            self.starty_list_menu = StartyListContextMenu(self.ui)
            self.starty_list_menu.seria_changed.connect(self._refresh_lista_startow)

    def _refresh_lista_startow(self) -> None:
        """Buduje listę startów dla bieżących zawodów."""
        list_widget = self.ui.starty_list
        list_widget.clear()
        zawody = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if not zawody:
            return
        starty = seria_data_manager.get_all_series_by_zawody(zawody.id)
        if not starty:
            return
        for start in starty:
            item = QListWidgetItem(f"{start.number} - {start.zawodnik.label()} - {start.konkurencja.label()}")
            item.setData(Qt.UserRole, start.id)
            list_widget.addItem(item)

    def zarzadzanie_zawodami_triggered(self) -> None:
        """Wyświetla listę istniejących zawodów z menu kontekstowym wyboru."""
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
            self.lista_zawodow_menu.zawody_list_changed.connect(self._on_zawody_list_changed)

    def on_zawody_selected(self, zawody_obj) -> None:
        """Po wyborze zawodów z listy — ładuje stronę zarządzania z tabelami wyników."""
        self._abandon_wynik_edit_state()
        self.ui.pageZawody_managment.zawody_data = zawody_obj
        self.ui.stackedWidget.setCurrentWidget(self.ui.pageZawody_managment)
        self.ui.tabWidget_zawody.clear()
        self.zawody_management_page_entered()

    def _on_zawody_list_changed(self) -> None:
        """Odświeża listę zawodów po edycji lub usunięciu z menu kontekstowego."""
        current = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if current and getattr(current, "id", None):
            still_exists = zawody_data_manager.get_zawody_by_id(current.id)
            if not still_exists:
                self.ui.pageZawody_managment.zawody_data = None
                if self.ui.stackedWidget.currentWidget() == self.ui.pageZawody_managment:
                    self.ui.stackedWidget.setCurrentWidget(self.ui.pageLista_zawodow)
        self.zarzadzanie_zawodami_triggered()


    def sort_seria_button_clicked(self) -> None:
        """Sortuje wyniki rosnąco po numerze serii."""
        if self._wynik_edit_table is not None:
            return
        self.sort_order = False
        self.sort_wyniki(self.ui.tabWidget_zawody.currentWidget(), self.sort_order)

    def sort_miejsce_button_clicked(self) -> None:
        """Sortuje wyniki malejąco po miejscu (suma punktów, tie-break po strzałach)."""
        if self._wynik_edit_table is not None:
            return
        self.sort_order = True
        self.sort_wyniki(self.ui.tabWidget_zawody.currentWidget(), self.sort_order)

    def zawody_management_page_entered(self) -> None:
        """Buduje zakładki konkurencji z tabelami wyników dla wybranych zawodów."""
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
            self._setup_wynik_table(table_widget)
            all_serie = seria_data_manager.get_all_series_by_zawody_and_konkurencja(zawody.id, konkurencja.id)
            if not all_serie:
                continue
            sum_col = table_widget.columnCount() - 1
            for seria in all_serie:
                wyniki = wynik_data_manager.get_all_wyniki_by_seria_id(seria.id)
                if not wyniki:
                    continue
                row = table_widget.rowCount()
                table_widget.insertRow(row)
                table_widget.setItem(row, 0, self._wynik_table_item(str(seria.number), editable=False))
                for wynik in wyniki:
                    table_widget.setItem(row, wynik.nr_strzalu, self._wynik_table_item(str(wynik.punkty)))
                table_widget.setItem(
                    row, sum_col, self._wynik_table_item(str(sum(wynik.punkty for wynik in wyniki)), editable=False)
                )
            self.sort_order = False
            self.sort_wyniki(table_widget, self.sort_order)

    def dodaj_wynik_clicked(self) -> None:
        """Dodaje pusty wiersz wyniku i rozpoczyna edycję od kolumny „Nr serii"."""
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
        self._wynik_edit_mode = "add"
        self._wynik_edit_begin(table_widget, row_count, handler)

    @staticmethod
    def _wynik_table_item(text: str, editable: bool = True) -> QTableWidgetItem:
        """Tworzy komórkę tabeli wyników; kolumny tylko do odczytu mają wyłączoną edycję inline."""
        item = QTableWidgetItem(text)
        if not editable:
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        return item

    def _setup_wynik_table(self, table_widget: QTableWidget) -> None:
        """Konfiguruje tabelę wyników: brak edycji inline, double-click uruchamia edycję strzału."""
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        table_widget.setSelectionBehavior(QAbstractItemView.SelectItems)
        table_widget.cellDoubleClicked.connect(partial(self._on_wynik_cell_double_clicked, table_widget))

    def _on_wynik_cell_double_clicked(self, table_widget: QTableWidget, row: int, col: int) -> None:
        """Double-click w komórce strzału — rozpoczyna edycję istniejącego wyniku."""
        self.edit_wynik(table_widget, row, col)

    def edit_wynik(self, table_widget: QTableWidget, row: int, col: int) -> None:
        """Rozpoczyna edycję pojedynczego strzału w istniejącym wierszu (double-click)."""
        if self._wynik_edit_table is not None:
            return
        if row < 0 or col <= 0 or col >= table_widget.columnCount() - 1:
            return

        seria_item = table_widget.item(row, 0)
        if seria_item is None or not seria_item.text().strip():
            return

        item = table_widget.item(row, col)
        if item is None:
            return

        snapshot: list[str] = []
        for c in range(table_widget.columnCount()):
            cell = table_widget.item(row, c)
            snapshot.append(cell.text() if cell is not None else "")

        self._wynik_edit_mode = "edit"
        self._wynik_edit_row_snapshot = snapshot
        self._wynik_edit_cell_original = item.text()

        handler = partial(self._wynik_existing_cell_changed, table_widget, row, col)
        table_widget.itemChanged.connect(handler)
        self._wynik_edit_begin(table_widget, row, handler)

        table_widget.blockSignals(True)
        table_widget.setCurrentCell(row, col)
        table_widget.editItem(item)
        table_widget.blockSignals(False)

    def _wynik_existing_cell_changed(
        self, table_widget: QTableWidget, row: int, col: int, item: QTableWidgetItem
    ) -> None:
        """Po zmianie komórki strzału — walidacja, zapis do DB, przeliczenie sumy i sort w wierszu."""
        if table_widget.row(item) != row or table_widget.column(item) != col:
            return

        value = item.text()
        zawody = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if not zawody or not getattr(zawody, "id", None):
            QMessageBox.warning(table_widget, "Błąd", "Zawody nie znalezione")
            self._reject_wynik_cell_edit(table_widget, item, row)
            return

        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(
            self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex())
        )
        if not konkurencja:
            QMessageBox.warning(table_widget, "Błąd", "Konkurencja nie znaleziona")
            self._reject_wynik_cell_edit(table_widget, item, row)
            return

        validator = WynikiTabValidation(value, True, zawody.id, konkurencja.id)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(table_widget, "Błąd", message)
            self._reject_wynik_cell_edit(table_widget, item, row)
            return

        nr_serii = int(table_widget.item(row, 0).text())
        seria = seria_data_manager.get_seria_by_number_and_zawody(nr_serii, zawody.id)
        if seria is None:
            QMessageBox.warning(table_widget, "Błąd", "Seria nie znaleziona")
            self._reject_wynik_cell_edit(table_widget, item, row)
            return

        last_shot_col = table_widget.columnCount() - 2
        shots: list[int] = []
        for c in range(1, last_shot_col + 1):
            cell = table_widget.item(row, c)
            text = value if c == col else (cell.text() if cell is not None else "")
            if not text.isdigit():
                QMessageBox.warning(table_widget, "Błąd", "Niepełne dane strzałów w wierszu.")
                self._reject_wynik_cell_edit(table_widget, item, row)
                return
            shots.append(int(text))
        shots.sort(reverse=True)

        if not wynik_data_manager.update_wyniki_for_seria(seria.id, shots):
            QMessageBox.warning(table_widget, "Błąd", "Błąd podczas zapisu wyniku")
            self._reject_wynik_cell_edit(table_widget, item, row)
            return

        sum_col = table_widget.columnCount() - 1
        score = sum(shots)
        table_widget.blockSignals(True)
        for i, c in enumerate(range(1, last_shot_col + 1)):
            table_widget.item(row, c).setText(str(shots[i]))
        sum_item = table_widget.item(row, sum_col)
        if sum_item is None:
            table_widget.setItem(row, sum_col, self._wynik_table_item(str(score), editable=False))
        else:
            sum_item.setText(str(score))
        table_widget.blockSignals(False)

        self._disconnect_wynik_item_changed(table_widget)
        table_widget.clearSelection()
        table_widget.clearFocus()
        self._wynik_edit_end()
        self.sort_wyniki(table_widget, self.sort_order)

    def _reject_wynik_cell_edit(
        self, table_widget: QTableWidget, item: QTableWidgetItem, row: int
    ) -> None:
        """Po błędzie walidacji przy edycji — przywraca poprzednią wartość komórki."""
        original = self._wynik_edit_cell_original or ""
        table_widget.blockSignals(True)
        item.setText(original)
        table_widget.setCurrentCell(row, table_widget.column(item))
        table_widget.editItem(item)
        table_widget.blockSignals(False)
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)

    def _reject_wynik_cell_after_warning(
        self, table_widget: QTableWidget, item: QTableWidgetItem, row: int
    ) -> None:
        """Po QMessageBox: czyści komórkę, ustawia fokus z powrotem na nią i odnawia filtr Esc na edytorze."""
        table_widget.blockSignals(True)
        item.setText("")
        table_widget.setCurrentCell(row, table_widget.column(item))
        table_widget.editItem(item)
        table_widget.blockSignals(False)
        QTimer.singleShot(0, self._attach_esc_filter_to_focus)

    def on_table_item_changed(self, table_widget, item, row: int) -> None:
        """Obsługuje wpisanie wartości w komórce w trakcie dodawania wyniku.

        Przepływ kolumn: nr serii → strzały 1…N → suma. Po ostatnim strzale wyniki
        są sortowane malejąco w wierszu, zapisywane do DB i wiersz jest finalizowany.
        Jeśli nr serii należy do innej konkurencji, wiersz jest przenoszony do jej zakładki.
        """
        value = item.text()
        is_shot_column = table_widget.column(item) != 0

        zawody = getattr(self.ui.pageZawody_managment, "zawody_data", None)
        if not zawody or not getattr(zawody, "id", None):
            QMessageBox.warning(table_widget, "Błąd", "Zawody nie znalezione")
            self._reject_wynik_cell_after_warning(table_widget, item, row)
            return
        zawody_id = zawody.id
        konkurencja = konkurencja_data_manager.get_konkurencja_by_name(
            self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex())
        )
        if not konkurencja:
            QMessageBox.warning(table_widget, "Błąd", "Konkurencja nie znaleziona")
            self._reject_wynik_cell_after_warning(table_widget, item, row)
            return

        validator = WynikiTabValidation(value, is_shot_column, zawody_id, konkurencja.id)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(table_widget, "Błąd", message)
            self._reject_wynik_cell_after_warning(table_widget, item, row)
            return
        if table_widget.column(item) == 0 and value != "":
            self.nr_serii = int(value)

        seria = None
        if hasattr(self, "nr_serii") and self.nr_serii is not None:
            seria = seria_data_manager.get_seria_by_number_and_zawody(self.nr_serii, zawody_id)

        if (
            table_widget.column(item) == 0
            and value != ""
            and seria is not None
            and seria.konkurencja.name != self.ui.tabWidget_zawody.tabText(self.ui.tabWidget_zawody.currentIndex())
        ):
            target_tab = self._tab_index_for_konkurencja(seria.konkurencja.name)
            if target_tab is not None:
                self._move_wynik_edit_to_konkurencja_tab(table_widget, row, target_tab, self.nr_serii)
                return

        if table_widget.row(item) != row:
            return

        cur_col = table_widget.column(item)
        next_col = cur_col + 1
        last_shot_col = table_widget.columnCount() - 2

        if next_col > last_shot_col:
            # Ostatni strzał — sortuj malejąco w wierszu, zapisz do DB, policz sumę
            table_widget.lista_wynikow_do_sortowania.append(int(value))
            table_widget.lista_wynikow_do_sortowania.sort(reverse=True)
            score = 0
            table_widget.blockSignals(True)
            for col in range(1, table_widget.columnCount() - 1):
                sorted_value = str(table_widget.lista_wynikow_do_sortowania[col - 1])
                table_widget.item(row, col).setText(sorted_value)
                score += int(sorted_value)
                wynik_data_manager.insert_wynik(seria.id, col, sorted_value)
            sum_col = table_widget.columnCount() - 1
            table_widget.setItem(row, sum_col, self._wynik_table_item(str(score), editable=False))
            seria_cell = table_widget.item(row, 0)
            if seria_cell is not None:
                seria_cell.setFlags(seria_cell.flags() & ~Qt.ItemIsEditable)
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

        grid = self._wyniki_sorter.sort_wyniki_grid(grid, by_ranking=sort_order)

        was_sorting = table_widget.isSortingEnabled()
        table_widget.setSortingEnabled(False)
        table_widget.blockSignals(True)
        try:
            sum_col = cols - 1
            for r in range(rows):
                for c in range(cols):
                    editable = c not in (0, sum_col)
                    table_widget.setItem(r, c, self._wynik_table_item(grid[r][c], editable=editable))
        finally:
            table_widget.blockSignals(False)
            table_widget.setSortingEnabled(was_sorting)

    def set_lista_zawodnikow_completer(self) -> None:
        """Konfiguruje completer wyszukiwania zawodników i spacer pod popup podpowiedzi."""
        self.lista_zawodnikow_model = QStringListModel()
        self.lista_zawodnikow_completer = QCompleter(self.lista_zawodnikow_model)
        self.lista_zawodnikow_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.lista_zawodnikow_completer.setFilterMode(Qt.MatchContains)
        self.ui.lineEditWyszukiwanie_zawodnikow.setCompleter(self.lista_zawodnikow_completer)

        # Spacer zapobiega zasłanianiu listy wyników przez popup completera
        layout = self.ui.pageZawodnicy.layout()
        self.lista_zawodnikow_popup_spacer = QWidget()
        self.lista_zawodnikow_popup_spacer.setFixedHeight(30)
        layout.removeWidget(self.ui.listaZawodnikow)
        layout.addWidget(self.lista_zawodnikow_popup_spacer, 2, 0, 1, 1)
        layout.addWidget(self.ui.listaZawodnikow, 3, 0, 1, 1)
        self.lista_zawodnikow_popup_spacer.hide()

    def clients_search_changed(self, line_edit) -> None:
        """Reaguje na zmianę tekstu wyszukiwania — filtruje listę i odświeża podpowiedzi."""
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
        """Po debounce ponownie podłącza sygnał wyszukiwania (zapobiega pętli textChanged)."""
        if self.ui.stackedWidget.currentWidget() == self.ui.pageZawodnicy:
            self.ui.lineEditWyszukiwanie_zawodnikow.textEdited.connect(
                lambda: self.clients_search_changed(self.ui.lineEditWyszukiwanie_zawodnikow)
            )

    def display_waiting_screen(self) -> None:
        """Wyświetla ekran oczekiwania na drugim monitorze w trybie pełnoekranowym."""
        self.waiting_window = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['WAITING_DISPLAY'])
        self.waiting_window.setGeometry(QApplication.screens()[1].geometry())
        self.waiting_window.setScreen(QApplication.screens()[1])
        self.waiting_window.showFullScreen()
    
    def second_screen_listener(self) -> None:
        """Włącza tryb rozszerzonego pulpitu i czeka na podłączenie drugiego ekranu."""
        subprocess_result = subprocess.run(['DisplaySwitch.exe', '/extend'], capture_output = True, text = True, timeout = 5)
        ok = subprocess_result.returncode == 0
        if not ok:
            QMessageBox.warning(self.ui, "Błąd", "Nie udało się rozszerzyć ekranu")
            return
        if len(QApplication.screens()) >= 2:
            self.display_waiting_screen()
        else:
            QTimer.singleShot(1000, self.second_screen_listener)

    

