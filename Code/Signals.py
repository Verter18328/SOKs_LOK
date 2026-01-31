from Globals import Globals
Globals.setMainDirectory()
from PySide6.QtGui import QShortcut
from PySide6.QtGui import QKeySequence
from DataManager import data_manager

class Signals:
    def __init__(self, UI):
        self.UI = UI
        self.connect_signals()
    def connect_signals(self):
        self.UI.actionZarzadzanie_zawodnikami.triggered.connect(self.actionZarzadzanie_zawodnikami_triggered)
        self.UI.exit_To_title_shortcut = QShortcut(QKeySequence("Esc"), self.UI)
        self.UI.exit_To_title_shortcut.activated.connect(self.exit_to_title_triggered)
    def actionZarzadzanie_zawodnikami_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageZawodnicy)
        klienci = data_manager.getClients()
        if klienci is not None:
            for klient in klienci:
                imie_nazwisko = f"{klient['imie']} {klient['nazwisko']}"
                self.UI.listaZawodnikow.addItem(imie_nazwisko)
    def exit_to_title_triggered(self):
        self.UI.stackedWidget.setCurrentWidget(self.UI.pageTitle)