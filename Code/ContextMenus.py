"""Context menu handlers dla list w UI (lista zawodów, lista konkurencji)."""

from Globals import Globals
Globals.setMainDirectory()

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt, Signal, QObject

from DataManager import zawody_data_manager


class Lista_zawodow_context_menu(QObject):
    """Obsługuje menu kontekstowe dla listy zawodów.

    Emituje `zawody_selected` z obiektem `Zawody` po otwarciu.
    """

    zawody_selected = Signal(object)

    def __init__(self, UI):
        super().__init__()
        self.UI = UI
        self.UI.listWidget_lista_zawodow.setContextMenuPolicy(Qt.CustomContextMenu)
        self.UI.listWidget_lista_zawodow.customContextMenuRequested.connect(self.show_context_menu)
        self.UI.listWidget_lista_zawodow.itemDoubleClicked.connect(self.on_item_double_clicked)

    def on_item_double_clicked(self, item):
        """Otwiera zawody po dwukrotnym kliknięciu pozycji."""
        self.open_zawody(item.data(Qt.UserRole))

    def show_context_menu(self, position):
        """Wyświetla menu kontekstowe przy prawym kliknięciu."""
        selected_item = self.UI.listWidget_lista_zawodow.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        otworz_action = menu.addAction("Otwórz Zawody")
        action = menu.exec(self.UI.listWidget_lista_zawodow.mapToGlobal(position))
        if action == otworz_action:
            self.open_zawody(selected_item.data(Qt.UserRole))

    def open_zawody(self, zawody_id):
        """Pobiera obiekt zawodów z DB i emituje sygnał `zawody_selected`."""
        zawody_obj = zawody_data_manager.get_zawody_by_id(zawody_id)
        if zawody_obj:
            self.zawody_selected.emit(zawody_obj)


class Konkurencje_list_context_menu(QObject):
    """Prototyp menu kontekstowego dla listy konkurencji (można rozwinąć)."""

    konkurencja_selected = Signal(object)

    def __init__(self, UI):
        super().__init__()
        self.UI = UI
        # Ustawienie polityki menu kontekstowego
        self.UI.konkurencje_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.UI.konkurencje_list.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Wyświetla proste menu z opcją usuwania (implementacja usuwania zależy od logiki aplikacji)."""
        selected_item = self.UI.konkurencje_list.itemAt(position)
        if not selected_item:
            return
        menu = QMenu()
        usun_action = menu.addAction("Usuń")
        action = menu.exec(self.UI.konkurencje_list.mapToGlobal(position))
        if action == usun_action:
            # TODO: usuń konkurencję z listy / DB
            pass

    def usun_konkurencje(self, konkurencja_id):
        """Usuwa konkurencję — implementacja zależy od UI i logiki aplikacji."""
        pass
