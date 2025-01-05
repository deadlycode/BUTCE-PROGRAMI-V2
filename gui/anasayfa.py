import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from .listele import liste_tablosu
from .anamenu import Ui_Form
from core.hizli_not_kod import hizli_Not
from core.gelir_liste_kod import GelirListe
import sqlite3
from PyQt5.QtCore import QDate
from datetime import datetime
from core.hesaplar_kod import HesapTablosu
import google.generativeai as genai
from core.config import GEMINI_API_KEY, MARKET_HARCAMA_LIMITLERI, FATURA_HARCAMA_LIMITLERI, DIGER_HARCAMA_LIMITLERI, HARCAMA_KATEGORILERI

class AIAnalysisThread(QThread):
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    
    def __init__(self, prompt):
        super().__init__()
        self.prompt = prompt
        
    def run(self):
        try:
            # Simüle edilmiş ilerleme
            self.progress.emit(20)
            # AI modelini başlat
            self.progress.emit(40)
            response = genai.GenerativeModel('gemini-pro').generate_content(self.prompt)
            self.progress.emit(80)
            analysis = response.text
            self.progress.emit(100)
            self.finished.emit(analysis)
        except Exception as e:
            self.finished.emit(f"Hata oluştu: {str(e)}")

class ProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Analizi Yapılıyor")
        self.setFixedSize(400, 100)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout()
        
        # Progress bar stil tanımı
        style = """
        QProgressBar {
            border: 2px solid #3d5a80;
            border-radius: 5px;
            text-align: center;
            background-color: #2b2b2b;
            height: 20px;
        }
        QProgressBar::chunk {
            background-color: #3d5a80;
            border-radius: 3px;
        }
        """
        
        self.progress_label = QLabel("AI analizi yapılıyor...")
        self.progress_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(style)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.progress_label.setText("Analiz tamamlandı!")

