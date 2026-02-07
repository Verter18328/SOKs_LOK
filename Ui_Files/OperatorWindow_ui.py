# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'OperatorWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QLabel, QLineEdit,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QStatusBar, QTabWidget, QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(967, 773)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.actionNowe_zawody = QAction(MainWindow)
        self.actionNowe_zawody.setObjectName(u"actionNowe_zawody")
        self.actionNowe_zawody.setMenuRole(QAction.NoRole)
        self.actionOtworz_zawody = QAction(MainWindow)
        self.actionOtworz_zawody.setObjectName(u"actionOtworz_zawody")
        self.actionOtworz_zawody.setMenuRole(QAction.NoRole)
        self.actionLista_zawodnikow = QAction(MainWindow)
        self.actionLista_zawodnikow.setObjectName(u"actionLista_zawodnikow")
        self.actionLista_zawodnikow.setMenuRole(QAction.NoRole)
        self.actionRozpocznij_wyswietlanie = QAction(MainWindow)
        self.actionRozpocznij_wyswietlanie.setObjectName(u"actionRozpocznij_wyswietlanie")
        self.actionRozpocznij_wyswietlanie.setMenuRole(QAction.NoRole)
        self.actionZakoncz_wyswietlanie = QAction(MainWindow)
        self.actionZakoncz_wyswietlanie.setObjectName(u"actionZakoncz_wyswietlanie")
        self.actionZakoncz_wyswietlanie.setMenuRole(QAction.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy)
        self.pageTitle = QWidget()
        self.pageTitle.setObjectName(u"pageTitle")
        self.gridLayout_4 = QGridLayout(self.pageTitle)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label = QLabel(self.pageTitle)
        self.label.setObjectName(u"label")
        self.label.setPixmap(QPixmap(u":/images/logo.jpeg"))
        self.label.setScaledContents(True)

        self.gridLayout_4.addWidget(self.label, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.pageTitle)
        self.pageZawodnicy = QWidget()
        self.pageZawodnicy.setObjectName(u"pageZawodnicy")
        self.gridLayout_2 = QGridLayout(self.pageZawodnicy)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.lineEditWyszukiwanie_zawodnikow = QLineEdit(self.pageZawodnicy)
        self.lineEditWyszukiwanie_zawodnikow.setObjectName(u"lineEditWyszukiwanie_zawodnikow")
        self.lineEditWyszukiwanie_zawodnikow.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.lineEditWyszukiwanie_zawodnikow, 1, 0, 1, 1)

        self.label_2 = QLabel(self.pageZawodnicy)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.listaZawodnikow = QListWidget(self.pageZawodnicy)
        self.listaZawodnikow.setObjectName(u"listaZawodnikow")

        self.gridLayout_2.addWidget(self.listaZawodnikow, 2, 0, 1, 1)

        self.stackedWidget.addWidget(self.pageZawodnicy)
        self.pageZawody_managment = QWidget()
        self.pageZawody_managment.setObjectName(u"pageZawody_managment")
        self.gridLayout_3 = QGridLayout(self.pageZawody_managment)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.button_dodaj_wynik = QPushButton(self.pageZawody_managment)
        self.button_dodaj_wynik.setObjectName(u"button_dodaj_wynik")

        self.gridLayout_3.addWidget(self.button_dodaj_wynik, 2, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 2, 0, 1, 1)

        self.tabWidget_zawody = QTabWidget(self.pageZawody_managment)
        self.tabWidget_zawody.setObjectName(u"tabWidget_zawody")
        sizePolicy.setHeightForWidth(self.tabWidget_zawody.sizePolicy().hasHeightForWidth())
        self.tabWidget_zawody.setSizePolicy(sizePolicy)

        self.gridLayout_3.addWidget(self.tabWidget_zawody, 1, 0, 1, 2)

        self.label_zawody_nazwa = QLabel(self.pageZawody_managment)
        self.label_zawody_nazwa.setObjectName(u"label_zawody_nazwa")

        self.gridLayout_3.addWidget(self.label_zawody_nazwa, 0, 0, 1, 2)

        self.stackedWidget.addWidget(self.pageZawody_managment)
        self.pageLista_zawodow = QWidget()
        self.pageLista_zawodow.setObjectName(u"pageLista_zawodow")
        self.gridLayout_5 = QGridLayout(self.pageLista_zawodow)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_3 = QLabel(self.pageLista_zawodow)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_5.addWidget(self.label_3, 0, 0, 1, 1)

        self.listWidget_lista_zawodow = QListWidget(self.pageLista_zawodow)
        self.listWidget_lista_zawodow.setObjectName(u"listWidget_lista_zawodow")

        self.gridLayout_5.addWidget(self.listWidget_lista_zawodow, 1, 0, 1, 1)

        self.stackedWidget.addWidget(self.pageLista_zawodow)

        self.gridLayout.addWidget(self.stackedWidget, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 967, 22))
        self.menuBar.setNativeMenuBar(True)
        self.menuBagno = QMenu(self.menuBar)
        self.menuBagno.setObjectName(u"menuBagno")
        self.menuZawodnicy = QMenu(self.menuBar)
        self.menuZawodnicy.setObjectName(u"menuZawodnicy")
        self.menuWy_wietlanie = QMenu(self.menuBar)
        self.menuWy_wietlanie.setObjectName(u"menuWy_wietlanie")
        self.menuWy_wietlanie.setSeparatorsCollapsible(False)
        MainWindow.setMenuBar(self.menuBar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.menuBar.addAction(self.menuWy_wietlanie.menuAction())
        self.menuBar.addAction(self.menuBagno.menuAction())
        self.menuBar.addAction(self.menuZawodnicy.menuAction())
        self.menuBagno.addSeparator()
        self.menuBagno.addAction(self.actionNowe_zawody)
        self.menuBagno.addSeparator()
        self.menuBagno.addAction(self.actionOtworz_zawody)
        self.menuBagno.addSeparator()
        self.menuZawodnicy.addSeparator()
        self.menuZawodnicy.addAction(self.actionLista_zawodnikow)
        self.menuZawodnicy.addSeparator()
        self.menuWy_wietlanie.addSeparator()
        self.menuWy_wietlanie.addAction(self.actionRozpocznij_wyswietlanie)
        self.menuWy_wietlanie.addSeparator()
        self.menuWy_wietlanie.addAction(self.actionZakoncz_wyswietlanie)
        self.menuWy_wietlanie.addSeparator()

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)
        self.tabWidget_zawody.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionNowe_zawody.setText(QCoreApplication.translate("MainWindow", u"Nowe Zawody", None))
