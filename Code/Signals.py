from Globals import Globals
Globals.setMainDirectory()
from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMessageBox, QHeaderView, QListWidgetItem, QCompleter, QSpacerItem, QSizePolicy, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, Signal, QObject, QStringListModel, QTimer, QEvent
from DataManager import client_data_manager, zawody_data_manager, konkurencja_data_manager
from DataValidation import New_zawody_data_validation, New_konkurencja_data_validation


class Signals_kreator_konkurencji_dialog(QObject):
    konkurencja_created = Signal(object)  # Sygnał przekazujący obiekt konkurencji
    
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
            self.konkurencja_created.emit(konkurencja_obj)  # Emituj sygnał z obiektem konkurencji
        else:
            QMessageBox.warning(self.UI, "Błąd", message)

class Signals_new_competition_dialog(QObject):
    zawody_created = Signal(object)  # Sygnał przekazujący obiekt New_zawody
    
    def __init__(self, UI, parent_window=None):
        super().__init__()
        self.UI = UI
        self.parent_window = parent_window
        self.konkurencje = {}
        self.connect_signals()
    def connect_signals(self):
        self.UI.button_dodaj_konkurencje.clicked.connect(self.new_konkurencja)
        self.UI.buttonBox_zawody.accepted.connect(self.accepted)
        self.UI.buttonBox_zawody.rejected.connect(self.UI.close)
    def new_konkurencja(self):
        from OperatorUI_Handler import Kreator_konkurencji_dialog
        self.kreator_dialog = Kreator_konkurencji_dialog()
        self.kreator_dialog.signals.konkurencja_created.connect(self.on_konkurencja_created)
        self.kreator_dialog.show_dialog()
    def on_konkurencja_created(self, konkurencja_obj):
        self.UI.konkurencje_list.addItem(f"{konkurencja_obj.nazwa} - {konkurencja_obj.ilosc_strzalow} strzałów")
        self.konkurencje[konkurencja_obj.nazwa] = konkurencja_obj
    def accepted(self):
        selected_nazwa = self.UI.lineEdit_nazwa_zawodow.text()
        selected_dateTime = self.UI.dateTimeEdit_data_zawodow.dateTime().toString(Globals.TIMESTAMP_FORMAT_QT)
        selected_konkurencje = {name: obj for name, obj in self.konkurencje.items() if self.UI.konkurencje_list.findItems(f"{name} - {obj.ilosc_strzalow} strzałów", Qt.MatchExactly)}
        validator = New_zawody_data_validation(selected_nazwa, selected_dateTime, selected_konkurencje)
        is_valid, message = validator.is_valid_result
        if is_valid:
            zawody_obj = zawody_data_manager.insert_zawody(selected_nazwa, selected_dateTime, selected_konkurencje)
            self.zawody_created.emit(zawody_obj)  # Emituj sygnał z obiektem zawodów
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
        # Obsługa sygnału po utworzeniu nowych zawodów
        self.UI.pageZawody_managment.zawody_data = zawody_obj
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        self.UI.tabWidget_zawody.clear()
        self.zawody_managment_page_entered()
            
    def actionLista_zawodnikow_triggered(self, filter=None):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawodnicy)
        zawodnicy = client_data_manager.get_clients(filter=filter)
        if zawodnicy is not None:
            zawodnicy.sort(key=lambda x: (x['nazwisko'], x['imie']))
            self.UI.listaZawodnikow.clear()
            for zawodnik in zawodnicy:
                imie_nazwisko = f"{zawodnik['imie']} {zawodnik['nazwisko']}"
                self.UI.listaZawodnikow.addItem(imie_nazwisko)

    def exit_to_title_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageTitle)
    def actionNowe_zawody_triggered(self):
        from OperatorUI_Handler import Nowe_zawody_dialog
        self.nowe_zawody_dialog = Nowe_zawody_dialog(parent=self.UI)
        # Podłącz sygnał z dialogu
        self.nowe_zawody_dialog.signals.zawody_created.connect(self.on_zawody_created)
        self.nowe_zawody_dialog.show_dialog()
    def zawody_managment_page_entered(self):
        zawody = getattr(self.UI.pageZawody_managment, 'zawody_data', None)
        if not zawody:
            return
        zawody_name = zawody.nazwa
        font = self.UI.label_zawody_nazwa.font()
        font.setPointSize(16)
        self.UI.label_zawody_nazwa.setFont(font)
        self.UI.label_zawody_nazwa.setText(f"<b>{zawody_name}</b>")
        pass
    def zarzadzanie_zawodami_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageLista_zawodow)
        listWidget = self.UI.listWidget_lista_zawodow
        listWidget.clear()
        lista_zawodow = zawody_data_manager.get_all_zawody()
        for zawody in lista_zawodow:
            id = zawody.id
            nazwa = zawody.nazwa
            data = zawody.dateTime.strftime(Globals.DATE_FORMAT_PY)
            list_item_text = f"{nazwa} - {data}"
            item = QListWidgetItem(list_item_text)
            item.setData(Qt.UserRole, id)  # Przechowuj ID zawodów w danych użytkownika
            listWidget.addItem(item)
        
        # Inicjalizuj context menu jeśli jeszcze nie istnieje
        if not hasattr(self, 'lista_zawodow_menu'):
            from ContextMenus import lista_zawodow_context_menu
            self.lista_zawodow_menu = lista_zawodow_context_menu(self.UI)
            self.lista_zawodow_menu.zawody_selected.connect(self.on_zawody_selected)
    
    def on_zawody_selected(self, zawody_obj):
        # Obsługa otwierania zawodów z listy
        self.UI.pageZawody_managment.zawody_data = zawody_obj
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        self.UI.tabWidget_zawody.clear()
        self.zawody_managment_page_entered()

    def dodaj_wynik_clicked(self):
        tableWidget = self.UI.tabWidget_zawody.currentWidget().tableWidget
        row_count = tableWidget.rowCount()
        tableWidget.insertRow(row_count)

    def set_lista_zawodnikow_completer(self):
        self.lista_zawodnikow_model = QStringListModel()
        self.lista_zawodnikow_completer = QCompleter(self.lista_zawodnikow_model)
        self.lista_zawodnikow_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.lista_zawodnikow_completer.setFilterMode(Qt.MatchContains)
        # Pobierz layout zawierający lineEdit i listę
        self.layout = self.UI.pageZawodnicy.layout()
        # Utwórz spacer jako widget
        self.lista_zawodnikow_popup_spacer = QWidget()
        self.lista_zawodnikow_popup_spacer.setFixedHeight(30)
        # Dodaj spacer do grid layout na pozycji (2, 0) i przesuń listę na (3, 0)
        self.layout.removeWidget(self.UI.listaZawodnikow)
        self.layout.addWidget(self.lista_zawodnikow_popup_spacer, 2, 0, 1, 1)
        self.layout.addWidget(self.UI.listaZawodnikow, 3, 0, 1, 1)
        self.lista_zawodnikow_popup_spacer.hide()  # Ukryj na początek
        self.UI.lineEditWyszukiwanie_zawodnikow.setCompleter(self.lista_zawodnikow_completer)

    
    def clients_search_changed(self, lineEdit):
        text = lineEdit.text()
        if len(text) < 3:
            self.lista_zawodnikow_model.setStringList([])
            self.timer.stop()
            self.lista_zawodnikow_popup_spacer.hide()  # Ukryj spacer
            self.actionLista_zawodnikow_triggered(filter=None)
            return
        clients = client_data_manager.get_clients(filter=text)
        data = []
        for client in clients:
            imie = client['imie']
            nazwisko = client['nazwisko']
            data.append(f'{imie} {nazwisko}')
        self.lista_zawodnikow_model.setStringList(data)
        # Pokaż spacer gdy są wyniki
        if data:
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