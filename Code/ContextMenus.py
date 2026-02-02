from Globals import Globals
Globals.setMainDirectory()
from PySide6.QtWidgets import QMenu
from PySide6.QtCore import Qt, Signal, QObject
from DataManager import zawody_data_manager


class lista_zawodow_context_menu(QObject):
    zawody_selected = Signal(object)  # Sygnał przekazujący obiekt zawodów
    
    def __init__(self, UI):
        super().__init__()
        self.UI = UI
        self.UI.listWidget_lista_zawodow.setContextMenuPolicy(Qt.CustomContextMenu)
        self.UI.listWidget_lista_zawodow.customContextMenuRequested.connect(self.show_context_menu)
        # Podłącz podwójne kliknięcie
        self.UI.listWidget_lista_zawodow.itemDoubleClicked.connect(self.on_item_double_clicked)
    
    def on_item_double_clicked(self, item):
        zawody_id = item.data(Qt.UserRole)
        self.open_zawody(zawody_id)
    
    def show_context_menu(self, position):
        selected_item = self.UI.listWidget_lista_zawodow.itemAt(position)
        if not selected_item:
            return
            
        menu = QMenu()
        otworz_action = menu.addAction("Otwórz Zawody")
        action = menu.exec(self.UI.listWidget_lista_zawodow.mapToGlobal(position))
        
        if action == otworz_action:
            zawody_id = selected_item.data(Qt.UserRole)
            self.open_zawody(zawody_id)
    
    def open_zawody(self, zawody_id):
        # Pobierz zawody z bazy danych
        zawody_obj = zawody_data_manager.get_zawody_by_id(zawody_id)
        if zawody_obj:
            self.zawody_selected.emit(zawody_obj)

