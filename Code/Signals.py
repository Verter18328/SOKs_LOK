from Globals import Globals
Globals.setMainDirectory()
from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMessageBox, QHeaderView, QWidget, QListWidgetItem, QMenu
from PySide6.QtCore import Qt, Signal, QObject
from DataManager import client_data_manager, zawody_data_manager, New_zawody
from DataValidation import New_zawody_data_validation


class Signals_new_competition_dialog(QObject):
    zawody_created = Signal(object)  # Sygnał przekazujący obiekt New_zawody
    
    def __init__(self, UI, parent_window=None):
        super().__init__()
        self.UI = UI
        self.parent_window = parent_window
        self.KONKURENCJE = Globals.KONKURENCJE
        self.connect_signals()
    def connect_signals(self):
        for idx, konkurencja in enumerate(self.KONKURENCJE.keys(), start=1):
            comboBox = getattr(self.UI, f'comboBox_konkurencja{idx}')
            comboBox.currentIndexChanged.connect(lambda index, box_idx=idx, cb=comboBox: self.display_comboBoxes(box_idx, cb))
        self.UI.buttonBox.accepted.disconnect()
        self.UI.buttonBox.accepted.connect(self.accepted)
    def display_comboBoxes(self, last_visible_comboBox_number, current_comboBox):
        selected_text = current_comboBox.currentText()
        if selected_text != 'Puste':  # Pokaż następny comboBox tylko gdy wybrano konkretną konkurencję, a nie "Puste"
            try:
                # Usuń wybraną konkurencję ze wszystkich kolejnych comboBoxów
                for comboBox_number in range(1, len(self.KONKURENCJE) + 1):
                    if comboBox_number > last_visible_comboBox_number:
                        comboBox_to_update = getattr(self.UI, f'comboBox_konkurencja{comboBox_number}')
                        index_to_remove = comboBox_to_update.findText(selected_text)
                        if index_to_remove != -1:
                            comboBox_to_update.removeItem(index_to_remove)

                # Pokaż następny comboBox i label
                next_comboBox = getattr(self.UI, f'comboBox_konkurencja{last_visible_comboBox_number + 1}')
                next_comboBox.show()
                label = getattr(self.UI, f'label_{last_visible_comboBox_number + 1}')
                label.show()
            except AttributeError:
                # Jeśli nie ma więcej comboBoxów, po prostu przejdź
                pass
    def accepted(self):
        selected_nazwa = self.UI.lineEdit_nazwa.text()
        selected_dateTime = self.UI.dateTime_input.dateTime().toString('HH:mm dd/MM/yyyy')
        selected_konkurencje = []
        for comboBox_number in range(1, len(self.KONKURENCJE) + 1):
            comboBox = getattr(self.UI, f'comboBox_konkurencja{comboBox_number}')
            selected_text = comboBox.currentText()
            if selected_text != 'Puste':
                for key, value in self.KONKURENCJE.items():
                    if value == selected_text:
                        selected_konkurencje.append(key)
        validator = New_zawody_data_validation(selected_nazwa, selected_dateTime, selected_konkurencje)
        is_valid, message = validator.is_valid_result
        if is_valid:
            # Tutaj można dodać kod do zapisania nowych zawodów do bazy danych
            zawody_obj = New_zawody(selected_nazwa, selected_dateTime, selected_konkurencje)
            setattr(self, f'zawody_{selected_nazwa}', zawody_obj)
            self.UI.close()
            # Emituj sygnał z obiektom zawodów
            self.zawody_created.emit(zawody_obj)
        else:
            QMessageBox.warning(self.UI, "Błędne dane", message)


class Signals_operator_window:
    def __init__(self, UI):
        self.UI = UI
        self.connect_signals()
    def connect_signals(self):
        self.UI.actionLista_zawodnikow.triggered.connect(self.actionLista_zawodnikow_triggered)
        self.UI.exit_To_title_shortcut = QShortcut(QKeySequence("Esc"), self.UI)
        self.UI.exit_To_title_shortcut.activated.connect(self.exit_to_title_triggered)
        self.UI.actionNowe_zawody.triggered.connect(self.actionNowe_zawody_triggered)
        self.UI.actionOtworz_zawody.triggered.connect(self.otworz_zawody_triggered)
        self.UI.button_dodaj_wynik.clicked.connect(self.dodaj_wynik_clicked)
    def on_zawody_created(self, zawody_obj):
        # Obsługa sygnału po utworzeniu nowych zawodów
        self.UI.pageZawody_managment.zawody_data = zawody_obj
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        self.UI.tabWidget_zawody.clear()
        self.zawody_managment_page_entered()
            
    def actionLista_zawodnikow_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawodnicy)
        zawodnicy = client_data_manager.get_clients()
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
        dialog = Nowe_zawody_dialog(parent=self.UI)
        # Podłącz sygnał z dialogu
        dialog.signals.zawody_created.connect(self.on_zawody_created)
        dialog.show_dialog()
    def zawody_managment_page_entered(self):
        zawody = getattr(self.UI.pageZawody_managment, 'zawody_data', None)
        if not zawody:
            return
        zawody_name = zawody.nazwa
        font = self.UI.label_zawody_nazwa.font()
        font.setPointSize(16)
        self.UI.label_zawody_nazwa.setFont(font)
        self.UI.label_zawody_nazwa.setText(f"<b>{zawody_name}</b>")
        for konkurencja in zawody.konkurencje_ids_dict.keys():
            tab_name = konkurencja.split('_')[0]
            match tab_name:
                case 'kbks':
                    tab_name = 'KBKS'
                case 'karabinekPneumatyczny':
                    tab_name = 'Karabinek Pneumatyczny'
                case 'pistoletPneumatyczny':
                    tab_name = 'Pistolet Pneumatyczny'
                case 'pistoletBocznyZapłon':
                    tab_name = 'Pistolet Boczny Zapłon'
                case _:
                    pass  # Pozostaw oryginalną nazwę, jeśli nie pasuje do żadnego przypadku
            ilosc_strzalow = konkurencja.split('_')[2]
            match ilosc_strzalow:
                case '5strz':
                    ui_path = Globals.UI_PATHS_DICT['5_SHOOTS_TABLE']
                case '10strz':
                    ui_path = Globals.UI_PATHS_DICT['10_SHOOTS_TABLE']
                case 'zapadki':
                    ui_path = Globals.UI_PATHS_DICT['ZAPADKI_TABLE']
                case _:
                    print(f"Unknown competition type: {ilosc_strzalow}")
                    continue  # Pomijaj nieznane konkurencje
            tabWidget = self.UI.tabWidget_zawody
            newTab = Globals.UI_LOADER.load(ui_path)
            newTab.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            newTab.tableWidget.verticalHeader().setVisible(False)  # Ukryj etykiety wierszy
            tabWidget.addTab(newTab, tab_name)
    def otworz_zawody_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageLista_zawodow)
        listWidget = self.UI.listWidget_lista_zawodow
        listWidget.clear()
        lista_zawodow = zawody_data_manager.get_all_zawody()
        for zawody in lista_zawodow:
            id = zawody['id']
            nazwa = zawody['nazwa']
            data = zawody['data']
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

            
