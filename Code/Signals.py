from Globals import Globals
Globals.setMainDirectory()

from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QAbstractItemView, QMessageBox, QHeaderView, QListWidgetItem,
    QCompleter, QTableWidget, QTableWidgetItem, QWidget
)
from PySide6.QtCore import Qt, Signal, QObject, QStringListModel, QTimer

from DataManager import client_data_manager, zawody_data_manager, konkurencja_data_manager
from DataValidation import New_zawody_data_validation, New_konkurencja_data_validation, Wyniki_tab_validation


class Signals_kreator_konkurencji_dialog(QObject):
    konkurencja_created = Signal(object)

    def __init__(self, UI, parent_window=None):
        super().__init__()
        self.UI = UI
        self.parent_window = parent_window
        self.connect_signals()

    def connect_signals(self):
        self.UI.buttonBox.accepted.connect(self.accepted)
        self.UI.buttonBox.rejected.connect(self.UI.close)

    def accepted(self):
        shots_quantity = self.UI.spinBox_shots_quantity.value()
        name = self.UI.lineEdit_name.text()
        validator = New_konkurencja_data_validation(shots_quantity, name)
        is_valid, message = validator.is_valid_result
        if is_valid:
            konkurencja_obj = konkurencja_data_manager.insert_konkurencja(name, shots_quantity)
            self.UI.close()
            self.konkurencja_created.emit(konkurencja_obj)
        else:
            QMessageBox.warning(self.UI, "Błąd", message)


class Signals_new_competition_dialog(QObject):
    zawody_created = Signal(object)

    def __init__(self, UI, parent_window=None):
        super().__init__()
        self.UI = UI
        self.parent_window = parent_window
        self.konkurencje = {}
        self.connect_signals()
        self.get_konkurencje()

    def connect_signals(self):
        self.UI.button_dodaj_konkurencje.clicked.connect(self.new_konkurencja)
        self.UI.buttonBox_zawody.accepted.connect(self.accepted)
        self.UI.buttonBox_zawody.rejected.connect(self.UI.close)
        self.UI.comboBox_konkurencje.activated.connect(self.konkurencja_comboBox_selected)

    def get_konkurencje(self):
        konkurencje = konkurencja_data_manager.get_all_konkurencje()
        if not konkurencje:
            return
        for konkurencja in konkurencje.values():
            self.UI.comboBox_konkurencje.addItem(
                f"{konkurencja.name} - {konkurencja.shots_quantity} strzałów", userData=konkurencja
            )
            self.konkurencje[konkurencja.name] = konkurencja

    def konkurencja_comboBox_selected(self, index):
        konkurencja_obj = self.UI.comboBox_konkurencje.itemData(index)
        item = QListWidgetItem(f"{konkurencja_obj.name} - {konkurencja_obj.shots_quantity} strzałów")
        item.setData(Qt.UserRole, konkurencja_obj)
        self.UI.konkurencje_list.addItem(item)

    def new_konkurencja(self):
        from OperatorUI_Handler import Kreator_konkurencji_dialog
        self.kreator_dialog = Kreator_konkurencji_dialog()
        self.kreator_dialog.signals.konkurencja_created.connect(self.on_konkurencja_created)
        self.kreator_dialog.show_dialog()

    def on_konkurencja_created(self, konkurencja_obj):
        item = QListWidgetItem(f"{konkurencja_obj.name} - {konkurencja_obj.shots_quantity} strzałów")
        item.setData(Qt.UserRole, konkurencja_obj)
        self.UI.konkurencje_list.addItem(item)
        self.konkurencje[konkurencja_obj.name] = konkurencja_obj
        for konkurencja in self.konkurencje.values():
            self.UI.comboBox_konkurencje.addItem(konkurencja.name, userData=konkurencja)

    def accepted(self):
        selected_nazwa = self.UI.lineEdit_nazwa_zawodow.text()
        selected_dateTime = self.UI.dateTimeEdit_data_zawodow.dateTime().toString(Globals.TIMESTAMP_FORMAT_QT)
        selected_konkurencje = {
            name: obj for name, obj in self.konkurencje.items()
            if self.UI.konkurencje_list.findItems(f"{name} - {obj.shots_quantity} strzałów", Qt.MatchExactly)
        }
        validator = New_zawody_data_validation(selected_nazwa, selected_dateTime, selected_konkurencje)
        is_valid, message = validator.is_valid_result
        if is_valid:
            zawody_obj = zawody_data_manager.insert_zawody(selected_nazwa, selected_dateTime, selected_konkurencje)
            self.zawody_created.emit(zawody_obj)
            self.UI.close()
        else:
            QMessageBox.warning(self.UI, "Błąd", message)


