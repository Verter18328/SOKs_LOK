"""Menu kontekstowe dla list w UI (lista zawodów, lista konkurencji).

Każda klasa menu emituje sygnał z wybranym obiektem po interakcji użytkownika.
Obsługiwane interakcje: prawy klik (menu kontekstowe) i podwójne kliknięcie.
"""

from globals import Globals
Globals.set_main_directory()

from PySide6.QtWidgets import QMenu, QListWidgetItem, QMessageBox
from PySide6.QtCore import Qt, Signal, QObject

from data_manager import seria_data_manager, zawody_data_manager, zawodnik_data_manager

class ListaZawodowContextMenu(QObject):
    """Obsługuje menu kontekstowe dla listy zawodów.

    Emituje `zawody_selected` z obiektem `Zawody` po otwarciu.
    Obsługuje zarówno prawy klik (menu kontekstowe) jak i podwójne kliknięcie.
    """

    zawody_selected = Signal(object)
    zawody_list_changed = Signal()

    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.ui.listWidget_lista_zawodow.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listWidget_lista_zawodow.customContextMenuRequested.connect(self.show_context_menu)
        self.ui.listWidget_lista_zawodow.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item) -> None:
        """Otwiera zawody po dwukrotnym kliknięciu pozycji."""
        self.open_zawody(item.data(Qt.UserRole))

    def show_context_menu(self, position) -> None:
        """Wyświetla menu kontekstowe przy prawym kliknięciu."""
        selected_item = self.ui.listWidget_lista_zawodow.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        otworz_action = menu.addAction("Otwórz Zawody")
        edytuj_action = menu.addAction("Edytuj")
        usun_action = menu.addAction("Usuń")
        action = menu.exec(self.ui.listWidget_lista_zawodow.mapToGlobal(position))
        if action == otworz_action:
            self.open_zawody(selected_item.data(Qt.UserRole))
        elif action == edytuj_action:
            self.edytuj_zawody(selected_item)
        elif action == usun_action:
            self.usun_zawody(selected_item)

    def open_zawody(self, zawody_id: int) -> None:
        """Pobiera obiekt zawodów z DB i emituje sygnał `zawody_selected`."""
        zawody_obj = zawody_data_manager.get_zawody_by_id(zawody_id)
        if zawody_obj:
            self.zawody_selected.emit(zawody_obj)

    def edytuj_zawody(self, selected_item: QListWidgetItem) -> None:
        """Otwiera dialog edycji zawodów dla wybranej pozycji listy."""
        zawody_id = selected_item.data(Qt.UserRole)
        if not zawody_id:
            return
        from operator_ui_handler import EdytujZawodyDialog

        dialog = EdytujZawodyDialog(parent=self.ui, zawody_id=zawody_id)
        dialog.signals.zawody_updated.connect(self.zawody_list_changed.emit)
        dialog.show_dialog()

    def usun_zawody(self, selected_item: QListWidgetItem) -> None:
        """Usuwa zawody z bazy (wraz z seriami i wynikami) i z listy w UI."""
        zawody_id = selected_item.data(Qt.UserRole)
        if not zawody_id:
            return
        answer = QMessageBox.question(
            self.ui,
            "Usuń zawody",
            f"Czy na pewno usunąć „{selected_item.text()}”?\n"
            "Zostaną też usunięte wszystkie serie i wyniki tych zawodów.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if not zawody_data_manager.delete_zawody(zawody_id):
            QMessageBox.warning(self.ui, "Błąd", "Nie udało się usunąć zawodów.")
            return
        self.ui.listWidget_lista_zawodow.takeItem(self.ui.listWidget_lista_zawodow.row(selected_item))
        self.zawody_list_changed.emit()


class KonkurencjeListContextMenu(QObject):
    """Menu kontekstowe dla listy konkurencji w dialogu tworzenia zawodów.

    """


    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.ui.konkurencje_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.konkurencje_list.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position) -> None:
        """Wyświetla menu z opcją usuwania konkurencji."""
        selected_item = self.ui.konkurencje_list.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        usun_action = menu.addAction("Usuń")
        action = menu.exec(self.ui.konkurencje_list.mapToGlobal(position))
        if action == usun_action:
            self.usun_konkurencje(selected_item)
            pass

    def usun_konkurencje(self, selected_item: QListWidgetItem) -> None:
        """Usuwa konkurencję — implementacja zależy od UI i logiki aplikacji."""
        self.ui.konkurencje_list.takeItem(self.ui.konkurencje_list.row(selected_item))


