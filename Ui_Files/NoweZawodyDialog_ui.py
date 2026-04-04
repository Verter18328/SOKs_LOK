# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NoweZawodyDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QAbstractSpinBox, QApplication, QDateTimeEdit,
    QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(580, 616)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.konkurencje_list = QListWidget(Dialog)
        self.konkurencje_list.setObjectName(u"konkurencje_list")

        self.gridLayout.addWidget(self.konkurencje_list, 6, 0, 1, 8)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.NoButton)

        self.gridLayout.addWidget(self.buttonBox, 10, 0, 1, 1)

        self.buttonBox_zawody = QDialogButtonBox(Dialog)
        self.buttonBox_zawody.setObjectName(u"buttonBox_zawody")
        self.buttonBox_zawody.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Save)

        self.gridLayout.addWidget(self.buttonBox_zawody, 10, 7, 1, 1)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 8)

        self.button_dodaj_konkurencje = QPushButton(Dialog)
        self.button_dodaj_konkurencje.setObjectName(u"button_dodaj_konkurencje")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.button_dodaj_konkurencje.sizePolicy().hasHeightForWidth())
        self.button_dodaj_konkurencje.setSizePolicy(sizePolicy1)
        self.button_dodaj_konkurencje.setLayoutDirection(Qt.RightToLeft)

        self.gridLayout.addWidget(self.button_dodaj_konkurencje, 5, 7, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_nazwa_zawodow = QLineEdit(Dialog)
        self.lineEdit_nazwa_zawodow.setObjectName(u"lineEdit_nazwa_zawodow")

        self.horizontalLayout.addWidget(self.lineEdit_nazwa_zawodow)


        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 8)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        sizePolicy2.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.dateTimeEdit_data_zawodow = QDateTimeEdit(Dialog)
        self.dateTimeEdit_data_zawodow.setObjectName(u"dateTimeEdit_data_zawodow")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.dateTimeEdit_data_zawodow.sizePolicy().hasHeightForWidth())
        self.dateTimeEdit_data_zawodow.setSizePolicy(sizePolicy3)
        self.dateTimeEdit_data_zawodow.setAlignment(Qt.AlignCenter)
        self.dateTimeEdit_data_zawodow.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.dateTimeEdit_data_zawodow.setProperty(u"showGroupSeparator", False)
        self.dateTimeEdit_data_zawodow.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateTimeEdit_data_zawodow)


        self.gridLayout.addLayout(self.horizontalLayout_2, 4, 0, 1, 8)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Konkurencje: </span></p></body></html>", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:700;\">Stw\u00f3rz nowe zawody</span></p></body></html>", None))
        self.button_dodaj_konkurencje.setText(QCoreApplication.translate("Dialog", u"Dodaj", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Nazwa Zawod\u00f3w: </span></p></body></html>", None))
        self.lineEdit_nazwa_zawodow.setPlaceholderText(QCoreApplication.translate("Dialog", u"Wpisz nazw\u0119 zawod\u00f3w", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600;\">Data Zawod\u00f3w: </span></p></body></html>", None))
        self.dateTimeEdit_data_zawodow.setDisplayFormat(QCoreApplication.translate("Dialog", u"HH:mm d.MM.yyyy", None))
    # retranslateUi