class Signals_operator_window:
    def __init__(self, UI):
        self.UI = UI
        self.set_lista_zawodnikow_completer()
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.connect_signals()

    def connect_signals(self):
        self.timer.timeout.connect(self.on_debounce_timeout)
        self.UI.actionLista_zawodnikow.triggered.connect(self.actionLista_zawodnikow_triggered)
        self.UI.exit_To_title_shortcut = QShortcut(QKeySequence("Esc"), self.UI)
        self.UI.exit_To_title_shortcut.activated.connect(self.exit_to_title_triggered)
        self.UI.actionNowe_zawody.triggered.connect(self.actionNowe_zawody_triggered)
        self.UI.actionZarzadzanie_zawodami.triggered.connect(self.zarzadzanie_zawodami_triggered)
        self.UI.button_dodaj_wynik.clicked.connect(self.dodaj_wynik_clicked)
        self.UI.lineEditWyszukiwanie_zawodnikow.textChanged.connect(
            lambda: self.clients_search_changed(self.UI.lineEditWyszukiwanie_zawodnikow)
        )

    def on_zawody_created(self, zawody_obj):
        self.UI.pageZawody_managment.zawody_data = zawody_obj
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        self.UI.tabWidget_zawody.clear()
        self.zawody_managment_page_entered()

    def actionLista_zawodnikow_triggered(self, filter=None):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawodnicy)
        zawodnicy = client_data_manager.get_clients(filter=filter)
        if zawodnicy is None:
            return
        zawodnicy.sort(key=lambda x: (x['nazwisko'], x['imie']))
        self.UI.listaZawodnikow.clear()
        for zawodnik in zawodnicy:
            self.UI.listaZawodnikow.addItem(f"{zawodnik['imie']} {zawodnik['nazwisko']}")

    def exit_to_title_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageTitle)

    def actionNowe_zawody_triggered(self):
        from OperatorUI_Handler import Nowe_zawody_dialog
        self.nowe_zawody_dialog = Nowe_zawody_dialog(parent=self.UI)
        self.nowe_zawody_dialog.signals.zawody_created.connect(self.on_zawody_created)
        self.nowe_zawody_dialog.show_dialog()

    def zawody_managment_page_entered(self):
        zawody = getattr(self.UI.pageZawody_managment, 'zawody_data', None)
        if not zawody:
            return
        font = self.UI.label_zawody_nazwa.font()
        font.setPointSize(16)
        self.UI.label_zawody_nazwa.setFont(font)
        self.UI.label_zawody_nazwa.setText(f"<b>{zawody.nazwa}</b>")
        for konkurencja in zawody.konkurencje.values():
            tableWidget = QTableWidget()
            self.UI.tabWidget_zawody.addTab(tableWidget, konkurencja.name)
            tableWidget.setColumnCount(konkurencja.shots_quantity + 2)
            tableWidget.setHorizontalHeaderLabels(
                ["Zawodnik"] + [f"Strzał {i+1}" for i in range(konkurencja.shots_quantity)] + ["Razem"]
            )
            for col in range(tableWidget.columnCount()):
                tableWidget.horizontalHeader().setSectionResizeMode(col, QHeaderView.Stretch)
        # TODO: GENEROWANIE TABELEK

    def zarzadzanie_zawodami_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageLista_zawodow)
        listWidget = self.UI.listWidget_lista_zawodow
        listWidget.clear()
        lista_zawodow = zawody_data_manager.get_all_zawody()
        if not lista_zawodow:
            return
        for zawody in lista_zawodow.values():
            item = QListWidgetItem(f"{zawody.nazwa} - {zawody.dateTime.strftime(Globals.DATE_FORMAT_PY)}")
            item.setData(Qt.UserRole, zawody.id)
            listWidget.addItem(item)
        if not hasattr(self, 'lista_zawodow_menu'):
            from ContextMenus import lista_zawodow_context_menu
            self.lista_zawodow_menu = lista_zawodow_context_menu(self.UI)
            self.lista_zawodow_menu.zawody_selected.connect(self.on_zawody_selected)

    def on_zawody_selected(self, zawody_obj):
        self.UI.pageZawody_managment.zawody_data = zawody_obj
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        self.UI.tabWidget_zawody.clear()
        self.zawody_managment_page_entered()

    def dodaj_wynik_clicked(self):
        tableWidget = self.UI.tabWidget_zawody.currentWidget()
        row_count = tableWidget.rowCount()
        tableWidget.insertRow(row_count)
        tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        tableWidget.setSelectionBehavior(QAbstractItemView.SelectItems)
        tableWidget.lista_wynikow_do_sortowania = []
        for col in range(tableWidget.columnCount()):
            tableWidget.setItem(row_count, col, QTableWidgetItem(""))
        tableWidget.setCurrentCell(row_count, 0)
        tableWidget.editItem(tableWidget.item(row_count, 0))
        tableWidget.itemChanged.connect(lambda item: self.on_table_item_changed(tableWidget, item, row_count))

    def on_table_item_changed(self, tableWidget, item, row):
        value = item.text()
        is_shot_column = tableWidget.column(item) != 0
        validator = Wyniki_tab_validation(value, is_shot_column)
        if not validator.is_valid_result[0]:
            QMessageBox.warning(tableWidget, "Błąd", validator.is_valid_result[1])
            tableWidget.blockSignals(True)
            item.setText("")
            tableWidget.setCurrentCell(row, tableWidget.column(item))
            tableWidget.editItem(item)
            tableWidget.blockSignals(False)
            return

        if tableWidget.row(item) != row:
            return

        cur_col = tableWidget.column(item)
        next_col = cur_col + 1
        last_shot_col = tableWidget.columnCount() - 2

        if next_col > last_shot_col:
            tableWidget.lista_wynikow_do_sortowania.append(int(value))
            tableWidget.lista_wynikow_do_sortowania.sort(reverse=True)
            score = 0
            tableWidget.blockSignals(True)
            for col in range(1, tableWidget.columnCount() - 1):
                sorted_value = str(tableWidget.lista_wynikow_do_sortowania[col - 1])
                tableWidget.item(row, col).setText(sorted_value)
                score += int(sorted_value)
            tableWidget.setItem(row, tableWidget.columnCount() - 1, QTableWidgetItem(str(score)))
            tableWidget.blockSignals(False)
            tableWidget.itemChanged.disconnect()
            tableWidget.clearSelection()
            tableWidget.clearFocus()
            return

        if is_shot_column:
            tableWidget.lista_wynikow_do_sortowania.append(int(value))
        tableWidget.blockSignals(True)
        tableWidget.setCurrentCell(row, next_col)
        tableWidget.editItem(tableWidget.item(row, next_col))
        tableWidget.blockSignals(False)

    def set_lista_zawodnikow_completer(self):
        self.lista_zawodnikow_model = QStringListModel()
        self.lista_zawodnikow_completer = QCompleter(self.lista_zawodnikow_model)
        self.lista_zawodnikow_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.lista_zawodnikow_completer.setFilterMode(Qt.MatchContains)
        self.UI.lineEditWyszukiwanie_zawodnikow.setCompleter(self.lista_zawodnikow_completer)
        layout = self.UI.pageZawodnicy.layout()
        self.lista_zawodnikow_popup_spacer = QWidget()
        self.lista_zawodnikow_popup_spacer.setFixedHeight(30)
        layout.removeWidget(self.UI.listaZawodnikow)
        layout.addWidget(self.lista_zawodnikow_popup_spacer, 2, 0, 1, 1)
        layout.addWidget(self.UI.listaZawodnikow, 3, 0, 1, 1)
        self.lista_zawodnikow_popup_spacer.hide()

    def clients_search_changed(self, lineEdit):
        text = lineEdit.text()
        if len(text) < 3:
            self.lista_zawodnikow_model.setStringList([])
            self.timer.stop()
            self.lista_zawodnikow_popup_spacer.hide()
            self.actionLista_zawodnikow_triggered(filter=None)
            return
        clients = client_data_manager.get_clients(filter=text)
        names = [f"{c['imie']} {c['nazwisko']}" for c in clients]
        self.lista_zawodnikow_model.setStringList(names)
        if names:
            self.lista_zawodnikow_popup_spacer.show()
        else:
            self.lista_zawodnikow_popup_spacer.hide()
        self.actionLista_zawodnikow_triggered(filter=text)
        self.timer.stop()
        self.timer.start(500)

    def on_debounce_timeout(self):
        match self.UI.stackedWidget.currentWidget():
            case self.UI.pageZawodnicy:
                self.UI.lineEditWyszukiwanie_zawodnikow.textEdited.connect(
                    lambda: self.clients_search_changed(self.UI.lineEditWyszukiwanie_zawodnikow)
                )