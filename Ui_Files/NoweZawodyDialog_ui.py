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
from PySide6.QtWidgets import (QAbstractButton, QAbstractSpinBox, QApplication, QComboBox,
    QDateTimeEdit, QDialog, QDialogButtonBox, QGridLayout,
    QHBoxLayout, QLabel, QLineEdit, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(863, 689)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Dialog)
        self.gridLayout.setObjectName(u"gridLayout")
        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 22, 2, 1, 1)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 3)

        self.inputs_layout = QVBoxLayout()
        self.inputs_layout.setObjectName(u"inputs_layout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_nazwa = QLineEdit(Dialog)
        self.lineEdit_nazwa.setObjectName(u"lineEdit_nazwa")

        self.horizontalLayout.addWidget(self.lineEdit_nazwa)


        self.inputs_layout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_2.addWidget(self.label_3)

        self.dateTime_input = QDateTimeEdit(Dialog)
        self.dateTime_input.setObjectName(u"dateTime_input")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.dateTime_input.sizePolicy().hasHeightForWidth())
        self.dateTime_input.setSizePolicy(sizePolicy1)
        self.dateTime_input.setFrame(True)
        self.dateTime_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dateTime_input.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.dateTime_input.setDateTime(QDateTime(QDate(2000, 1, 1), QTime(0, 0, 0)))
        self.dateTime_input.setCalendarPopup(True)

        self.horizontalLayout_2.addWidget(self.dateTime_input)


        self.inputs_layout.addLayout(self.horizontalLayout_2)

        self.konkurencja_layout1 = QHBoxLayout()
        self.konkurencja_layout1.setObjectName(u"konkurencja_layout1")
        self.label_1 = QLabel(Dialog)
        self.label_1.setObjectName(u"label_1")

        self.konkurencja_layout1.addWidget(self.label_1)

        self.comboBox_konkurencja1 = QComboBox(Dialog)
        self.comboBox_konkurencja1.setObjectName(u"comboBox_konkurencja1")
        sizePolicy1.setHeightForWidth(self.comboBox_konkurencja1.sizePolicy().hasHeightForWidth())
        self.comboBox_konkurencja1.setSizePolicy(sizePolicy1)

        self.konkurencja_layout1.addWidget(self.comboBox_konkurencja1)


        self.inputs_layout.addLayout(self.konkurencja_layout1)


        self.gridLayout.addLayout(self.inputs_layout, 8, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 7, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer_2, 21, 2, 1, 1)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:700;\">Stw\u00f3rz nowe zawody</span></p></body></html>", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:700;\">Nazwa zawod\u00f3w: </span></p></body></html>", None))
        self.lineEdit_nazwa.setPlaceholderText(QCoreApplication.translate("Dialog", u"Wpisz nazw\u0119 zawod\u00f3w", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:700;\">Data zawod\u00f3w: </span></p></body></html>", None))
        self.dateTime_input.setDisplayFormat(QCoreApplication.translate("Dialog", u"HH:mm dd/MM/yyyy ", None))
        self.label_1.setText(QCoreApplication.translate("Dialog", u"<html><head/><body><p align=\"center\"><span style=\" font-size:12pt; font-weight:700;\">Konkurencja: </span></p></body></html>", None))
    # retranslateUi

