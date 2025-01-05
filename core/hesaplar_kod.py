import sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
from PyQt5.QtCore import QDate, QRect
from PyQt5.QtWidgets import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
import sqlite3
from core import sesiz_uyari_mesaj
from core.sesiz_uyari_mesaj import SessizMesajDialog
from gui.hesapkayit_gui import HesapKayitBolumu
from gui.hesaptablo_gui import Ui_Form
import hashlib
import csv
import os
import pandas as pd

# Veritabanı bağlantısı ve tablo oluşturma
baglanti = sqlite3.connect("data/veriler1.db")
islem = baglanti.cursor()
islem.execute('''CREATE TABLE IF NOT EXISTS hesaplar (
    hesap_id INTEGER PRIMARY KEY,
    hesap_turu TEXT,
    email TEXT,
    parola_hash TEXT,
    kullanici_adi TEXT,
    hesap_tarihi TEXT,
    takipci INTEGER,
    takip_edilen INTEGER,
    aciklama TEXT,
    notlar TEXT,
    renk TEXT
)''')

# Hesap türü tablosu oluşturma
islem.execute('''CREATE TABLE IF NOT EXISTS hesap_turu (
    tur_id INTEGER PRIMARY KEY,
    tur_adi TEXT UNIQUE
)''')

baglanti.commit()

