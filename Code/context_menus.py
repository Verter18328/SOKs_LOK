"""Menu kontekstowe dla list w UI (lista zawodów, lista konkurencji).

Każda klasa menu emituje sygnał z wybranym obiektem po interakcji użytkownika.
Obsługiwane interakcje: prawy klik (menu kontekstowe) i podwójne kliknięcie.
"""

from globals import Globals
Globals.set_main_directory()

from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt, Signal, QObject

from data_manager import zawody_data_manager


class ListaZawodowContextMenu(QObject):
    """Obsługuje menu kontekstowe dla listy zawodów.

    Emituje `zawody_selected` z obiektem `Zawody` po otwarciu.
    Obsługuje zarówno prawy klik (menu kontekstowe) jak i podwójne kliknięcie.
    """

    zawody_selected = Signal(object)

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
        action = menu.exec(self.ui.listWidget_lista_zawodow.mapToGlobal(position))
        if action == otworz_action:
            self.open_zawody(selected_item.data(Qt.UserRole))

    def open_zawody(self, zawody_id: int) -> None:
        """Pobiera obiekt zawodów z DB i emituje sygnał `zawody_selected`."""
        zawody_obj = zawody_data_manager.get_zawody_by_id(zawody_id)
        if zawody_obj:
            self.zawody_selected.emit(zawody_obj)


class KonkurencjeListContextMenu(QObject):
    """Menu kontekstowe dla listy konkurencji w dialogu tworzenia zawodów.

    Emituje `konkurencja_selected` z obiektem `Konkurencja`.
    """

    konkurencja_selected = Signal(object)

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
            # TODO: usuń konkurencję z listy / DB
            pass

    def usun_konkurencje(self, konkurencja_id: int) -> None:
        """Usuwa konkurencję — implementacja zależy od UI i logiki aplikacji."""
        pass
