from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication

class SessizMesajDialog(QDialog):
    def __init__(self, mesaj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bilgilendirme")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(mesaj))
        kapatButonu = QPushButton("Kapat")
        kapatButonu.clicked.connect(self.close)
        layout.addWidget(kapatButonu)

# Bu fonksiyonu QMessageBox.information yerine kullanabilirsiniz
def sessiz_mesaj_goster(mesaj):
    app = QApplication([])
    dialog = SessizMesajDialog(mesaj)
    dialog.exec_()

# Kullanımı:
# sessiz_mesaj_goster("NOTUN TARİHİ: 01-01-2024")