class ZawodnicyListContextMenu(QObject):
    """Menu kontekstowe dla listy zawodników w dialogu tworzenia zawodów."""

    zawodnik_updated = Signal()

    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.ui.listaZawodnikow.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.listaZawodnikow.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position) -> None:
        """Wyświetla menu kontekstowe przy prawym kliknięciu."""
        selected_item = self.ui.listaZawodnikow.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        usun_action = menu.addAction("Usuń")
        edytuj_action = menu.addAction("Edytuj")
        action = menu.exec(self.ui.listaZawodnikow.mapToGlobal(position))
        if action == usun_action:
            self.usun_zawodnika(selected_item)
        elif action == edytuj_action:
            self.edytuj_zawodnika(selected_item)

    def usun_zawodnika(self, selected_item: QListWidgetItem) -> None:
        """Usuwa zawodnika z bazy (wraz z seriami i wynikami) i z listy w UI."""
        zawodnik_id = selected_item.data(Qt.UserRole)
        if not zawodnik_id:
            return
        answer = QMessageBox.question(
            self.ui,
            "Usuń zawodnika",
            f"Czy na pewno usunąć „{selected_item.text()}”?\n"
            "Zostaną też usunięte wszystkie serie i wyniki tego zawodnika.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if not zawodnik_data_manager.delete_zawodnik(zawodnik_id):
            QMessageBox.warning(self.ui, "Błąd", "Nie udało się usunąć zawodnika.")
            return
        self.ui.listaZawodnikow.takeItem(self.ui.listaZawodnikow.row(selected_item))
            
    def edytuj_zawodnika(self, selected_item: QListWidgetItem) -> None:
        """Edytuje zawodnika — implementacja zależy od UI i logiki aplikacji."""
        from operator_ui_handler import EdytujZawodnikaDialog
        dialog = EdytujZawodnikaDialog(parent=self.ui, zawodnik_id=selected_item.data(Qt.UserRole))
        dialog.signals.zawodnik_updated.connect(self.zawodnik_updated.emit)
        dialog.show_dialog()


class StartyListContextMenu(QObject):
    """Menu kontekstowe dla listy startów/serii.

    Obsługuje usuwanie serii (z kaskadowym usunięciem strzałów po stronie DB)
    oraz edycję serii poprzez dialog ``EdytujSerieDialog``.
    """

    seria_changed = Signal()

    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.ui.starty_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.starty_list.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position) -> None:
        """Wyświetla menu kontekstowe przy prawym kliknięciu na pozycji listy."""
        selected_item = self.ui.starty_list.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        usun_action = menu.addAction("Usuń")
        edytuj_action = menu.addAction("Edytuj")
        action = menu.exec(self.ui.starty_list.mapToGlobal(position))
        if action == usun_action:
            self.usun_serie(selected_item)
        elif action == edytuj_action:
            self.edytuj_serie(selected_item)

    def usun_serie(self, selected_item: QListWidgetItem) -> None:
        """Usuwa serię z bazy (z kaskadowym usunięciem strzałów) i z listy w UI."""
        seria_id = selected_item.data(Qt.UserRole)
        if not seria_id:
            return
        answer = QMessageBox.question(
            self.ui,
            "Usuń serię",
            f"Czy na pewno usunąć „{selected_item.text()}”?\n"
            "Zostaną też usunięte wszystkie wpisane wyniki tej serii.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        if not seria_data_manager.delete_seria(seria_id):
            QMessageBox.warning(self.ui, "Błąd", "Nie udało się usunąć serii.")
            return
        self.ui.starty_list.takeItem(self.ui.starty_list.row(selected_item))
        self.seria_changed.emit()

    def edytuj_serie(self, selected_item: QListWidgetItem) -> None:
        """Otwiera dialog edycji serii dla wybranej pozycji listy."""
        seria_id = selected_item.data(Qt.UserRole)
        if not seria_id:
            return
        seria = seria_data_manager.get_seria_by_id(seria_id)
        if not seria:
            QMessageBox.warning(self.ui, "Błąd", "Nie udało się załadować serii.")
            return
        from operator_ui_handler import EdytujSerieDialog
        dialog = EdytujSerieDialog(parent=self.ui, seria=seria)
        dialog.signals.seria_updated.connect(self.seria_changed.emit)
        dialog.show_dialog()
