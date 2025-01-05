import sys
import textwrap
from datetime import datetime

from PyQt5.QtGui import QTextCursor
from dateutil.relativedelta import relativedelta
from PyQt5.QtCore import QDate, QTimer
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QApplication
from core import sesiz_uyari_mesaj
from core.sesiz_uyari_mesaj import SessizMesajDialog

from PyQt5.QtWidgets import *
from gui.hizlinotlar import Ui_Form

# VeriTabanı İşlemleri
import sqlite3


class SessizMesajDialog(QDialog):
    def __init__(self, mesaj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Bilgilendirme")

        # QPlainTextEdit widget'ı oluşturma
        self.metin_alani = QPlainTextEdit()
        self.metin_alani.setReadOnly(False)  # Metnin seçilebilir olmasını sağlar.
        self.metin_alani.setPlainText(mesaj)  # Mesajı metin alanına ekleme


        # Status bar oluşturma
        self.tarih_label = QLabel()
        self.selected_note_id = None

        layout = QVBoxLayout(self)
        layout.addWidget(self.metin_alani)
        layout.addWidget(self.tarih_label)  # QLabel'i layout'a ekleyin

        # self.tarihigoster.setText("Tarih: " + self.tarih_str)
        self.tarihigoster=QLabel("Tarih:")
        layout.addWidget(self.tarihigoster)

        guncelleButonu = QPushButton("Güncelle")
        guncelleButonu.clicked.connect(self.notumu_guncelle)
        layout.addWidget(guncelleButonu)

        kapatButonu = QPushButton("Kapat")
        kapatButonu.clicked.connect(self.close)
        layout.addWidget(kapatButonu)

    def notumu_guncelle(self):
        """
            Metin alanındaki metni kullanarak seçili notu günceller.

            Parametreler:
                metin_alani (QPlainTextEdit): Not metnini içeren metin alanı nesnesi.

            Döndürülen Değer:
                None.
            """
        try:
            # Seçili notun ID'sini al
            global selected_note_id

            # Yeni not metnini al
            yeni_not_metni = self.metin_alani.toPlainText()

            # Metin alanındaki metni satırlara ayır
            satirlar = yeni_not_metni.split("\n")

            # İlk satırı atla
            satirlar = satirlar[1:]

            if selected_note_id is not None:  # Seçili bir not varsa devam et
                # Veritabanı bağlantısını oluştur
                with sqlite3.connect("data/notlar.db") as baglanti:
                    islem = baglanti.cursor()

                    # Not metnini tek bir metin olarak kaydet
                    guncellenmis_not = "\n".join(satirlar)

                    # `not1` sütununu güncelle
                    islem.execute("UPDATE notlar SET not1 = ? WHERE id = ?", (guncellenmis_not, selected_note_id))

                    baglanti.commit()  # Değişiklikleri kaydet

        except Exception as e:
            print("Hata oluştu:", e)


        # self.not_listelekon()
        #     # Kullanıcıya güncelleme başarılı mesajı göster
        #     sessiz_mesaj_goster("Not başarıyla güncellendi.")
        # else:
        #     # Seçili bir not yoksa kullanıcıya uyarı mesajı göster
        #     sessiz_mesaj_goster("Güncellenecek bir not seçilmedi.")

        #     # Veritabanından notları al
        islem.execute("SELECT not1 FROM notlar")
        notlar = islem.fetchall()

        # Notları listeye ekle
        for not_metni in notlar:
            item = QListWidgetItem(not_metni[0])
            self.notu.lstListe.addItem(item)


# Bu fonksiyonu QMessageBox.information yerine kullanabilirsiniz
def sessiz_mesaj_goster(mesaj):
    dialog = SessizMesajDialog(mesaj)
    dialog.exec_()




baglanti = sqlite3.connect("data/notlar.db")
islem = baglanti.cursor()
baglanti.commit()

table = islem.execute("CREATE TABLE IF NOT EXISTS notlar(id INTEGER PRIMARY KEY AUTOINCREMENT, tarih datetime, not1 text, not2 text , not3 text)")
baglanti.commit()


class hizli_Not(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.notu = Ui_Form()
        self.notu.setupUi(self)
        self.notu.btnEkle.clicked.connect(self.not_ekle)
        self.notu.btnSil.clicked.connect(self.not_sil)
        # self.notu.lstListe.itemDoubleClicked.connect(self.show_date)
        self.notu.lstListe.itemDoubleClicked.connect(lambda item: self.show_date(item))


        # self.notu.lstListe.itemDoubleClicked.connect(lambda item: (self.notu_sec(item), self.show_date()))
        self.not_id = None  # not_id ve not_metni değişkenlerini tanımla
        self.not_metni = None
        # for i in range(5):
        #     self.notu.lstListe.addItem(f"Item {i}")
        #
        # self.setCentralWidget(self.notu.lstListe)
        #
        # self.baglanti = sqlite3.connect("notlar.db")
        # self.islem = self.baglanti.cursor()




    def not_ekle(self):
        # Line edit'ten metni al
        not_metni = self.notu.lneKayit.text().strip()

        # Şu anki tarihi al
        tarih = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Veritabanına ekleme işlemi
        baglanti = sqlite3.connect("data/notlar.db")
        islem = baglanti.cursor()
        islem.execute("INSERT INTO notlar (tarih, not1) VALUES (?, ?)", (tarih, not_metni))
        baglanti.commit()
        baglanti.close()
        self.notu.lneKayit.clear()
        self.not_listelekon()

    def not_listelekon(self):
        self.notu.lstListe.clear()

        # Veritabanına bağlan
        baglanti = sqlite3.connect("data/notlar.db")
        islem = baglanti.cursor()

        # Veritabanından notları al
        islem.execute("SELECT not1 FROM notlar")
        notlar = islem.fetchall()

        # Notları listeye ekle
        for not_metni in notlar:
            item = QListWidgetItem(not_metni[0])
            self.notu.lstListe.addItem(item)

        # Veritabanı bağlantısını kapat
        baglanti.close()

    def not_sil(self):
        # Seçilen öğeleri al
        secili_itemler = self.notu.lstListe.selectedItems()

        if len(secili_itemler) == 0:
            # Seçili bir öğe yoksa hata mesajı göster
            # QMessageBox.warning(self, "Hata", "Silinecek bir öğe seçiniz.")
            sessiz_mesaj_goster("LÜTFEN SİLİNECEK BİR NOT SEÇİNİZ.")
        else:
            # Seçili öğeleri sil
            for item in secili_itemler:
                self.notu.lstListe.takeItem(self.notu.lstListe.row(item))

            # Veritabanından da sil
            baglanti = sqlite3.connect("data/notlar.db")
            islem = baglanti.cursor()

            for item in secili_itemler:
                not_metni = item.text()
                islem.execute("DELETE FROM notlar WHERE not1 = ?", (not_metni,))

            baglanti.commit()
            baglanti.close()
            sessiz_mesaj_goster("SEÇİLEN NOT SİLİNDİ.")
            # QMessageBox.information(self, "Başarılı", "Seçilen öğeler başarıyla silindi.")

    def show_date(self, item):
        # Global olarak tanımlanan not_id değişkenini kullanmak için 'global' anahtar kelimesini kullanıyoruz
        global selected_note_id

        # Veritabanından seçilen öğenin ID'sini al
        with sqlite3.connect("data/notlar.db") as baglanti:
            islem = baglanti.cursor()
            not_metni = item.text()
            islem.execute("SELECT id FROM notlar WHERE not1 = ?", (not_metni,))
            selected_note_id = islem.fetchone()[0]

        # Veritabanından tarih bilgisini al
        with sqlite3.connect("data/notlar.db") as baglanti:
            islem = baglanti.cursor()
            islem.execute("SELECT tarih FROM notlar WHERE not1 = ?", (not_metni,))
            tarih = islem.fetchone()[0]

        # Tarihi formatla
        tarih_obj = datetime.strptime(tarih, "%Y-%m-%d %H:%M:%S")
        self.tarih_str = datetime.strftime(tarih_obj, "%d-%m-%Y")

        # Metni 50 karakterden sonra alt satıra geçir
        if len(not_metni) > 50:
            not_metni = "\n".join(textwrap.wrap(not_metni, 50))

        # Bilgileri mesaj olarak göster
        sessiz_mesaj_goster(f"NOTUN TARİHİ: {self.tarih_str}\n{not_metni}")

        # # Tarihi QLabel'e ata
        # self.tarihigoster.setText("Tarih: " + self.tarih_str)
        # 
