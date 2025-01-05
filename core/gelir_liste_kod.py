import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import sqlite3
from core import sesiz_uyari_mesaj
from core.sesiz_uyari_mesaj import SessizMesajDialog
from gui.GelirListe_Gui import Ui_Form


# VeriTabanı İşlemleri


class GelirListe(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.gelirliste = Ui_Form()
        self.gelirliste.setupUi(self)
        self.gelirliste.btnListele.clicked.connect(self.GelirGetir)
        self.gelirliste.bitTarih.setDate(QDate.currentDate())  # bitDate widget'ı bugünün tarihine ayarlar

        self.bugun = QDate.currentDate()
        self.ayin_ilk_gunu = QDate(self.bugun.year(), self.bugun.month(), 1)  # Geçerli ayın ilk günü
        self.gelirliste.basTarih.setDate(self.ayin_ilk_gunu)
        self.gelirliste.btnGelirSil.clicked.connect(self.GelirSil)

    def GelirSil(self):
        # Seçilen kaydı silme fonksiyonu

        selected_item = self.gelirliste.tableWidget.currentItem()

        if not selected_item:
            # Eğer hiç hücre seçili değilse işlem yapma
            return

        # Kullanıcının seçtiği hücrenin bulunduğu satırı al
        selected_row = selected_item.row()

        # Seçilen satırın id değerini al
        id_sil_str = self.gelirliste.tableWidget.item(selected_row, 0).text()

        try:
            # Seçilen id'yi integer'a çevir
            id_sil = int(id_sil_str)

            # Kullanıcıya onay mesajı göster
            onay = QMessageBox.question(self, "Onay", "Seçili kaydı silmek istediğinizden emin misiniz?",
                                        QMessageBox.Yes | QMessageBox.No)

            if onay == QMessageBox.No:
                # Kullanıcı "Hayır" derse işlemi iptal et
                return

            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            # Veritabanından ilgili kaydı silen SQL sorgusu
            sorgu = "DELETE FROM gelirler WHERE id = ?"

            # Güncellenmiş sorguyu çalıştır
            islem.execute(sorgu, (id_sil,))
            baglanti.commit()

            if islem.rowcount > 0:
                # Eğer bir veya daha fazla satır silindi ise
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla silindi.")
            else:
                # Hiç satır silinmemeli (bu kod hata kontrolü için eklenmiştir)
                raise Exception("Beklenmedik bir hata oluştu.")

        except ValueError:
            # ID değeri geçersiz (sayısal olmayan bir değer veya boş)
            QMessageBox.warning(self, "Hata", "Geçersiz ID")

        except sqlite3.Error as e:
            # SQLite hatası durumunda bir mesaj göster
            QMessageBox.warning(self, "Hata", f"SQLite Hatası: {str(e)}")

        except Exception as e:
            # Diğer hata durumlarında bir mesaj göster
            QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")

        finally:
            # Veritabanı bağlantısını kapat
            baglanti.close()

    def GelirGetir(self):
        self.gelirliste.tableWidget.setColumnWidth(0, 85)
        self.gelirliste.tableWidget.setColumnWidth(1, 65)
        self.gelirliste.tableWidget.setColumnWidth(5, 200)
        self.gelirliste.tableWidget.setColumnWidth(4, 250)  # 4. sütunu 250 piksele genişlet

        self.gelirliste.tableWidget.clearContents()  # Sadece içeriği temizleyin
        self.gelirliste.tableWidget.setRowCount(0)

        self.gelirliste.tableWidget.setHorizontalHeaderLabels(
            ("ID", "Tarih", "Kaynak", "Miktar", "Açıklama")
        )

        bas_tarih = self.gelirliste.basTarih.date().toString("yyyy-MM-dd")
        bit_tarih = self.gelirliste.bitTarih.date().toString("yyyy-MM-dd")

        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        listele = """
                     SELECT 
                         id,  -- Keep the ID column
                         strftime('%d-%m-%Y', tarih) AS Tarih, 
                         kaynak AS Kaynak,
                         miktar AS Miktar, 
                         aciklama AS Aciklama
                     FROM gelirler 
                     WHERE tarih BETWEEN ? AND ?
                     ORDER BY tarih ASC 
                 """

        islem.execute(listele, (bas_tarih, bit_tarih))

        for indexSatir, kayitNumarasi in enumerate(islem.fetchall()):
            self.gelirliste.tableWidget.insertRow(indexSatir)

            for indexSutun, kayitSutun in enumerate(kayitNumarasi):
                if indexSutun == 3:  # Miktar sütununa "TL" ekle
                    self.gelirliste.tableWidget.setItem(
                        indexSatir, indexSutun, QTableWidgetItem(f"{kayitSutun} TL")
                    )
                else:
                    self.gelirliste.tableWidget.setItem(
                        indexSatir, indexSutun, QTableWidgetItem(str(kayitSutun))
                    )

            # Hide the ID column (which has index 0)
            self.gelirliste.tableWidget.hideColumn(0)

        baglanti.close()
