import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sqlite3

from .butce_gui import Ui_MainWindow

# VeriTabanı İşlemleri
import sqlite3

baglanti = sqlite3.connect("data/veriler1.db")
islem = baglanti.cursor()
baglanti.commit()

table = islem.execute("CREATE TABLE IF NOT EXISTS muhasebe(id INTEGER PRIMARY KEY AUTOINCREMENT, tarih datetime, market REAL, fatura REAL, harcama REAL, aciklama text)")
baglanti.commit()
gelirler=islem.execute("""
CREATE TABLE IF NOT EXISTS gelirler(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tarih datetime,
    kaynak VARCHAR(255),
    miktar REAL,
    aciklama TEXT
)""")
baglanti.commit()

class liste_tablosu(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.liste = Ui_MainWindow()
        self.liste.setupUi(self)
        
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
        self.liste.tableWidget.setStyleSheet(table_style)
        
        # Enable alternating row colors
        self.liste.tableWidget.setAlternatingRowColors(True)
        
        # Hide vertical header (row numbers)
        self.liste.tableWidget.verticalHeader().setVisible(False)
        
        # Set selection behavior
        self.liste.tableWidget.setSelectionBehavior(QTableWidget.SelectRows)
        self.liste.tableWidget.setSelectionMode(QTableWidget.SingleSelection)
        
        self.liste.btnListele.clicked.connect(self.toplalistele)
        self.liste.bitTarih.setDate(QDate.currentDate())  # bitDate widget'ı bugünün tarihine ayarlar

        self.bugun = QDate.currentDate()
        self.ayin_ilk_gunu = QDate(self.bugun.year(), self.bugun.month(), 1)  # Geçerli ayın ilk günü
        self.liste.basTarih.setDate(self.ayin_ilk_gunu)

    def toplamHarcamaGoster(self):
        # Tarih formatını YYYY-MM-DD olarak değiştir
        bas_tarih = self.liste.basTarih.date().toString("yyyy-MM-dd")
        bit_tarih = self.liste.bitTarih.date().toString("yyyy-MM-dd")

        # Veritabanı bağlantısı
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        # Toplam harcamayı hesaplamak için sorgu
        sorgu = """
        SELECT SUM(market) + SUM(fatura) + SUM(harcama) AS ToplamHarcama
        FROM muhasebe
        WHERE tarih BETWEEN ? AND ?
        """

        # Sorguyu çalıştır
        islem.execute(sorgu, (bas_tarih, bit_tarih))

        # Toplam harcamayı al
        toplam_harcama = islem.fetchone()[0]

        # Veritabanı bağlantısını kapat
        baglanti.close()

        # Mesaj kutusunda toplam harcamayı göster
        if toplam_harcama is not None:
            toplam_harcama_str = f"{toplam_harcama} TL"
            self.liste.lblToplamGider.setText(f"TOPLAM: "+toplam_harcama_str)
        else:
            self.liste.lblToplamGider.setText("Veri bulunamadı.")

    def toplalistele(self):
        self.liste.tableWidget.clear()
        self.liste.tableWidget.setRowCount(0)  # Tabloyu temizle

        self.liste.tableWidget.setHorizontalHeaderLabels(
            ("Tarih", "Toplam Market", "Toplam Faturalar", "Toplam Diğer", "Açıklama", "Toplam Harcama"))

        # self.liste.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Tarih formatını YYYY-MM-DD olarak değiştir
        bas_tarih = self.liste.basTarih.date().toString("yyyy-MM-dd")
        bit_tarih = self.liste.bitTarih.date().toString("yyyy-MM-dd")

        listele = """
        SELECT
        tarih,
        SUM(market) AS ToplamMarket,
        SUM(fatura) AS ToplamFaturalar,
        SUM(harcama) AS ToplamDiğer,
        GROUP_CONCAT(aciklama, ', ') AS Aciklama
        FROM muhasebe
        WHERE tarih BETWEEN ? AND ?
        GROUP BY tarih
        """

        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        islem.execute(listele, (bas_tarih, bit_tarih))

        for indexSatir, kayitNumarasi in enumerate(islem.fetchall()):
            self.liste.tableWidget.insertRow(indexSatir)
            for indexSutun, kayitSutun in enumerate(kayitNumarasi):
                if indexSutun == 0:  # Tarih sütunu
                    tarih_formatli = QDate.fromString(kayitSutun, "yyyy-MM-dd").toString("dd-MM-yyyy")
                    self.liste.tableWidget.setItem(indexSatir, indexSutun, QTableWidgetItem(tarih_formatli))
                elif indexSutun in [1, 2, 3]:  # Toplam Market, Toplam Faturalar ve Toplam Diğer sütunları
                    # TL sembolünü sadece bu sütunlara ekleyin
                    self.liste.tableWidget.setItem(indexSatir, indexSutun, QTableWidgetItem(f"{kayitSutun} TL"))
                else:
                    self.liste.tableWidget.setItem(indexSatir, indexSutun, QTableWidgetItem(str(kayitSutun)))

            # Toplam Harcamayı hesapla ve göster
            toplam_harcama = kayitNumarasi[1] + kayitNumarasi[2] + kayitNumarasi[3]
            harcama_item = QTableWidgetItem(f"{toplam_harcama} TL")
            self.liste.tableWidget.setItem(indexSatir, 5, harcama_item)

        baglanti.close()

        self.toplamHarcamaGoster()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = liste_tablosu()
    window.show()
    sys.exit(app.exec_())