#if QT_CONFIG(tooltip)
        self.actionNowe_zawody.setToolTip(QCoreApplication.translate("MainWindow", u"Nowe Zawody", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionNowe_zawody.setStatusTip(QCoreApplication.translate("MainWindow", u"Tworzy nowe zawody", None))
#endif // QT_CONFIG(statustip)
        self.actionOtworz_zawody.setText(QCoreApplication.translate("MainWindow", u"Otw\u00f3rz Zawody", None))
#if QT_CONFIG(tooltip)
        self.actionOtworz_zawody.setToolTip(QCoreApplication.translate("MainWindow", u"Otw\u00f3rz Zawody", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionOtworz_zawody.setStatusTip(QCoreApplication.translate("MainWindow", u"Otwiera zapisane zawody", None))
#endif // QT_CONFIG(statustip)
        self.actionLista_zawodnikow.setText(QCoreApplication.translate("MainWindow", u"Lista Zawodnik\u00f3w", None))
#if QT_CONFIG(tooltip)
        self.actionLista_zawodnikow.setToolTip(QCoreApplication.translate("MainWindow", u"Lista Zawodnik\u00f3w", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionLista_zawodnikow.setStatusTip(QCoreApplication.translate("MainWindow", u"Przechodzi do panelu z list\u0105 wszystkich zawodnik\u00f3w", None))
#endif // QT_CONFIG(statustip)
        self.actionRozpocznij_wyswietlanie.setText(QCoreApplication.translate("MainWindow", u"Rozpocznij Wy\u015bwietlanie", None))
#if QT_CONFIG(tooltip)
        self.actionRozpocznij_wyswietlanie.setToolTip(QCoreApplication.translate("MainWindow", u"Rozpocznij Wy\u015bwietlanie", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionRozpocznij_wyswietlanie.setStatusTip(QCoreApplication.translate("MainWindow", u"Rozpoczyna wy\u015bwietlanie na urz\u0105dzeniu zewn\u0119trznym", None))
#endif // QT_CONFIG(statustip)
        self.actionZakoncz_wyswietlanie.setText(QCoreApplication.translate("MainWindow", u"Zako\u0144cz Wy\u015bwietlanie", None))
#if QT_CONFIG(tooltip)
        self.actionZakoncz_wyswietlanie.setToolTip(QCoreApplication.translate("MainWindow", u"Zako\u0144cz Wy\u015bwietlanie", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionZakoncz_wyswietlanie.setStatusTip(QCoreApplication.translate("MainWindow", u"Przestaje wy\u015bwietla\u0107 na urz\u0105dzeniu zewn\u0119trznym", None))
#endif // QT_CONFIG(statustip)
        self.label.setText("")
        self.lineEditWyszukiwanie_zawodnikow.setText("")
        self.lineEditWyszukiwanie_zawodnikow.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Szukaj", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\">Zarz\u0105dzanie zawodnikami</span></p></body></html>", None))
        self.button_dodaj_wynik.setText(QCoreApplication.translate("MainWindow", u"Dodaj Wynik", None))
        self.label_zawody_nazwa.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\">Nazwa zawod\u00f3w</span></p></body></html>", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:700;\">Lista Zawod\u00f3w</span></p></body></html>", None))
        self.menuBagno.setTitle(QCoreApplication.translate("MainWindow", u"Zawody", None))
        self.menuZawodnicy.setTitle(QCoreApplication.translate("MainWindow", u"Zawodnicy", None))
        self.menuWy_wietlanie.setTitle(QCoreApplication.translate("MainWindow", u"Wy\u015bwietlanie", None))
    # retranslateUi

