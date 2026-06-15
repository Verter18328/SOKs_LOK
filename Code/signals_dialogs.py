"""Obsługa sygnałów dla dialogów (rejestracja serii, kreator konkurencji, nowe zawody)."""

from globals import Globals

Globals.set_main_directory()

from PySide6.QtCore import QObject, Qt, QStringListModel, QTimer, Signal
from PySide6.QtWidgets import QCompleter, QListWidgetItem, QMessageBox

from data_manager import (
    konkurencja_data_manager,
    seria_data_manager,
    wynik_data_manager,
    zawody_data_manager,
    zawodnik_data_manager,
    Zawody,
    Konkurencja,
    Seria,
)
from data_validation import NewKonkurencjaDataValidation, NewZawodyDataValidation, ZarejestrujSerieDataValidation


class SignalsEdytujZawodnikaDialog(QObject):
    """Obsługa sygnałów w dialogu edycji zawodnika."""

    zawodnik_updated = Signal()

    def __init__(self, ui, parent_window=None, zawodnik_id: int = None) -> None:
        super().__init__()
        self.ui = ui
        self.parent_window = parent_window
        self.zawodnik_id = zawodnik_id
        self.connect_signals()
        self.fill_zawodnik_data()
    def connect_signals(self) -> None:
        """Podłącza akceptację/anulowanie dialogu."""
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.ui.reject)
    
    def fill_zawodnik_data(self) -> None:
        """Wypełnia dane zawodnika w polach dialogu."""
        zawodnik = zawodnik_data_manager.get_zawodnik_by_id(self.zawodnik_id)
        if not zawodnik:
            return
        self.ui.imie_lineEdit.setText(zawodnik.imie)
        self.ui.nazwisko_lineEdit.setText(zawodnik.nazwisko)
    def accept(self) -> None:
        """Waliduje dane, aktualizuje zawodnika w bazie i zamyka dialog."""
        imie = self.ui.imie_lineEdit.text()
        nazwisko = self.ui.nazwisko_lineEdit.text()
        validator = ZarejestrujSerieDataValidation(imie, nazwisko)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(self.ui, "Błąd", message)
            return
        updated = zawodnik_data_manager.update_zawodnik(self.zawodnik_id, imie, nazwisko)
        if not updated:
            QMessageBox.warning(self.ui, "Błąd", "Błąd podczas aktualizacji zawodnika")
            return
        self.zawodnik_updated.emit()
        self.ui.close()
