"""Obsługa sygnałów dla dialogów (kreator konkurencji i nowe zawody)."""

from globals import Globals

Globals.set_main_directory()

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QListWidgetItem, QMessageBox

from data_manager import konkurencja_data_manager, zawody_data_manager
from data_validation import NewKonkurencjaDataValidation, NewZawodyDataValidation


class SignalsKreatorKonkurencjiDialog(QObject):
    """Obsługa sygnałów w dialogu tworzenia konkurencji."""

    konkurencja_created = Signal(object)

    def __init__(self, ui, parent_window=None) -> None:
        super().__init__()
        self.ui = ui
        self.parent_window = parent_window
        self.connect_signals()

    def connect_signals(self) -> None:
        self.ui.buttonBox.accepted.connect(self.accepted)
        self.ui.buttonBox.rejected.connect(self.ui.close)

    def accepted(self) -> None:
        shots_quantity = self.ui.spinBox_shots_quantity.value()
        name = self.ui.lineEdit_name.text()
        validator = NewKonkurencjaDataValidation(shots_quantity, name)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(self.ui, "Błąd", message)
            return
        konkurencja_obj = konkurencja_data_manager.insert_konkurencja(name, shots_quantity)
        self.ui.close()
        self.konkurencja_created.emit(konkurencja_obj)


class SignalsNewCompetitionDialog(QObject):
    """Obsługa dialogu tworzenia nowych zawodów."""

    zawody_created = Signal(object)

    def __init__(self, ui, parent_window=None) -> None:
        super().__init__()
        self.ui = ui
        self.parent_window = parent_window
        self.konkurencje: dict = {}
        self.connect_signals()
        self.get_konkurencje()

    def connect_signals(self) -> None:
        self.ui.button_dodaj_konkurencje.clicked.connect(self.new_konkurencja)
        self.ui.buttonBox_zawody.accepted.connect(self.accepted)
        self.ui.buttonBox_zawody.rejected.connect(self.ui.close)
        self.ui.comboBox_konkurencje.activated.connect(self.konkurencja_combobox_selected)

    def get_konkurencje(self) -> None:
        konkurencje = konkurencja_data_manager.get_all_konkurencje()
        if not konkurencje:
            return
        self.konkurencje = {k.name: k for k in konkurencje.values()}
        self._refresh_konkurencje_combobox()

    def _refresh_konkurencje_combobox(self) -> None:
        self.ui.comboBox_konkurencje.clear()
        for konkurencja in self.konkurencje.values():
            self.ui.comboBox_konkurencje.addItem(konkurencja.label(), userData=konkurencja)

    def _add_konkurencja_to_list_widget(self, konkurencja_obj) -> None:
        item = QListWidgetItem(konkurencja_obj.label())
        item.setData(Qt.UserRole, konkurencja_obj)
        self.ui.konkurencje_list.addItem(item)

    def _get_selected_konkurencje(self) -> dict:
        selected_konkurencje = {}
        for row in range(self.ui.konkurencje_list.count()):
            konkurencja_obj = self.ui.konkurencje_list.item(row).data(Qt.UserRole)
            if konkurencja_obj:
                selected_konkurencje[konkurencja_obj.name] = konkurencja_obj
        return selected_konkurencje

    def konkurencja_combobox_selected(self, index: int) -> None:
        konkurencja_obj = self.ui.comboBox_konkurencje.itemData(index)
        if konkurencja_obj:
            self._add_konkurencja_to_list_widget(konkurencja_obj)

    def new_konkurencja(self) -> None:
        from operator_ui_handler import KreatorKonkurencjiDialog

        self.kreator_dialog = KreatorKonkurencjiDialog()
        self.kreator_dialog.signals.konkurencja_created.connect(self.on_konkurencja_created)
        self.kreator_dialog.show_dialog()

    def on_konkurencja_created(self, konkurencja_obj) -> None:
        self._add_konkurencja_to_list_widget(konkurencja_obj)
        self.konkurencje[konkurencja_obj.name] = konkurencja_obj
        self._refresh_konkurencje_combobox()

    def accepted(self) -> None:
        selected_nazwa = self.ui.lineEdit_nazwa_zawodow.text()
        selected_datetime = self.ui.dateTimeEdit_data_zawodow.dateTime().toString(
            Globals.TIMESTAMP_FORMAT_QT
        )
        selected_konkurencje = self._get_selected_konkurencje()

        validator = NewZawodyDataValidation(selected_nazwa, selected_datetime, selected_konkurencje)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(self.ui, "Błąd", message)
            return

        zawody_obj = zawody_data_manager.insert_zawody(
            selected_nazwa, selected_datetime, selected_konkurencje
        )
        self.zawody_created.emit(zawody_obj)
        self.ui.close()