class HesapKayidi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hesap_Kayit = HesapKayitBolumu()
        self.hesap_Kayit.setupUi(self)
        self.hesap_Kayit.btnHesapKayit.clicked.connect(self.HesapEkle)
        self.hesap_Kayit.btnYeniHesapTuru.clicked.connect(self.YeniHesapTuruEkle)
        
        # Initialize default account types if table is empty
        self.VarsayilanHesapTurleriOlustur()
        # Load account types from database
        self.HesapTurleriYukle()

    def VarsayilanHesapTurleriOlustur(self):
        varsayilan_turler = ["Google", "Instagram", "Twitter (X)", "Facebook", 
                            "Hotmail", "WordPress", "Hosting", "Diğer"]
        
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()
        
        # Check if table is empty
        islem.execute("SELECT COUNT(*) FROM hesap_turu")
        if islem.fetchone()[0] == 0:
            # Insert default types
            for tur in varsayilan_turler:
                try:
                    islem.execute("INSERT INTO hesap_turu (tur_adi) VALUES (?)", (tur,))
                except sqlite3.IntegrityError:
                    continue  # Skip if already exists
            baglanti.commit()
        
        baglanti.close()

    def HesapTurleriYukle(self):
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()
        
        # Clear existing items
        self.hesap_Kayit.cmbKayitHesapTuru.clear()
        
        # Get account types from database
        islem.execute("SELECT tur_adi FROM hesap_turu ORDER BY tur_adi")
        hesap_turleri = islem.fetchall()
        
        # Add account types to combobox
        for tur in hesap_turleri:
            self.hesap_Kayit.cmbKayitHesapTuru.addItem(tur[0])
            
        baglanti.close()

    def YeniHesapTuruEkle(self):
        yeni_tur = self.hesap_Kayit.lneYeniHesapTuru.text().strip()
        if not yeni_tur:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir hesap türü giriniz.")
            return
            
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()
        
        try:
            # Add new account type to database
            islem.execute("INSERT INTO hesap_turu (tur_adi) VALUES (?)", (yeni_tur,))
            baglanti.commit()
            
            # Reload account types to update combobox
            self.HesapTurleriYukle()
            
            # Select the newly added item
            index = self.hesap_Kayit.cmbKayitHesapTuru.findText(yeni_tur)
            if index >= 0:
                self.hesap_Kayit.cmbKayitHesapTuru.setCurrentIndex(index)
            
            self.hesap_Kayit.lneYeniHesapTuru.clear()
            QMessageBox.information(self, "Başarılı", f"'{yeni_tur}' hesap türü başarıyla eklendi.")
            
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Hata", "Bu hesap türü zaten mevcut!")
        finally:
            baglanti.close()

    def HesapEkle(self):
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()
        hesaptur = self.hesap_Kayit.cmbKayitHesapTuru.currentText()
        email = self.hesap_Kayit.lneHesapMail.text()
        parola = self.hesap_Kayit.lneHesapParola.text()
        kullaniciadi = self.hesap_Kayit.lneHesapKadi.text()
        hesaptarih = self.hesap_Kayit.lneHesapTarih.text()
        takipcim = self.hesap_Kayit.lneHesapTakipci.text()
        tedilen = self.hesap_Kayit.lneHesapTakipEdilen.text()
        aciklamam = self.hesap_Kayit.lneHesapAciklama.text()
        notlarim = self.hesap_Kayit.lneHesapNot.text()

        if not hesaptur or not email or not parola:
            print("Lütfen hesap türü, email ve parola alanlarını boş bırakmayınız.")
            return

        islem.execute('''INSERT INTO hesaplar (hesap_turu, email, parola_hash, kullanici_adi, hesap_tarihi, takipci, takip_edilen, aciklama, notlar)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                       (hesaptur, email, parola, kullaniciadi, hesaptarih, takipcim, tedilen,
                        aciklamam, notlarim))

        self.hesap_Kayit.cmbKayitHesapTuru.setCurrentIndex(-1)
        self.hesap_Kayit.lneHesapMail.clear()
        self.hesap_Kayit.lneHesapParola.clear()
        self.hesap_Kayit.lneHesapKadi.clear()
        self.hesap_Kayit.lneHesapTarih.clear()
        self.hesap_Kayit.lneHesapTakipci.clear()
        self.hesap_Kayit.lneHesapTakipEdilen.clear()
        self.hesap_Kayit.lneHesapAciklama.clear()
        self.hesap_Kayit.lneHesapNot.clear()

        baglanti.commit()
        baglanti.close()

class HesapTablosu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.hesap_Tablo = Ui_Form()
        self.hesap_Tablo.setupUi(self)
        self.hesapkayit = HesapKayidi()
        self.hesap_Tablo.pushButton.clicked.connect(self.Hesap_Kayit_Ekran)
        self.hesap_Tablo.btnHesapListele.clicked.connect(self.HesapListele)
        self.hesap_Tablo.btnHesapGuncelle.clicked.connect(self.HesapGuncelle)
        self.hesap_Tablo.btnHesapSil.clicked.connect(self.HesapSil)
        self.hesap_Tablo.btnisaret.clicked.connect(self.isaretle)
        
        # Load account types when form opens
        self.TabloHesapTurleriYukle()
        
        # Buton boyutları ve konumları güncelleniyor
        button_width = 120
        button_height = 35
        button_y = 370
        button_spacing = 10

        self.hesap_Tablo.cmbHesapTuru.setGeometry(QRect(10, button_y, button_width, button_height))
        
        buttons = [
            (self.hesap_Tablo.btnHesapListele, "LİSTELE"),
            (self.hesap_Tablo.btnHesapGuncelle, "GÜNCELLE"),
            (self.hesap_Tablo.btnHesapSil, "SİL"),
            (self.hesap_Tablo.btnisaret, "İŞARETLE"),
            (self.hesap_Tablo.btnDisaAktar, "DIŞA AKTAR"),
            (self.hesap_Tablo.btnIceAktar, "İÇE AKTAR"),
            (self.hesap_Tablo.pushButton, "HESAP EKLE")
        ]

        for i, (button, text) in enumerate(buttons, start=1):
            button.setGeometry(QRect(10 + i * (button_width + button_spacing), button_y, button_width, button_height))
            button.setText(text)

        self.hesap_Tablo.btnDisaAktar.clicked.connect(self.disa_aktar)
        self.hesap_Tablo.btnIceAktar.clicked.connect(self.ice_aktar)

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
        self.hesap_Tablo.tblHesap.setStyleSheet(table_style)
        
        # Enable alternating row colors
        self.hesap_Tablo.tblHesap.setAlternatingRowColors(True)
        
        # Hide vertical header (row numbers)
        self.hesap_Tablo.tblHesap.verticalHeader().setVisible(False)
        
        # Set selection behavior
        self.hesap_Tablo.tblHesap.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.hesap_Tablo.tblHesap.setSelectionMode(QAbstractItemView.SingleSelection)

    def renklendirmeIslemi(self):
        rowCount = self.hesap_Tablo.tblHesap.rowCount()
        for row in range(rowCount):
            aktiflikDurumuItem = self.hesap_Tablo.tblHesap.item(row, 1)
            if aktiflikDurumuItem.text() == "Instagram":
                for column in range(self.hesap_Tablo.tblHesap.columnCount()):
                    self.hesap_Tablo.tblHesap.item(row, column).setBackground(QColor(245, 245, 220))
            elif aktiflikDurumuItem.text() == "Google":
                for column in range(self.hesap_Tablo.tblHesap.columnCount()):
                    self.hesap_Tablo.tblHesap.item(row, column).setBackground(QColor(245, 255, 250))
            else:
                for column in range(self.hesap_Tablo.tblHesap.columnCount()):
                    self.hesap_Tablo.tblHesap.item(row, column).setBackground(QColor(255, 255, 255))

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def decrypt_password(self, parola_hash):
        return parola_hash

    def Hesap_Kayit_Ekran(self):
        self.hesapkayit.show()

    def HesapGuncelle(self):
        selected_item = self.hesap_Tablo.tblHesap.currentItem()
        if selected_item is None:
            return
        selected_row = selected_item.row()
        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()
            try:
                id_guncelle = int(self.hesap_Tablo.tblHesap.item(selected_row, 0).text())
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz ID değeri. ID bir tam sayı olmalıdır.")
                return

            def get_item_text(row, col):
                item = self.hesap_Tablo.tblHesap.item(row, col)
                return item.text() if item is not None else ""

            hesapturu = get_item_text(selected_row, 1)
            email = get_item_text(selected_row, 2)
            parola = get_item_text(selected_row, 3)
            kullaniciadi = get_item_text(selected_row, 4)
            hesaptarih = get_item_text(selected_row, 5)
            takipci = get_item_text(selected_row, 6)
            takipedilen = get_item_text(selected_row, 7)
            aciklamam = get_item_text(selected_row, 8)
            notu = get_item_text(selected_row, 9)

            renk_bilgisi = islem.execute("SELECT renk FROM hesaplar WHERE hesap_id = ?", (id_guncelle,)).fetchone()[0]

            sorgu = "UPDATE hesaplar SET hesap_turu = ?, email = ?, parola_hash = ?, kullanici_adi = ?, hesap_tarihi = ?, takipci = ?, takip_edilen = ?, aciklama = ?, notlar = ? WHERE hesap_id = ?"
            islem.execute(sorgu, (
            hesapturu, email, parola, kullaniciadi, hesaptarih, takipci, takipedilen, aciklamam, notu, id_guncelle))

            baglanti.commit()

            if islem.rowcount > 0:
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla güncellendi.")
            else:
                QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere sahip kayıt bulunamadı.")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")
        finally:
            baglanti.close()
        self.HesapListele()

    def HesapSil(self):
        selected_item = self.hesap_Tablo.tblHesap.currentItem()

        if selected_item is None:
            return

        selected_row = selected_item.row()

        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            try:
                id_sutun_indeksi = 0
                id_sil = int(self.hesap_Tablo.tblHesap.item(selected_row, id_sutun_indeksi).text())
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz ID değeri. ID bir tam sayı olmalıdır.")
                return

            sorgu = "DELETE FROM hesaplar WHERE hesap_id = ?"
            islem.execute(sorgu, (id_sil,))
            baglanti.commit()

            if islem.rowcount > 0:
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla silindi.")
            else:
                QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere sahip kayıt bulunamadı.")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")

        finally:
            baglanti.close()

        self.HesapListele()

    def HesapListele(self):
        self.hesap_Tablo.tblHesap.clear()
        self.hesap_Tablo.tblHesap.setRowCount(0)
        self.hesap_Tablo.tblHesap.setColumnCount(11)

        self.hesap_Tablo.tblHesap.setHorizontalHeaderLabels(
            ("ID", "Hesap Türü", "E-Mail", "Parola", "Kullanıcı Adı", "Hesap Tarihi",
             "Takipçi", "Takip", "Açıklama", "Not", "Renk")
        )

        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            secili_tur = self.hesap_Tablo.cmbHesapTuru.currentText()
            
            if secili_tur == "Hepsi":
                islem.execute("""SELECT hesap_id, hesap_turu, email, parola_hash, kullanici_adi, 
                                hesap_tarihi, takipci, takip_edilen, aciklama, notlar, renk 
                                FROM hesaplar ORDER BY hesap_id DESC""")
            else:
                islem.execute("""SELECT hesap_id, hesap_turu, email, parola_hash, kullanici_adi, 
                                hesap_tarihi, takipci, takip_edilen, aciklama, notlar, renk 
                                FROM hesaplar WHERE hesap_turu = ? ORDER BY hesap_id DESC""", (secili_tur,))

            hesaplar = islem.fetchall()

            for row_number, hesap in enumerate(hesaplar):
                self.hesap_Tablo.tblHesap.insertRow(row_number)
                for column_number, data in enumerate(hesap):
                    if column_number == 10:
                        continue
                    item = QTableWidgetItem(str(data))
                    if column_number == 3:
                        decrypted_password = self.decrypt_password(data)
                        item.setText(decrypted_password)
                    self.hesap_Tablo.tblHesap.setItem(row_number, column_number, item)

                renk_bilgisi = hesap[10]
                if renk_bilgisi:
                    try:
                        renk_parcalari = renk_bilgisi.split(';')
                        for renk_parca in renk_parcalari:
                            if ':' in renk_parca:
                                column, color = renk_parca.split(':')
                                column = int(column)
                                item = self.hesap_Tablo.tblHesap.item(row_number, column)
                                if item:
                                    item.setBackground(QColor(color))
                            else:
                                for col in range(self.hesap_Tablo.tblHesap.columnCount()):
                                    item = self.hesap_Tablo.tblHesap.item(row_number, col)
                                    if item:
                                        item.setBackground(QColor(renk_parca))
                    except Exception as e:
                        print(f"Renk uygulama hatası: {str(e)}")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Veriler listelenirken bir hata oluştu: {str(e)}")
        finally:
            baglanti.close()

    def TabloHesapTurleriYukle(self):
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()
        
        # Clear existing items
        self.hesap_Tablo.cmbHesapTuru.clear()
        
        # Add "Hepsi" option first
        self.hesap_Tablo.cmbHesapTuru.addItem("Hepsi")
        
        # Get account types from database
        islem.execute("SELECT tur_adi FROM hesap_turu ORDER BY tur_adi")
        hesap_turleri = islem.fetchall()
        
        # Add account types to combobox
        for tur in hesap_turleri:
            self.hesap_Tablo.cmbHesapTuru.addItem(tur[0])
            
        baglanti.close()

    def isaretle(self):
        selected_items = self.hesap_Tablo.tblHesap.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen işaretlenecek hücreleri seçin.")
            return

        color = QColorDialog.getColor()
        if color.isValid():
            color_hex = color.name()
            for item in selected_items:
                item.setBackground(color)
                row = item.row()
                column = item.column()
                id_value = self.hesap_Tablo.tblHesap.item(row, 0).text()
                self.save_color_to_db(id_value, color_hex, column)

    def save_color_to_db(self, id_value, color, column):
        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            islem.execute("SELECT renk FROM hesaplar WHERE hesap_id = ?", (id_value,))
            mevcut_renk = islem.fetchone()[0]

            if mevcut_renk:
                renk_parcalari = mevcut_renk.split(';')
                guncellendi = False
                for i, parca in enumerate(renk_parcalari):
                    if parca.startswith(f"{column}:"):
                        renk_parcalari[i] = f"{column}:{color}"
                        guncellendi = True
                        break
                if not guncellendi:
                    renk_parcalari.append(f"{column}:{color}")
                yeni_renk = ';'.join(renk_parcalari)
            else:
                yeni_renk = f"{column}:{color}"

            islem.execute("UPDATE hesaplar SET renk = ? WHERE hesap_id = ?", (yeni_renk, id_value))
            baglanti.commit()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Renk bilgisi kaydedilemedi: {str(e)}")
        finally:
            baglanti.close()

    def disa_aktar(self):
        try:
            dosya_yolu, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "", "Excel Dosyaları (*.xlsx);;CSV Dosyaları (*.csv)")
            if not dosya_yolu:
                return

            baglanti = sqlite3.connect("data/veriler1.db")
            
            # Mevcut filtre durumunu kontrol et
            selected_index = self.hesap_Tablo.cmbHesapTuru.currentIndex()
            if selected_index == 0:
                query = "SELECT * FROM hesaplar"
            else:
                selected_item = self.hesap_Tablo.cmbHesapTuru.currentText()
                query = f"SELECT * FROM hesaplar WHERE hesap_turu='{selected_item}'"

            df = pd.read_sql_query(query, baglanti)

            if dosya_yolu.endswith('.xlsx'):
                df.to_excel(dosya_yolu, index=False)
            elif dosya_yolu.endswith('.csv'):
                df.to_csv(dosya_yolu, index=False)

            QMessageBox.information(self, "Başarılı", "Veriler başarıyla dışa aktarıldı.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dışa aktarma sırasında bir hata oluştu: {str(e)}")
        finally:
            baglanti.close()

    def ice_aktar(self):
        baglanti = None
        try:
            dosya_yolu, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Excel Dosyaları (*.xlsx);;CSV Dosyaları (*.csv)")
            if not dosya_yolu:
                return

            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            if dosya_yolu.endswith('.xlsx'):
                df = pd.read_excel(dosya_yolu)
            elif dosya_yolu.endswith('.csv'):
                df = pd.read_csv(dosya_yolu)
            else:
                raise ValueError("Desteklenmeyen dosya formatı")

            for _, row in df.iterrows():
                islem.execute('''INSERT INTO hesaplar 
                                (hesap_turu, email, parola_hash, kullanici_adi, hesap_tarihi, 
                                takipci, takip_edilen, aciklama, notlar, renk)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (row['hesap_turu'], row['email'], row['parola_hash'], row['kullanici_adi'],
                            row['hesap_tarihi'], row['takipci'], row['takip_edilen'], row['aciklama'],
                            row['notlar'], row.get('renk', '')))

            baglanti.commit()
            QMessageBox.information(self, "Başarılı", "Veriler başarıyla içe aktarıldı.")
            self.HesapListele()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"İçe aktarma sırasında bir hata oluştu: {str(e)}")
        finally:
            if baglanti:
                baglanti.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    hesap_tablo = HesapTablosu()
    hesap_tablo.show()
    sys.exit(app.exec_())