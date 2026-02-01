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
    QMenuBar, QSizePolicy, QStackedWidget, QStatusBar,
    QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(967, 773)
        self.actionNowe_zawody = QAction(MainWindow)
        self.actionNowe_zawody.setObjectName(u"actionNowe_zawody")
        self.actionNowe_zawody.setMenuRole(QAction.MenuRole.NoRole)
        self.actionOtworz_Zawody = QAction(MainWindow)
        self.actionOtworz_Zawody.setObjectName(u"actionOtworz_Zawody")
        self.actionOtworz_Zawody.setMenuRole(QAction.MenuRole.NoRole)
        self.actionLista_zawodnikow = QAction(MainWindow)
        self.actionLista_zawodnikow.setObjectName(u"actionLista_zawodnikow")
        self.actionLista_zawodnikow.setMenuRole(QAction.MenuRole.NoRole)
        self.actionRozpocznij_Wyswietlanie = QAction(MainWindow)
        self.actionRozpocznij_Wyswietlanie.setObjectName(u"actionRozpocznij_Wyswietlanie")
        self.actionRozpocznij_Wyswietlanie.setMenuRole(QAction.MenuRole.NoRole)
        self.actionZakoncz_Wyswietlanie = QAction(MainWindow)
        self.actionZakoncz_Wyswietlanie.setObjectName(u"actionZakoncz_Wyswietlanie")
        self.actionZakoncz_Wyswietlanie.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.pageTitle = QWidget()
        self.pageTitle.setObjectName(u"pageTitle")
        self.label = QLabel(self.pageTitle)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(290, 220, 321, 241))
        self.label.setPixmap(QPixmap(u":/images/logo.jpeg"))
        self.label.setScaledContents(True)
        self.stackedWidget.addWidget(self.pageTitle)
        self.pageZawodnicy = QWidget()
        self.pageZawodnicy.setObjectName(u"pageZawodnicy")
        self.gridLayout_2 = QGridLayout(self.pageZawodnicy)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_2 = QLabel(self.pageZawodnicy)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)

        self.lineEditWyszukiwanieZawodnikow = QLineEdit(self.pageZawodnicy)
        self.lineEditWyszukiwanieZawodnikow.setObjectName(u"lineEditWyszukiwanieZawodnikow")
        self.lineEditWyszukiwanieZawodnikow.setClearButtonEnabled(True)

        self.gridLayout_2.addWidget(self.lineEditWyszukiwanieZawodnikow, 1, 0, 1, 1)

        self.listaZawodnikow = QListWidget(self.pageZawodnicy)
        self.listaZawodnikow.setObjectName(u"listaZawodnikow")

        self.gridLayout_2.addWidget(self.listaZawodnikow, 2, 0, 1, 1)

        self.stackedWidget.addWidget(self.pageZawodnicy)

        self.gridLayout.addWidget(self.stackedWidget, 1, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QMenuBar(MainWindow)
        self.menuBar.setObjectName(u"menuBar")
        self.menuBar.setGeometry(QRect(0, 0, 967, 33))
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
        self.menuBagno.addAction(self.actionOtworz_Zawody)
        self.menuBagno.addSeparator()
        self.menuZawodnicy.addSeparator()
        self.menuZawodnicy.addAction(self.actionLista_zawodnikow)
        self.menuZawodnicy.addSeparator()
        self.menuWy_wietlanie.addSeparator()
        self.menuWy_wietlanie.addAction(self.actionRozpocznij_Wyswietlanie)
        self.menuWy_wietlanie.addSeparator()
        self.menuWy_wietlanie.addAction(self.actionZakoncz_Wyswietlanie)
        self.menuWy_wietlanie.addSeparator()

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(1)


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
        self.actionOtworz_Zawody.setText(QCoreApplication.translate("MainWindow", u"Otw\u00f3rz Zawody", None))
#if QT_CONFIG(tooltip)
        self.actionOtworz_Zawody.setToolTip(QCoreApplication.translate("MainWindow", u"Otw\u00f3rz Zawody", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionOtworz_Zawody.setStatusTip(QCoreApplication.translate("MainWindow", u"Otwiera zapisane zawody", None))
#endif // QT_CONFIG(statustip)
        self.actionLista_zawodnikow.setText(QCoreApplication.translate("MainWindow", u"Lista Zawodnik\u00f3w", None))
#if QT_CONFIG(tooltip)
        self.actionLista_zawodnikow.setToolTip(QCoreApplication.translate("MainWindow", u"Lista Zawodnik\u00f3w", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionLista_zawodnikow.setStatusTip(QCoreApplication.translate("MainWindow", u"Przechodzi do panelu z list\u0105 wszystkich zawodnik\u00f3w", None))
#endif // QT_CONFIG(statustip)
        self.actionRozpocznij_Wyswietlanie.setText(QCoreApplication.translate("MainWindow", u"Rozpocznij Wy\u015bwietlanie", None))
#if QT_CONFIG(tooltip)
        self.actionRozpocznij_Wyswietlanie.setToolTip(QCoreApplication.translate("MainWindow", u"Rozpocznij Wy\u015bwietlanie", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionRozpocznij_Wyswietlanie.setStatusTip(QCoreApplication.translate("MainWindow", u"Rozpoczyna wy\u015bwietlanie na urz\u0105dzeniu zewn\u0119trznym", None))
#endif // QT_CONFIG(statustip)
        self.actionZakoncz_Wyswietlanie.setText(QCoreApplication.translate("MainWindow", u"Zako\u0144cz Wy\u015bwietlanie", None))
#if QT_CONFIG(tooltip)
        self.actionZakoncz_Wyswietlanie.setToolTip(QCoreApplication.translate("MainWindow", u"Zako\u0144cz Wy\u015bwietlanie", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(statustip)
        self.actionZakoncz_Wyswietlanie.setStatusTip(QCoreApplication.translate("MainWindow", u"Przestaje wy\u015bwietla\u0107 na urz\u0105dzeniu zewn\u0119trznym", None))
#endif // QT_CONFIG(statustip)
        self.label.setText("")
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:14pt; font-weight:700;\">Zarz\u0105dzanie zawodnikami</span></p></body></html>", None))
        self.lineEditWyszukiwanieZawodnikow.setText("")
        self.lineEditWyszukiwanieZawodnikow.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Szukaj", None))
        self.menuBagno.setTitle(QCoreApplication.translate("MainWindow", u"Zawody", None))
        self.menuZawodnicy.setTitle(QCoreApplication.translate("MainWindow", u"Zawodnicy", None))
        self.menuWy_wietlanie.setTitle(QCoreApplication.translate("MainWindow", u"Wy\u015bwietlanie", None))
    # retranslateUi