class anamenu_ui(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.listepencere=liste_tablosu()
        self.ui.btnListele.clicked.connect(self.tablo_liste)
        self.ui.pushButton_2.clicked.connect(self.kayit_yap)
        self.ui.kayitTarih.selectionChanged.connect(self.tarihdegistir)
        self.aylikliste()
        self.ui.btnSil.clicked.connect(lambda: self.kayitsil())
        self.ui.chkToplam.stateChanged.connect(self.checkbox_kontrol)
        self.checkbox_kontrol()  # İlk başta checkbox durumuna göre işlevi çağır
        self.ui.btnGuncelle.clicked.connect(self.guncelle)
        self.notlarim=hizli_Not()
        self.gelirlistesi=GelirListe()
        self.ui.btnGelirListe.clicked.connect(self.GelirListeGoruntule)
        self.ui.btnNot.clicked.connect(self.not_listele)
        self.ui.chkButunKayitlar.stateChanged.connect(self.checkbox_kayitkontrol)
        self.ui.btnGelirKayit.clicked.connect(self.GelirKayit)
        self.tablogoster=HesapTablosu()
        self.ui.btnHesaplarGiris.clicked.connect(self.Tabloyu_Goster)
        self.ui.btnAIAnalysis.clicked.connect(self.analyze_expenses)
        
        # Initialize Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Add AI analysis column if not exists
        self.setup_database()
        
        # Enable alternating row colors for better readability
        self.ui.tblYeni.setAlternatingRowColors(True)
        
        # Initialize database and setup
        self.setup_database()
        self.aylikliste()

    def setup_database(self):
        try:
            conn = sqlite3.connect('data/veriler1.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='muhasebe';
            ''')
            if cursor.fetchone():
                cursor.execute('''
                    PRAGMA table_info(muhasebe);
                ''')
                columns = [info[1] for info in cursor.fetchall()]
                if 'ai_analysis' not in columns:
                    cursor.execute('''
                        ALTER TABLE muhasebe
                        ADD COLUMN ai_analysis TEXT;
                    ''')
                    conn.commit()
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Database Error", f"Error setting up database: {str(e)}")

    def analyze_expenses(self):
        try:
            # Seçili satır kontrolü
            selected_items = self.ui.tblYeni.selectedItems()
            if not selected_items:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Uyarı")
                
                # Toplam listele durumuna göre mesaj ve butonları ayarla
                if self.ui.chkToplam.isChecked():
                    msg.setText("Satır seçilmedi!")
                    msg.setInformativeText("Lütfen analiz edilecek bir satır seçin veya ayın tamamını analiz edin.")
                    aylik_analiz = msg.addButton("AYI TOPLAM ANALİZ ET", QMessageBox.ActionRole)
                    msg.addButton("İptal", QMessageBox.RejectRole)
                    msg.exec_()
                    
                    # Eğer "AYI TOPLAM ANALİZ ET" seçildiyse
                    if msg.clickedButton() == aylik_analiz:
                        self.analyze_monthly_totals()
                else:
                    msg.setText("Lütfen analiz edilecek bir satır seçin!")
                    msg.setInformativeText("Analiz etmek istediğiniz satıra tıklayarak seçim yapabilirsiniz.")
                    msg.addButton("Tamam", QMessageBox.AcceptRole)
                    msg.exec_()
                return

            # Get selected row data
            current_row = self.ui.tblYeni.currentRow()
            
            # Toplam listele durumunu kontrol et
            toplam_listele = self.ui.chkToplam.isChecked()
            
            # Sütun indekslerini belirle
            if toplam_listele:
                tarih_sutun = 0    # Tarih sütunu
                market_sutun = 1    # Market sütunu
                fatura_sutun = 2    # Fatura sütunu
                diger_sutun = 3     # Diğer sütunu
                aciklama_sutun = 4  # Açıklama sütunu
                toplam_sutun = 5    # Toplam sütunu
                
                # Tüm değerleri al ve dönüştür
                market_item = self.ui.tblYeni.item(current_row, market_sutun)
                fatura_item = self.ui.tblYeni.item(current_row, fatura_sutun)
                diger_item = self.ui.tblYeni.item(current_row, diger_sutun)
                toplam_item = self.ui.tblYeni.item(current_row, toplam_sutun)
                
                print("\nDönüşüm öncesi değerler:")
                print(f"Market text: {market_item.text() if market_item else 'None'}")
                print(f"Fatura text: {fatura_item.text() if fatura_item else 'None'}")
                print(f"Diğer text: {diger_item.text() if diger_item else 'None'}")
                print(f"Toplam text: {toplam_item.text() if toplam_item else 'None'}")
                
                market = self.temizle_ve_donustur(market_item.text() if market_item else "0")
                fatura = self.temizle_ve_donustur(fatura_item.text() if fatura_item else "0")
                diger = self.temizle_ve_donustur(diger_item.text() if diger_item else "0")
                toplam = self.temizle_ve_donustur(toplam_item.text() if toplam_item else "0")
                
                print("\nDönüşüm sonrası değerler:")
                print(f"Market: {market}")
                print(f"Fatura: {fatura}")
                print(f"Diğer: {diger}")
                print(f"Toplam: {toplam}")
                
                # Açıklamayı al
                aciklama_item = self.ui.tblYeni.item(current_row, aciklama_sutun)
                aciklama = aciklama_item.text() if aciklama_item else ""

                # Yüzde hesaplama fonksiyonu
                def hesapla_yuzde(kismi, toplam):
                    if toplam == 0:
                        return 0.0
                    return (kismi/toplam*100)

                # Toplam listele için özel prompt hazırla
                prompt = f"""
                Lütfen aşağıdaki günlük toplam harcama kaydını detaylı olarak analiz et:
                
                Market Harcaması: {market} TL
                Fatura Ödemesi: {fatura} TL
                Diğer Harcamalar: {diger} TL
                Toplam Harcama: {toplam} TL
                
                Harcama Detayları: {aciklama}
                
                Analiz kriterleri:
                1. Harcama Dağılımı Analizi:
                   - Market harcaması toplam içinde %{hesapla_yuzde(market, toplam):.1f}
                   - Fatura ödemesi toplam içinde %{hesapla_yuzde(fatura, toplam):.1f}
                   - Diğer harcamalar toplam içinde %{hesapla_yuzde(diger, toplam):.1f}
                
                2. Kategori Bazlı Değerlendirme:
                   - Market harcaması makul mü? ({MARKET_HARCAMA_LIMITLERI['min']}-{MARKET_HARCAMA_LIMITLERI['max']} TL arası normal)
                   - Fatura ödemesi makul mü? ({FATURA_HARCAMA_LIMITLERI['min']}-{FATURA_HARCAMA_LIMITLERI['max']} TL arası normal)
                   - Diğer harcamalar makul mü? ({DIGER_HARCAMA_LIMITLERI['min']}-{DIGER_HARCAMA_LIMITLERI['max']} TL arası normal)
                
                3. Detaylı İnceleme:
                   - Her bir harcama kalemi gerekli mi?
                   - Harcamalar arasında dengesizlik var mı?
                   - Optimize edilebilecek alanlar var mı?
                
                4. Tasarruf İmkanları:
                   - Hangi kategoride tasarruf yapılabilir?
                   - Alternatif çözümler neler olabilir?
                   - Gereksiz harcamalar var mı?
                
                Lütfen şu formatta yanıt ver:
                
                ## 💰 Genel Değerlendirme
                - Toplam Harcama: {toplam} TL
                - Market: {market} TL (%{hesapla_yuzde(market, toplam):.1f})
                - Fatura: {fatura} TL (%{hesapla_yuzde(fatura, toplam):.1f})
                - Diğer: {diger} TL (%{hesapla_yuzde(diger, toplam):.1f})
                
                ## 📊 Kategori Analizi
                - Market Değerlendirmesi: [Makul/Yüksek/Düşük]
                - Fatura Değerlendirmesi: [Makul/Yüksek/Düşük]
                - Diğer Harcamalar: [Makul/Yüksek/Düşük]
                
                ## 🎯 Bulgular
                - [Her kategori için önemli tespitler]
                
                ## 💡 Tasarruf Önerileri
                - [Her kategori için öneriler]
                
                ## ⚠️ Dikkat Edilmesi Gerekenler
                - [Önemli uyarılar ve tavsiyeler]
                """
            else:
                # Normal görünüm - mevcut sütun yapısı
                def temizle_ve_donustur(deger_text):
                    if not deger_text:
                        return 0.0
                    # Önce TL ve boşlukları temizle
                    deger_text = deger_text.replace("TL", "").strip()
                    if deger_text == "0.0" or deger_text == "0,0" or deger_text == "0":
                        return 0.0
                    try:
                        # Eğer sadece sayı ve nokta varsa direkt dönüştür
                        if all(c.isdigit() or c == '.' for c in deger_text):
                            return float(deger_text)
                        # Binlik ayracı ve virgül varsa
                        deger_text = deger_text.replace(".", "")  # Binlik ayracını kaldır
                        deger_text = deger_text.replace(",", ".")  # Virgülü noktaya çevir
                        return float(deger_text)
                    except ValueError as e:
                        print(f"Dönüşüm hatası: {deger_text} -> {str(e)}")
                        return 0.0

                # Market değeri (2. sütun)
                market_item = self.ui.tblYeni.item(current_row, 2)
                market_text = market_item.text() if market_item else "0"
                market = temizle_ve_donustur(market_text)
                
                # Fatura değeri (3. sütun)
                fatura_item = self.ui.tblYeni.item(current_row, 3)
                fatura_text = fatura_item.text() if fatura_item else "0"
                fatura = temizle_ve_donustur(fatura_text)
                
                # Harcama değeri (4. sütun)
                harcama_item = self.ui.tblYeni.item(current_row, 4)
                harcama_text = harcama_item.text() if harcama_item else "0"
                harcama = temizle_ve_donustur(harcama_text)
                
                # Açıklama (5. sütun)
                aciklama_item = self.ui.tblYeni.item(current_row, 5)
                aciklama = aciklama_item.text() if aciklama_item else ""

                # Normal görünüm için mevcut prompt kullan
                prompt = f"""
                Lütfen aşağıdaki günlük harcama kaydını detaylı olarak analiz et:
                
                Market Harcaması: {market} TL
                Fatura: {fatura} TL
                Diğer Harcama: {harcama} TL
                Açıklama: {aciklama}
                
                [Mevcut prompt devam ediyor...]
                """

            # Progress dialog oluştur
            progress_dialog = ProgressDialog(self)
            
            # AI thread'ini başlat
            self.analysis_thread = AIAnalysisThread(prompt)
            
            # Thread sinyallerini bağla
            self.analysis_thread.progress.connect(progress_dialog.update_progress)
            if toplam_listele:
                self.analysis_thread.finished.connect(lambda analysis: self.show_analysis_results(analysis, 0, 0, diger, aciklama))
            else:
                self.analysis_thread.finished.connect(lambda analysis: self.show_analysis_results(analysis, market, fatura, harcama, aciklama))
            self.analysis_thread.finished.connect(progress_dialog.close)
            
            # Thread'i başlat ve dialog'u göster
            self.analysis_thread.start()
            progress_dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Analiz sırasında bir hata oluştu: {str(e)}")

    def show_analysis_results(self, analysis, market, fatura, harcama, aciklama):
        # Analiz sonuçlarını göster
        analysis_dialog = QDialog(self)
        analysis_dialog.setWindowTitle("AI Analiz Sonucu")
        analysis_dialog.setMinimumWidth(500)
        analysis_dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # Create text browser for analysis
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        text_browser.setMarkdown(analysis)
        layout.addWidget(text_browser)
        
        # Add close button
        close_button = QPushButton("Kapat")
        close_button.clicked.connect(analysis_dialog.close)
        layout.addWidget(close_button)
        
        analysis_dialog.setLayout(layout)
        
        # Update database
        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            cursor = baglanti.cursor()
            cursor.execute("UPDATE muhasebe SET ai_analysis = ? WHERE market = ? AND fatura = ? AND harcama = ? AND aciklama = ?",
                         (analysis, market, fatura, harcama, aciklama))
            baglanti.commit()
        except Exception as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Analiz kaydedilirken hata oluştu: {str(e)}")
        
        analysis_dialog.exec_()

    def analyze_monthly_totals(self):
        try:
            # İlerleme çubuğunu göster
            progress_dialog = QProgressDialog(self)
            progress_dialog.setLabelText("Aylık toplam analiz yapılıyor...")
            progress_dialog.setRange(0, 100)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.show()
            
            # Mevcut ayın verilerini topla
            current_date = QDate.currentDate()
            current_month = current_date.month()
            current_year = current_date.year()
            
            market_total = 0.0
            fatura_total = 0.0
            diger_total = 0.0
            aciklamalar = []
            
            # Tablodaki tüm satırları kontrol et
            row_count = self.ui.tblYeni.rowCount()
            for row in range(row_count):
                # Tarih sütunundaki veriyi al
                tarih_item = self.ui.tblYeni.item(row, 0)
                if tarih_item:
                    tarih_str = tarih_item.text()
                    try:
                        # Tarih formatını kontrol et ve dönüştür
                        tarih = QDate.fromString(tarih_str, "dd-MM-yyyy")
                        if tarih.month() == current_month and tarih.year() == current_year:
                            # Bu satır mevcut aya ait, değerleri topla
                            market_item = self.ui.tblYeni.item(row, 1)
                            fatura_item = self.ui.tblYeni.item(row, 2)
                            diger_item = self.ui.tblYeni.item(row, 3)
                            aciklama_item = self.ui.tblYeni.item(row, 4)
                            
                            if market_item:
                                market_total += self.temizle_ve_donustur(market_item.text())
                            if fatura_item:
                                fatura_total += self.temizle_ve_donustur(fatura_item.text())
                            if diger_item:
                                diger_total += self.temizle_ve_donustur(diger_item.text())
                            if aciklama_item and aciklama_item.text().strip():
                                aciklamalar.append(aciklama_item.text())
                    except Exception as e:
                        print(f"Tarih dönüşüm hatası: {str(e)}")
                        continue
                
                # İlerleme çubuğunu güncelle
                progress = int((row + 1) / row_count * 100)
                progress_dialog.setValue(progress)
                
                if progress_dialog.wasCanceled():
                    return
            
            # Toplam hesapla
            toplam_total = market_total + fatura_total + diger_total
            
            # Birleştirilmiş açıklama oluştur
            birlesik_aciklama = " | ".join(aciklamalar)
            
            # AI analizi başlat
            self.start_ai_analysis(market_total, fatura_total, diger_total, toplam_total, birlesik_aciklama, True)
            
            # İlerleme çubuğunu kapat
            progress_dialog.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Aylık analiz sırasında bir hata oluştu: {str(e)}")

    def start_ai_analysis(self, market, fatura, diger, toplam, aciklama, is_monthly=False):
        # İlerleme çubuğunu göster
        progress_dialog = QProgressDialog(self)
        progress_dialog.setLabelText("AI analizi yapılıyor...")
        progress_dialog.setRange(0, 100)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        # Yüzde hesaplama fonksiyonu
        def hesapla_yuzde(kismi, toplam):
            if toplam == 0:
                return 0.0
            return (kismi/toplam*100)

        # Prompt hazırla
        prompt = f"""
        Lütfen aşağıdaki {'aylık' if is_monthly else 'günlük'} toplam harcama kaydını detaylı olarak analiz et:
        
        Market Harcaması: {market} TL
        Fatura Ödemesi: {fatura} TL
        Diğer Harcamalar: {diger} TL
        Toplam Harcama: {toplam} TL
        
        Harcama Detayları: {aciklama}
        
        Analiz kriterleri:
        1. Harcama Dağılımı Analizi:
           - Market harcaması toplam içinde %{hesapla_yuzde(market, toplam):.1f}
           - Fatura ödemesi toplam içinde %{hesapla_yuzde(fatura, toplam):.1f}
           - Diğer harcamalar toplam içinde %{hesapla_yuzde(diger, toplam):.1f}
        
        2. Kategori Bazlı Değerlendirme:
           - {'Aylık' if is_monthly else 'Günlük'} market harcaması makul mü? ({MARKET_HARCAMA_LIMITLERI['min']}-{MARKET_HARCAMA_LIMITLERI['max']} TL arası normal)
           - {'Aylık' if is_monthly else 'Günlük'} fatura ödemesi makul mü? ({FATURA_HARCAMA_LIMITLERI['min']}-{FATURA_HARCAMA_LIMITLERI['max']} TL arası normal)
           - {'Aylık' if is_monthly else 'Günlük'} diğer harcamalar makul mü? ({DIGER_HARCAMA_LIMITLERI['min']}-{DIGER_HARCAMA_LIMITLERI['max']} TL arası normal)
        
        3. Detaylı İnceleme:
           - Her bir harcama kalemi gerekli mi?
           - Harcamalar arasında dengesizlik var mı?
           - Optimize edilebilecek alanlar var mı?
        
        4. Tasarruf İmkanları:
           - Hangi kategoride tasarruf yapılabilir?
           - Alternatif çözümler neler olabilir?
           - Gereksiz harcamalar var mı?
        
        Lütfen şu formatta yanıt ver:
        
        ## 💰 {'Aylık' if is_monthly else 'Günlük'} Genel Değerlendirme
        - Toplam Harcama: {toplam} TL
        - Market: {market} TL (%{hesapla_yuzde(market, toplam):.1f})
        - Fatura: {fatura} TL (%{hesapla_yuzde(fatura, toplam):.1f})
        - Diğer: {diger} TL (%{hesapla_yuzde(diger, toplam):.1f})
        
        ## 📊 Kategori Analizi
        - Market Değerlendirmesi: [Makul/Yüksek/Düşük]
        - Fatura Değerlendirmesi: [Makul/Yüksek/Düşük]
        - Diğer Harcamalar: [Makul/Yüksek/Düşük]
        
        ## 🎯 Bulgular
        - [Her kategori için önemli tespitler]
        
        ## 💡 Tasarruf Önerileri
        - [Her kategori için öneriler]
        
        ## ⚠️ Dikkat Edilmesi Gerekenler
        - [Önemli uyarılar ve tavsiyeler]
        """

        # AI analiz thread'ini başlat
        self.analysis_thread = AIAnalysisThread(prompt)
        self.analysis_thread.start()

        # Thread sinyallerini bağla
        self.analysis_thread.progress.connect(progress_dialog.setValue)  # update_progress yerine setValue kullan
        self.analysis_thread.finished.connect(lambda analysis: self.show_analysis_results(analysis, market, fatura, diger, aciklama))
        self.analysis_thread.finished.connect(progress_dialog.close)

    def Tabloyu_Goster(self):
        self.tablogoster.show()

    def GelirListeGoruntule(self):
        self.gelirlistesi.show()

    def checkbox_kayitkontrol(self):
        if self.ui.chkButunKayitlar.isChecked():
            self.HepsiniGoster()
        else:
            self.aylikliste()

    def checkbox_kontrol(self):
        if self.ui.chkToplam.isChecked():
            self.ayliktoplam()
        else:
            self.aylikliste()

    def not_listele(self):
        self.notlarim.show()
        self.notlarim.not_listelekon()

    def tablo_liste(self):
        self.listepencere.show()

    def tarihdegistir(self):
        self.tarih = self.ui.kayitTarih.selectedDate().toString("yyyy-MM-dd")

    from PyQt5.QtCore import QDate

    def ayliktoplam(self):
        self.ui.tblYeni.setColumnWidth(0, 60)
        self.ui.tblYeni.setColumnWidth(1, 70)
        self.ui.tblYeni.setColumnWidth(2, 70)
        self.ui.tblYeni.setColumnWidth(3, 60)
        self.ui.tblYeni.setColumnWidth(4, 150)
        self.ui.tblYeni.setColumnWidth(5, 80)
        self.ui.tblYeni.clear()
        self.ui.tblYeni.setRowCount(0)  # Tabloyu temizle
        self.ui.tblYeni.setHorizontalHeaderLabels(
            ("Tarih", "T.Market", "T.Fatura", "Diğer", "Açıklama", "Toplam Harcama"))

        # Bulunduğumuz ayın ilk ve son günlerini hesapla
        simdiki_ayin_ilk_gunu = QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)
        simdiki_ayin_son_gunu = QDate(QDate.currentDate().year(), QDate.currentDate().month(),
                                      QDate.currentDate().daysInMonth())

        # ayin_ilk_gunu ve ayin_son_gunu değişkenlerini str tipine dönüştür
        ayin_ilk_gunu = simdiki_ayin_ilk_gunu.toString("yyyy-MM-dd")
        ayin_son_gunu = simdiki_ayin_son_gunu.toString("yyyy-MM-dd")

        # Bulunduğumuz aya ait kayıtları veritabanından sorgula
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        sorgu = """
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

        islem.execute(sorgu, (ayin_ilk_gunu, ayin_son_gunu))

        # Sonuçları tabloya ekle
        kayitlar = islem.fetchall()
        for satir in kayitlar:
            # Tarihi doğru formata dönüştür
            tarih_formatli = QDate.fromString(satir[0], "yyyy-MM-dd").toString("dd-MM-yyyy")

            # TL sembolünü Toplam Market, Toplam Faturalar ve Toplam Diğer sütunlarına ekleyin
            market_item = QTableWidgetItem(f"{satir[1]} TL")
            fatura_item = QTableWidgetItem(f"{satir[2]} TL")
            diger_item = QTableWidgetItem(f"{satir[3]} TL")

            self.ui.tblYeni.insertRow(self.ui.tblYeni.rowCount())
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 0, QTableWidgetItem(tarih_formatli))
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 1, market_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 2, fatura_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 3, diger_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 4, QTableWidgetItem(satir[4]))

            # Toplam Harcamayı hesapla ve göster
            toplam_harcama = satir[1] + satir[2] + satir[3]
            harcama_item = QTableWidgetItem(f"{toplam_harcama} TL")
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 5, harcama_item)

        baglanti.close()

    def aylikliste(self):
        self.ui.tblYeni.setColumnWidth(0, 0)
        self.ui.tblYeni.setColumnWidth(1, 60)
        self.ui.tblYeni.setColumnWidth(2, 70)
        self.ui.tblYeni.setColumnWidth(3, 70)
        self.ui.tblYeni.setColumnWidth(4, 60)
        self.ui.tblYeni.setColumnWidth(5, 150)
        self.ui.tblYeni.setColumnWidth(6, 150)
        self.ui.tblYeni.clear()
        self.ui.tblYeni.setRowCount(0)  # Tabloyu temizle
        self.ui.tblYeni.setHorizontalHeaderLabels(
            ("ID", "Tarih", "T.Market", "T.Fatura", "Diğer", "Açıklama", "AI Analiz"))

        # Bulunduğumuz ayın ilk ve son günlerini hesapla
        simdiki_ayin_ilk_gunu = QDate(QDate.currentDate().year(), QDate.currentDate().month(), 1)
        simdiki_ayin_son_gunu = QDate(QDate.currentDate().year(), QDate.currentDate().month(),
                                    QDate.currentDate().daysInMonth())

        # ayin_ilk_gunu ve ayin_son_gunu değişkenlerini str tipine dönüştür
        ayin_ilk_gunu = simdiki_ayin_ilk_gunu.toString("yyyy-MM-dd")
        ayin_son_gunu = simdiki_ayin_son_gunu.toString("yyyy-MM-dd")

        # Bulunduğumuz aya ait kayıtları veritabanından sorgula
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        sorgu = """
            SELECT 
                id,
                tarih, 
                market AS ToplamMarket,
                fatura AS ToplamFaturalar, 
                harcama AS ToplamDiğer,
                aciklama AS Aciklama,
                ai_analysis AS AIAnaliz
            FROM muhasebe 
            WHERE tarih BETWEEN ? AND ?
        """

        islem.execute(sorgu, (ayin_ilk_gunu, ayin_son_gunu))

        # Sonuçları tabloya ekle
        kayitlar = islem.fetchall()
        for satir in kayitlar:
            # Tarihi doğru formata dönüştür
            tarih_formatli = QDate.fromString(satir[1], "yyyy-MM-dd").toString("dd-MM-yyyy")

            # ID, Tarih, Toplam Market, Toplam Faturalar, Toplam Diğer ve Açıklama sütunlarını tabloya ekle
            self.ui.tblYeni.insertRow(self.ui.tblYeni.rowCount())
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 0, QTableWidgetItem(str(satir[0])))
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 1, QTableWidgetItem(tarih_formatli))

            if isinstance(satir[2], str) and satir[2][-2:] == "TL":
                market_item = QTableWidgetItem(satir[2])
            else:
                market_item = QTableWidgetItem(f"{str(satir[2])} TL")

            # Aynı işlemi fatura ve diğer öğeler için de tekrarlayın
            if isinstance(satir[3], str) and satir[3][-2:] == "TL":
                fatura_item = QTableWidgetItem(satir[3])
            else:
                fatura_item = QTableWidgetItem(f"{str(satir[3])} TL")

            if isinstance(satir[4], str) and satir[4][-2:] == "TL":
                diger_item = QTableWidgetItem(satir[4])
            else:
                diger_item = QTableWidgetItem(f"{str(satir[4])} TL")

            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 2, market_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 3, fatura_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 4, diger_item)

            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 5, QTableWidgetItem(satir[5]))
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 6, QTableWidgetItem(satir[6]))

        baglanti.close()

    def GelirKayit(self):
        try:
            # Veritabanı bağlantısı
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            # Tarih bilgisini al
            secili_tarih = self.ui.kayitTarih.selectedDate()
            if not secili_tarih.isValid():
                secili_tarih = QDate.currentDate()
            tarih = secili_tarih.toString("yyyy-MM-dd")

            # Form verilerini al
            kaynak = self.ui.cmbKaynak.currentText()
            miktar_text = self.ui.lneGelirMiktar.text().strip()
            aciklama = self.ui.lneGelirAciklama.text().strip()

            # Gerekli alan kontrolü
            if not kaynak or not miktar_text:
                QMessageBox.warning(self, "Hata", "Kaynak ve miktar alanları boş bırakılamaz!")
                return

            # Miktar değerini sayıya çevir
            try:
                miktar = float(miktar_text.replace(",", "."))
            except ValueError:
                QMessageBox.warning(self, "Hata", "Lütfen geçerli bir miktar giriniz!")
                return

            # Veritabanına kaydet
            kayit = "INSERT INTO gelirler (tarih, kaynak, miktar, aciklama) VALUES (?, ?, ?, ?)"
            islem.execute(kayit, (tarih, kaynak, miktar, aciklama))
            baglanti.commit()

            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", "Gelir kaydı başarıyla eklendi!")

            # Form alanlarını temizle
            self.ui.cmbKaynak.setCurrentIndex(-1)
            self.ui.lneGelirMiktar.clear()
            self.ui.lneGelirAciklama.clear()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Gelir kaydı eklenirken bir hata oluştu: {str(e)}")
        finally:
            baglanti.close()

    def kayit_yap(self):
        try:
            # Seçili tarihi al (eğer seçili değilse bugünün tarihini kullan)
            secili_tarih = self.ui.kayitTarih.selectedDate()
            if not secili_tarih.isValid():
                secili_tarih = QDate.currentDate()
            
            tarih = secili_tarih.toString("yyyy-MM-dd")
            
            # Diğer değerleri al
            market = self.ui.lneMarket.text().strip() if self.ui.lneMarket.text().strip() else "0"
            fatura = self.ui.lneFatura.text().strip() if self.ui.lneFatura.text().strip() else "0"
            harcama = self.ui.lneHarcama.text().strip() if self.ui.lneHarcama.text().strip() else "0"
            aciklama = self.ui.lneAciklama.text().strip()

            # Sayısal değerleri kontrol et
            try:
                market = float(market.replace(",", "."))
                fatura = float(fatura.replace(",", "."))
                harcama = float(harcama.replace(",", "."))
            except ValueError:
                QMessageBox.warning(self, "Hata", "Lütfen geçerli sayısal değerler girin!")
                return

            # Veritabanına kaydet
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()
            
            kayit_ekle = """INSERT INTO muhasebe 
                (tarih, market, fatura, harcama, aciklama) 
                VALUES (?, ?, ?, ?, ?)"""
                
            islem.execute(kayit_ekle, (tarih, market, fatura, harcama, aciklama))
            baglanti.commit()
            
            # Input alanlarını temizle
            self.ui.lneMarket.clear()
            self.ui.lneFatura.clear()
            self.ui.lneHarcama.clear()
            self.ui.lneAciklama.clear()
            
            # Başarılı mesajı göster
            QMessageBox.information(self, "Başarılı", "Kayıt başarıyla eklendi!")
            
            # Tabloyu güncelle
            self.aylikliste()

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt sırasında bir hata oluştu: {str(e)}")
        finally:
            baglanti.close()

    def kayitsil(self):
        selected_item = self.ui.tblYeni.currentItem()

        if not selected_item:
            return

        selected_row = selected_item.row()
        id_sil_str = self.ui.tblYeni.item(selected_row, 0).text()
        sorgu = "DELETE FROM muhasebe WHERE id = ?"

        try:
            id_sil = int(id_sil_str)
            onay = QMessageBox.question(self, "Onay", "Seçili kaydı silmek istediğinizden emin misiniz?",
                                      QMessageBox.Yes | QMessageBox.No)

            if onay == QMessageBox.No:
                return

            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            islem.execute(sorgu, (id_sil,))
            baglanti.commit()

            if islem.rowcount > 0:
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla silindi.")
            else:
                QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere sahip kayıt bulunamadı.")

        except ValueError:
            QMessageBox.warning(self, "Hata", "Geçersiz id değeri.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")
        finally:
            baglanti.close()
            self.aylikliste()

    def guncelle(self):
        selected_item = self.ui.tblYeni.currentItem()

        if selected_item is None:
            return

        selected_row = selected_item.row()

        try:
            baglanti = sqlite3.connect("data/veriler1.db")
            islem = baglanti.cursor()

            try:
                id_sutun_indeksi = 0
                market_sutun_indeksi = 2
                fatura_sutun_indeksi = 3
                harcama_sutun_indeksi = 4
                aciklama_sutun_indeksi = 5
                tarih_sutun_indeksi = 1

                id_guncelle = int(self.ui.tblYeni.item(selected_row, id_sutun_indeksi).text())
            except ValueError:
                print(f"Hata: Geçersiz ID değeri: '{self.ui.tblYeni.item(selected_row, id_sutun_indeksi).text()}'")
                QMessageBox.warning(self, "Hata", "Geçersiz ID değeri. ID bir tam sayı olmalıdır.")
                return

            market = self.ui.tblYeni.item(selected_row, market_sutun_indeksi).text()
            fatura = self.ui.tblYeni.item(selected_row, fatura_sutun_indeksi).text()
            harcama = self.ui.tblYeni.item(selected_row, harcama_sutun_indeksi).text()
            aciklama = self.ui.tblYeni.item(selected_row, aciklama_sutun_indeksi).text()
            tarih_text = self.ui.tblYeni.item(selected_row, tarih_sutun_indeksi).text()

            try:
                tarih = datetime.strptime(tarih_text, "%d-%m-%Y")
            except ValueError:
                print(f"Hata: Geçersiz tarih formatı: '{tarih_text}'")
                QMessageBox.warning(self, "Hata", "Geçersiz tarih formatı. Tarih 'dd-mm-yyyy' formatında olmalıdır.")
                return

            sorgu = "UPDATE muhasebe SET market = ?, fatura = ?, harcama = ?, aciklama = ?, tarih = ? WHERE id = ?"
            islem.execute(sorgu, (market, fatura, harcama, aciklama, tarih.strftime("%Y-%m-%d"), id_guncelle))

            baglanti.commit()

            if islem.rowcount > 0:
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla güncellendi.")
            else:
                QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere sahip kayıt bulunamadı.")

        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Hata oluştu: {str(e)}")

        finally:
            baglanti.close()
            self.aylikliste()

    def HepsiniGoster(self):
        self.ui.tblYeni.setColumnWidth(0, 0)
        self.ui.tblYeni.setColumnWidth(1, 60)
        self.ui.tblYeni.setColumnWidth(2, 70)
        self.ui.tblYeni.setColumnWidth(3, 70)
        self.ui.tblYeni.setColumnWidth(4, 60)
        self.ui.tblYeni.setColumnWidth(5, 150)
        self.ui.tblYeni.setColumnWidth(6, 150)
        self.ui.tblYeni.clear()
        self.ui.tblYeni.setRowCount(0)  # Tabloyu temizle
        self.ui.tblYeni.setHorizontalHeaderLabels(
            ("ID", "Tarih", "T.Market", "T.Fatura", "Diğer", "Açıklama", "AI Analiz"))

        # Tüm kayıtları veritabanından sorgula
        baglanti = sqlite3.connect("data/veriler1.db")
        islem = baglanti.cursor()

        sorgu = """
            SELECT 
                id,
                tarih, 
                market AS ToplamMarket,
                fatura AS ToplamFaturalar, 
                harcama AS ToplamDiğer,
                aciklama AS Aciklama,
                ai_analysis AS AIAnaliz
            FROM muhasebe 
            ORDER BY tarih ASC
        """

        islem.execute(sorgu)

        # Sonuçları tabloya ekle
        kayitlar = islem.fetchall()
        for satir in kayitlar:
            # Tarihi doğru formata dönüştür
            tarih_formatli = QDate.fromString(satir[1], "yyyy-MM-dd").toString("dd-MM-yyyy")

            # ID, Tarih, Toplam Market, Toplam Faturalar, Toplam Diğer ve Açıklama sütunlarını tabloya ekle
            self.ui.tblYeni.insertRow(self.ui.tblYeni.rowCount())
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 0, QTableWidgetItem(str(satir[0])))
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 1, QTableWidgetItem(tarih_formatli))

            if isinstance(satir[2], str) and satir[2][-2:] == "TL":
                market_item = QTableWidgetItem(satir[2])
            else:
                market_item = QTableWidgetItem(f"{str(satir[2])} TL")

            # Aynı işlemi fatura ve diğer öğeler için de tekrarlayın
            if isinstance(satir[3], str) and satir[3][-2:] == "TL":
                fatura_item = QTableWidgetItem(satir[3])
            else:
                fatura_item = QTableWidgetItem(f"{str(satir[3])} TL")

            if isinstance(satir[4], str) and satir[4][-2:] == "TL":
                diger_item = QTableWidgetItem(satir[4])
            else:
                diger_item = QTableWidgetItem(f"{str(satir[4])} TL")

            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 2, market_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 3, fatura_item)
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 4, diger_item)

            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 5, QTableWidgetItem(satir[5]))
            self.ui.tblYeni.setItem(self.ui.tblYeni.rowCount() - 1, 6, QTableWidgetItem(satir[6]))

        baglanti.close()

    def temizle_ve_donustur(self, deger_text):
        """Sayısal değerleri temizler ve float'a dönüştürür."""
        if not deger_text:
            return 0.0
        # Önce TL ve boşlukları temizle
        deger_text = deger_text.replace("TL", "").strip()
        if deger_text == "0.0" or deger_text == "0,0" or deger_text == "0":
            return 0.0
        try:
            # Eğer sadece sayı ve nokta varsa direkt dönüştür
            if all(c.isdigit() or c == '.' for c in deger_text):
                return float(deger_text)
            # Binlik ayracı ve virgül varsa
            deger_text = deger_text.replace(".", "")  # Binlik ayracını kaldır
            deger_text = deger_text.replace(",", ".")  # Virgülü noktaya çevir
            return float(deger_text)
        except ValueError as e:
            print(f"Dönüşüm hatası: {deger_text} -> {str(e)}")
            return 0.0