class SignalsZarejestrujSerieDialog(QObject):
    """Obsługa sygnałów w dialogu zarejestrowania serii."""

    def __init__(self, ui, zawody: Zawody | None = None, parent_window=None) -> None:
        """Inicjalizuje dialog: numer serii, lista konkurencji zawodów, completery zawodników."""
        super().__init__()
        self.ui = ui
        self.zawody = zawody
        self.parent_window = parent_window
        self.last_seria_number = seria_data_manager.get_last_seria_number_for_zawody(self.zawody.id)
        self.seria_number = self.last_seria_number + 1
        self.ui.seria_label.setText(f"Seria {self.seria_number}")
        self.konkurencje = self.zawody.konkurencje
        self.ui.konkurencja_comboBox.clear()
        self.ui.konkurencja_comboBox.setPlaceholderText("Wybierz konkurencję")
        self.ui.konkurencja_comboBox.setCurrentIndex(-1)
        for konkurencja in self.konkurencje.values():
            self.ui.konkurencja_comboBox.addItem(konkurencja.label(), userData=konkurencja)
        self.connect_signals()

    def connect_signals(self) -> None:
        """Podłącza akceptację/anulowanie dialogu i completery pól zawodnika."""
        self.ui.buttonBox.accepted.connect(self.accepted)
        self.ui.buttonBox.rejected.connect(self.ui.close)
        self._setup_zawodnik_completers()

    def accepted(self) -> None:
        """Waliduje dane, tworzy lub odnajduje zawodnika i zapisuje serię w bazie."""
        imie = self.ui.imie_lineEdit.text()
        nazwisko = self.ui.nazwisko_lineEdit.text()
        konkurencja_selected = self.ui.konkurencja_comboBox.currentData()
        if not konkurencja_selected:
            QMessageBox.warning(self.ui, "Błąd", "Wybierz konkurencję")
            return
        validator = ZarejestrujSerieDataValidation(imie, nazwisko)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(self.ui, "Błąd", message)
            return
        zawodnik = zawodnik_data_manager.get_zawodnik_by_id(
            zawodnik_data_manager.get_id_from_imie_nazwisko(validator.imie, validator.nazwisko)
        )
        if not zawodnik:
            zawodnik = zawodnik_data_manager.insert_zawodnik(validator.imie, validator.nazwisko)
            if not zawodnik:
                QMessageBox.warning(self.ui, "Błąd", "Błąd podczas zapisu zawodnika")
                return
        seria = Seria(number=self.seria_number, zawodnik=zawodnik, zawody=self.zawody, konkurencja=konkurencja_selected)
        seria = seria_data_manager.insert_seria(seria.number, zawodnik, self.zawody, konkurencja_selected)
        if not seria:
            QMessageBox.warning(self.ui, "Błąd", "Błąd podczas zapisu serii")
            return
        self.ui.close()

    def _setup_zawodnik_completers(self) -> None:
        """Podpowiedzi imię/nazwisko — wspólny model, osobny QCompleter na pole (Qt: jeden completer = jeden widget).

        Po wyborze z popupu wypełniane są pola imię i nazwisko; opóźnienie 0 ms — po domyślnym wstawieniu tekstu przez Qt.
        """
        zawodnicy = zawodnik_data_manager.get_zawodnicy()
        if not zawodnicy:
            return
        zawodnicy = sorted(zawodnicy, key=lambda z: (z.nazwisko.lower(), z.imie.lower()))
        self._zawodnicy_completer_rows = zawodnicy
        model = QStringListModel([z.label() for z in zawodnicy], self.ui)
        for line_edit in (self.ui.imie_lineEdit, self.ui.nazwisko_lineEdit):
            completer = QCompleter(model, self.ui)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            line_edit.setCompleter(completer)
            completer.activated[str].connect(self._on_zawodnik_completer_activated)

    def _on_zawodnik_completer_activated(self, completion: str) -> None:
        """Po wyborze zawodnika z podpowiedzi wypełnia imię i nazwisko."""
        def apply_choice() -> None:
            for z in self._zawodnicy_completer_rows:
                if z.label() == completion:
                    self.ui.imie_lineEdit.setText(z.imie)
                    self.ui.nazwisko_lineEdit.setText(z.nazwisko)
                    return

        QTimer.singleShot(0, apply_choice)


