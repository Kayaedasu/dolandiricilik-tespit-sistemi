AI Destekli Dolandırıcılık Tespit Sistemi
Kullanıcı El Kitapçığı (User Manual)
1. Proje Amacı

Bu sistem finansal işlemler üzerinde risk analizi yaparak şüpheli işlemleri tespit etmek, alarm üretmek ve yöneticilere raporlama sağlamayı amaçlamaktadır.

2. Sistem Gereksinimleri
Yazılım
Python 3.11+
Flask
SQLite
Web Tarayıcı
Kurulum

Terminal:

pip install flask

Çalıştırma:

python app.py
3. Giriş Sistemi

Sistem iki rol içerir.

Admin

Yetkiler:

İşlem ekleme
Alarm kayıtları görüntüleme
CSV rapor indirme

Örnek:

Kullanıcı: admin
Şifre: 1234
Denetçi

Yetkiler:

İşlemleri görüntüleme

Örnek:

Kullanıcı: denetci
Şifre: 1234
4. Yeni İşlem Oluşturma

Panel:

Yeni İşlem Ekle

Alanlar:

Müşteri Adı
İşlem Tutarı
Ödeme Kanalı
Ödeme Onayı
Sistem Erişim Durumu
5. Risk Analizi

Sistem otomatik analiz yapar.

Kontroller:

Ödeme doğrulandı mı
Yetkisiz erişim var mı
Yüksek tutar var mı
Kanal yoğunluğu
Geçmiş işlem davranışı
6. Alarm Sistemi

Risk yüksekse:

Alarm oluşturulur

Alarm panelinde görüntülenir.

7. Dashboard

Gösterilen bilgiler:

Toplam İşlem
Normal İşlem
Şüpheli İşlem
Engellenen İşlem
Toplam Risk Skoru
8. CSV Raporlama

Admin:

CSV Rapor İndir

ile rapor alabilir.

9. Çıkış
Çıkış Yap

ile oturum kapatılır.

Hazırlayan
Halil Oğuz Çetin
Edasu Kaya
Abdullah Durgun
Berat Demirel
Mustafa Yaşar Eroğlu