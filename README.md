Tabii, Türkçe bir README hazırlayalım. İşte önerdiğim Türkçe README içeriği:

💰 PUBLIC BUTCE - Kişisel Bütçe Yönetim Sistemi
PythonPyQt5License

📝 Açıklama
PUBLIC BUTCE, Python ve PyQt5 kullanılarak geliştirilmiş kapsamlı bir kişisel bütçe yönetim sistemidir. Kullanıcı dostu arayüzü ile gelir-giderlerinizi takip etmenize ve finansal hedeflerinizi yönetmenize yardımcı olur.

✨ Temel Özellikler
📊 Gelir ve gider takibi
💳 Çoklu hesap yönetimi
📝 Hızlı not alma özelliği
📈 Bütçe planlama ve izleme
🔔 Sessiz bildirim sistemi
🌙 Koyu tema arayüzü
🗄️ Güvenilir veri depolama için SQLite veritabanı


🚀 Kurulum
Ön Gereksinimler
Python 3.8 veya üzeri
Git (depoyu klonlamak için)
Kurulum Adımları
Depoyu klonlayın
Code
CopyInsert
git clone https://github.com/kullaniciadi/PUBLIC-BUTCE.git
cd PUBLIC-BUTCE

Sanal ortam oluşturun (önerilen)
Code
CopyInsert
python -m venv venv
# Windows için
venv\Scripts\activate
# Linux/Mac için
source venv/bin/activate

Bağımlılıkları yükleyin
Code
CopyInsert
pip install -r requirements.txt
Veritabanını başlatın
Code
CopyInsert
python core/init_db.py

Uygulamayı çalıştırın
Code
CopyInsert
python main.pyw

🗂️ Proje Yapısı
Code
CopyInsert
PUBLIC BUTCE/
├── core/                   # Temel mantık ve arka uç
├── gui/                    # Kullanıcı arayüzü bileşenleri
├── data/                   # Veritabanı dosyaları
├── main.pyw               # Ana uygulama başlangıç noktası
└── requirements.txt       # Bağımlılıklar
💻 Sistem Gereksinimleri
İşletim Sistemi: Windows, Linux veya macOS
RAM: Minimum 2GB (4GB önerilen)
Depolama: 100MB boş alan
Python 3.8 veya üzeri
🔧 Bağımlılıklar
PyQt5 >= 5.15.9
pandas >= 2.1.0
numpy >= 1.24.0
Diğer bağımlılıklar requirements.txt dosyasında listelenmiştir


🤝 Katkıda Bulunma
Katkılarınızı bekliyoruz! Lütfen Pull Request göndermekten çekinmeyin.

Projeyi forklayın
Özellik dalınızı oluşturun (git checkout -b özellik/HarikaBirÖzellik)
Değişikliklerinizi commit edin (git commit -m 'Harika bir özellik eklendi')
Dalınıza push yapın (git push origin özellik/HarikaBirÖzellik)
Bir Pull Request açın


📝 Lisans
Bu proje MIT Lisansı altında lisanslanmıştır - detaylar için LICENSE dosyasına bakın.

📞 Destek
Herhangi bir sorunla karşılaşırsanız veya sorularınız varsa:

poetwhitecloud@gmail.com
