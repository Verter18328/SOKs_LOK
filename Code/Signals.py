from Globals import Globals
Globals.setMainDirectory()
from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMessageBox, QHeaderView
from DataManager import client_data_manager, New_zawody
from DataValidation import New_zawody_data_validation


class Signals_new_competition_dialog:
    def __init__(self, UI):
        self.UI = UI
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
            setattr(self, f'zawody_{selected_nazwa}', New_zawody(selected_nazwa, selected_dateTime, selected_konkurencje))
            self.UI.close()
            # Tutaj powinno się otwierać działanie związane z nowo utworzonymi zawodami w oknie głównym
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
        self.UI.Test_shortcut = QShortcut(QKeySequence("F2"), self.UI)
        self.UI.Test_shortcut.activated.connect(self.test_shortcut_triggered)
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
        dialog.show_dialog()
    def test_shortcut_triggered(self):
        # Testowa funkcja do przełączania na zakładkę zarządzania zawodami z przykładową tabelą
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawody_managment)
        tabWidget = self.UI.tabWidget_zawody
        tabWidget.clear()
        newTab = Globals.UI_LOADER.load(Globals.UI_PATHS_DICT['5_SHOOTS_TABLE'])
        newTab.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabWidget.addTab(newTab, "Testowe Zawody")