class SignalsEdytujSerieDialog(QObject):
    """Obsługa sygnałów w dialogu edycji serii.

    Wzorowane na ``SignalsZarejestrujSerieDialog``, ale zamiast tworzyć nową serię
    aktualizuje istniejącą (zawodnik + konkurencja + numer). Zmiana konkurencji
    jest blokowana, gdy seria ma już wpisane wyniki.
    """

    seria_updated = Signal()

    def __init__(self, ui, seria: Seria, parent_window=None) -> None:
        """Inicjalizuje dialog edycji serii: prefilluje pola i przygotowuje completery."""
        super().__init__()
        self.ui = ui
        self.seria = seria
        self.zawody = seria.zawody
        self.parent_window = parent_window

        self.ui.seria_spinBox.setValue(seria.number)
        self.ui.imie_lineEdit.setText(seria.zawodnik.imie)
        self.ui.nazwisko_lineEdit.setText(seria.zawodnik.nazwisko)

        self.konkurencje = self.zawody.konkurencje
        self.ui.konkurencja_comboBox.clear()
        current_index = -1
        for idx, konkurencja in enumerate(self.konkurencje.values()):
            self.ui.konkurencja_comboBox.addItem(konkurencja.label(), userData=konkurencja)
            if konkurencja.id == seria.konkurencja.id:
                current_index = idx
        self.ui.konkurencja_comboBox.setCurrentIndex(current_index)

        if wynik_data_manager.does_wynik_exist_for_seria_id(seria.id):
            self.ui.konkurencja_comboBox.setEnabled(False)
            self.ui.konkurencja_comboBox.setToolTip(
                "Nie można zmienić konkurencji — seria ma wpisane wyniki."
            )

        self.connect_signals()

    def connect_signals(self) -> None:
        """Podłącza akceptację/anulowanie dialogu i completery pól zawodnika."""
        self.ui.buttonBox.accepted.connect(self.accepted)
        self.ui.buttonBox.rejected.connect(self.ui.close)
        self._setup_zawodnik_completers()

    def accepted(self) -> None:
        """Waliduje dane, aktualizuje serię i emituje sygnał ``seria_updated``."""
        imie = self.ui.imie_lineEdit.text()
        nazwisko = self.ui.nazwisko_lineEdit.text()
        new_number = self.ui.seria_spinBox.value()
        konkurencja_selected = self.ui.konkurencja_comboBox.currentData()
        if not konkurencja_selected:
            QMessageBox.warning(self.ui, "Błąd", "Wybierz konkurencję")
            return
        validator = ZarejestrujSerieDataValidation(imie, nazwisko)
        is_valid, message = validator.is_valid_result
        if not is_valid:
            QMessageBox.warning(self.ui, "Błąd", message)
            return
        if new_number != self.seria.number and seria_data_manager.does_seria_number_exist_for_zawody(
            new_number, self.zawody.id
        ):
            QMessageBox.warning(
                self.ui, "Błąd", f"Numer serii {new_number} już istnieje w tych zawodach."
            )
            return
        zawodnik = zawodnik_data_manager.get_zawodnik_by_id(
            zawodnik_data_manager.get_id_from_imie_nazwisko(validator.imie, validator.nazwisko)
        )
        if not zawodnik:
            zawodnik = zawodnik_data_manager.insert_zawodnik(validator.imie, validator.nazwisko)
            if not zawodnik:
                QMessageBox.warning(self.ui, "Błąd", "Błąd podczas zapisu zawodnika")
                return
        if not seria_data_manager.update_seria(
            self.seria.id, new_number, zawodnik, konkurencja_selected
        ):
            QMessageBox.warning(self.ui, "Błąd", "Błąd podczas aktualizacji serii")
            return
        self.seria_updated.emit()
        self.ui.close()

    def _setup_zawodnik_completers(self) -> None:
        """Podpowiedzi imię/nazwisko — wspólny model, osobny QCompleter na pole."""
        zawodnicy = zawodnik_data_manager.get_zawodnicy()
        if not zawodnicy:
            return
        zawodnicy = sorted(zawodnicy, key=lambda z: (z.nazwisko.lower(), z.imie.lower()))
        self._zawodnicy_completer_rows = zawodnicy
        model = QStringListModel([z.label() for z in zawodnicy], self.ui)
        for line_edit in (self.ui.imie_lineEdit, self.ui.nazwisko_lineEdit):
            completer = QCompleter(model, self.ui)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            line_edit.setCompleter(completer)
            completer.activated[str].connect(self._on_zawodnik_completer_activated)

    def _on_zawodnik_completer_activated(self, completion: str) -> None:
        """Po wyborze zawodnika z podpowiedzi wypełnia imię i nazwisko."""
        def apply_choice() -> None:
            for z in self._zawodnicy_completer_rows:
                if z.label() == completion:
                    self.ui.imie_lineEdit.setText(z.imie)
                    self.ui.nazwisko_lineEdit.setText(z.nazwisko)
                    return

        QTimer.singleShot(0, apply_choice)


