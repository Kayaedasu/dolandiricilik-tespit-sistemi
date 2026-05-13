import sqlite3

def veritabani_olustur():
    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS kullanicilar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kullanici_adi TEXT NOT NULL,
        sifre TEXT NOT NULL,
        rol TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS islemler (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        musteri_adi TEXT NOT NULL,
        tutar REAL NOT NULL,
        kanal TEXT NOT NULL,
        odeme_onayli TEXT NOT NULL,
        erisim_tipi TEXT NOT NULL,
        durum TEXT NOT NULL,
        risk_seviyesi TEXT NOT NULL,
        risk_skoru INTEGER NOT NULL,
        aciklama TEXT NOT NULL,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS alarmlar (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        islem_id INTEGER,
        alarm_mesaji TEXT NOT NULL,
        risk_skoru INTEGER NOT NULL,
        tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi='admin'")
    admin = cursor.fetchone()

    if admin is None:
        cursor.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (?, ?, ?)",
            ("admin", "1234", "Admin")
        )

    cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi='denetci'")
    denetci = cursor.fetchone()

    if denetci is None:
        cursor.execute(
            "INSERT INTO kullanicilar (kullanici_adi, sifre, rol) VALUES (?, ?, ?)",
            ("denetci", "1234", "Denetçi")
        )

    conn.commit()
    conn.close()