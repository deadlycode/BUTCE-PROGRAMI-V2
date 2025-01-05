# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1069, 431)
        Form.setStyleSheet("""
        QPushButton {
            background-color: #f7f7f7;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 5px 10px;
            color: #333;
            font-family: "Helvetica Neue", sans-serif;
            font-size: 10px;
            font-weight: 400;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            transition: 0.2s ease-in-out;
        }

        QPushButton:hover {
            background-color: #fafafa;
            border-color: #bbb;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        QPushButton:pressed {
            background-color: #f5f5f5;
            border-color: #aaa;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }

        QLineEdit {
            background-color: #f7f7f7;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 4px;
            color: #333;
            font-family: "Helvetica Neue", sans-serif;
            font-size: 11px;
            font-weight: 400;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
            transition: 0.2s ease-in-out;
        }

        QLineEdit:focus {
            background-color: #fafafa;
            border-color: #bbb;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            font-size: 11px;
        }

        QTableWidget {
            background-color: #f7f7f7;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: "Helvetica Neue", sans-serif;
            font-size: 11px;
            font-weight: 400;
            color: #333;
            gridline-color: #ddd;
        }
        """)

        self.tblHesap = QtWidgets.QTableWidget(Form)
        self.tblHesap.setGeometry(QtCore.QRect(10, 20, 1051, 321))
        self.tblHesap.setRowCount(50)
        self.tblHesap.setColumnCount(10)
        self.tblHesap.setObjectName("tblHesap")

        # Set dark theme for table
        table_style = """
            QTableWidget {
                background-color: #2b2b2b;
                alternate-background-color: #323232;
                border: 1px solid #3b3b3b;
                gridline-color: #3b3b3b;
                color: #ffffff;
                selection-background-color: #3d5a80;
            }
            
            QTableWidget::item {
                padding: 4px;
            }
            
            QHeaderView::section {
                background-color: #3b3b3b;
                color: #ffffff;
                padding: 6px;
                border: none;
                font-weight: bold;
            }
            
            QTableCornerButton::section {
                background-color: #3b3b3b;
                border: none;
            }
        """
        self.tblHesap.setStyleSheet(table_style)
        
        # Enable alternating row colors
        self.tblHesap.setAlternatingRowColors(True)
        
        # Hide vertical header (row numbers)
        self.tblHesap.verticalHeader().setVisible(False)
        
        # Set selection behavior
        self.tblHesap.setSelectionBehavior(QtWidgets.QTableWidget.SelectRows)
        self.tblHesap.setSelectionMode(QtWidgets.QTableWidget.SingleSelection)

        # Add search boxes for each column
        self.searchBoxes = []
        for i in range(10):
            searchBox = QtWidgets.QLineEdit(Form)
            searchBox.setGeometry(QtCore.QRect(10 + (i * 105), 0, 100, 20))
            searchBox.setPlaceholderText(f"Arama {i+1}")
            searchBox.setObjectName(f"searchBox_{i}")
            searchBox.textChanged.connect(lambda text, col=i: self.filterTable(text, col))
            self.searchBoxes.append(searchBox)

        button_width = 120
        button_height = 35
        button_y = 350  # Butonları tablonun altına yerleştir
        button_spacing = 10

        self.cmbHesapTuru = QtWidgets.QComboBox(Form)
        self.cmbHesapTuru.setGeometry(QtCore.QRect(10, button_y, button_width, button_height))
        self.cmbHesapTuru.setObjectName("cmbHesapTuru")

        self.btnHesapListele = QtWidgets.QPushButton(Form)
        self.btnHesapListele.setGeometry(QtCore.QRect(140, button_y, button_width, button_height))
        self.btnHesapListele.setObjectName("btnHesapListele")

        self.btnHesapGuncelle = QtWidgets.QPushButton(Form)
        self.btnHesapGuncelle.setGeometry(QtCore.QRect(270, button_y, button_width, button_height))
        self.btnHesapGuncelle.setObjectName("btnHesapGuncelle")

        self.btnHesapSil = QtWidgets.QPushButton(Form)
        self.btnHesapSil.setGeometry(QtCore.QRect(400, button_y, button_width, button_height))
        self.btnHesapSil.setObjectName("btnHesapSil")

        self.btnisaret = QtWidgets.QPushButton(Form)
        self.btnisaret.setGeometry(QtCore.QRect(530, button_y, button_width, button_height))
        self.btnisaret.setObjectName("btnisaret")

        self.btnDisaAktar = QtWidgets.QPushButton(Form)
        self.btnDisaAktar.setGeometry(QtCore.QRect(660, button_y, button_width, button_height))
        self.btnDisaAktar.setObjectName("btnDisaAktar")

        self.btnIceAktar = QtWidgets.QPushButton(Form)
        self.btnIceAktar.setGeometry(QtCore.QRect(790, button_y, button_width, button_height))
        self.btnIceAktar.setObjectName("btnIceAktar")

        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(920, button_y, button_width, button_height))
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        self.cmbHesapTuru.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def filterTable(self, text, column):
        for row in range(self.tblHesap.rowCount()):
            item = self.tblHesap.item(row, column)
            if item is not None:
                if text.lower() in item.text().lower():
                    self.tblHesap.setRowHidden(row, False)
                else:
                    should_hide = True
                    for col in range(self.tblHesap.columnCount()):
                        if col != column:
                            other_item = self.tblHesap.item(row, col)
                            if other_item is not None and any(box.text().lower() in other_item.text().lower() for box in self.searchBoxes if box.text()):
                                should_hide = False
                                break
                    self.tblHesap.setRowHidden(row, should_hide)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Dijital Hesaplar"))
        self.btnHesapListele.setText(_translate("Form", "LİSTELE"))
        self.btnHesapGuncelle.setText(_translate("Form", "GÜNCELLE"))
        self.btnHesapSil.setText(_translate("Form", "SİL"))
        self.btnisaret.setText(_translate("Form", "İŞARETLE"))
        self.btnDisaAktar.setText(_translate("Form", "DIŞA AKTAR"))
        self.btnIceAktar.setText(_translate("Form", "İÇE AKTAR"))
        self.pushButton.setText(_translate("Form", "HESAP EKLE"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())