class SignalsKreatorKonkurencjiDialog(QObject):
    """Obsługa sygnałów w dialogu tworzenia konkurencji."""

    konkurencja_created = Signal(object)

    def __init__(self, ui, parent_window=None) -> None:
        """Inicjalizuje dialog kreatora konkurencji."""
        super().__init__()
        self.ui = ui
        self.parent_window = parent_window
        self.connect_signals()

    def connect_signals(self) -> None:
        """Podłącza akceptację i anulowanie dialogu."""
        self.ui.buttonBox.accepted.connect(self.accepted)
        self.ui.buttonBox.rejected.connect(self.ui.close)

    def accepted(self) -> None:
        """Waliduje dane i zapisuje nową konkurencję; emituje sygnał ``konkurencja_created``."""
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
        """Inicjalizuje dialog tworzenia zawodów z listą konkurencji i menu kontekstowym."""
        super().__init__()
        self.ui = ui
        self.parent_window = parent_window
        self.konkurencje: dict = {}
        from context_menus import KonkurencjeListContextMenu
        self.konkurencje_list_context_menu = KonkurencjeListContextMenu(self.ui)
        self.connect_signals()
        self.get_konkurencje()

    def connect_signals(self) -> None:
        """Podłącza przyciski dodawania konkurencji, combobox i akceptację formularza."""
        self.ui.button_dodaj_konkurencje.clicked.connect(self.new_konkurencja)
        self.ui.buttonBox_zawody.accepted.connect(self.accepted)
        self.ui.buttonBox_zawody.rejected.connect(self.ui.close)
        self.ui.comboBox_konkurencje.activated.connect(self.konkurencja_combobox_selected)

    def get_konkurencje(self) -> None:
        """Pobiera konkurencje z bazy i odświeża combobox."""
        konkurencje = konkurencja_data_manager.get_all_konkurencje()
        if not konkurencje:
            return
        self.konkurencje = {k.name: k for k in konkurencje.values()}
        self._refresh_konkurencje_combobox()
    
    def _refresh_konkurencje_combobox(self) -> None:
        """Odświeża listę konkurencji w comboboxie (np. po dodaniu nowej)."""
        self.ui.comboBox_konkurencje.clear()
        self.ui.comboBox_konkurencje.setPlaceholderText("Wybierz konkurencję")
        self.ui.comboBox_konkurencje.setCurrentIndex(-1)
        for konkurencja in self.konkurencje.values():
            self.ui.comboBox_konkurencje.addItem(konkurencja.label(), userData=konkurencja)

    def _add_konkurencja_to_list_widget(self, konkurencja_obj) -> None:
        """Dodaje konkurencję do listy wybranych w formularzu zawodów."""
        item = QListWidgetItem(konkurencja_obj.label())
        item.setData(Qt.UserRole, konkurencja_obj)
        self.ui.konkurencje_list.addItem(item)

    def _get_selected_konkurencje(self) -> dict:
        """Zwraca słownik konkurencji wybranych na liście (klucz: nazwa)."""
        selected_konkurencje = {}
        for row in range(self.ui.konkurencje_list.count()):
            konkurencja_obj = self.ui.konkurencje_list.item(row).data(Qt.UserRole)
            if konkurencja_obj:
                selected_konkurencje[konkurencja_obj.name] = konkurencja_obj
        return selected_konkurencje

    def konkurencja_combobox_selected(self, index: int) -> None:
        """Po wyborze konkurencji z comboboxa dodaje ją do listy wybranych."""
        konkurencja_obj = self.ui.comboBox_konkurencje.itemData(index)
        if konkurencja_obj:
            self._add_konkurencja_to_list_widget(konkurencja_obj)

    def new_konkurencja(self) -> None:
        """Otwiera dialog kreatora nowej konkurencji."""
        from operator_ui_handler import KreatorKonkurencjiDialog

        self.kreator_dialog = KreatorKonkurencjiDialog()
        self.kreator_dialog.signals.konkurencja_created.connect(self.on_konkurencja_created)
        self.kreator_dialog.show_dialog()

    def on_konkurencja_created(self, konkurencja_obj) -> None:
        """Po utworzeniu konkurencji — dodaje ją do listy i odświeża combobox."""
        self._add_konkurencja_to_list_widget(konkurencja_obj)
        self.konkurencje[konkurencja_obj.name] = konkurencja_obj
        self._refresh_konkurencje_combobox()

    def accepted(self) -> None:
        """Waliduje dane zawodów, zapisuje je w bazie i emituje sygnał ``zawody_created``."""
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


