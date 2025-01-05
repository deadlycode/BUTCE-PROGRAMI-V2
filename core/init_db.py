import sqlite3
import os

def init_database():
    # data klasörünü oluştur
    if not os.path.exists('data'):
        os.makedirs('data')

    # veriler1.db için tablolar
    conn = sqlite3.connect('data/veriler1.db')
    cursor = conn.cursor()

    # muhasebe tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS muhasebe(
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        tarih datetime, 
        market REAL, 
        fatura REAL, 
        harcama REAL, 
        aciklama text
    )""")

    # gelirler tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gelirler(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih datetime,
        kaynak text,
        miktar REAL,
        aciklama text
    )""")

    # hesaplar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hesaplar(
        hesap_id INTEGER PRIMARY KEY,
        hesap_turu TEXT,
        email TEXT,
        sifre TEXT,
        aciklama TEXT,
        renk TEXT
    )""")

    # hesap_turleri tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hesap_turleri(
        tur_id INTEGER PRIMARY KEY,
        tur_adi TEXT UNIQUE
    )""")

    conn.commit()
    conn.close()

    # notlar.db için tablolar
    conn = sqlite3.connect('data/notlar.db')
    cursor = conn.cursor()

    # notlar tablosu
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notlar(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih datetime,
        not1 text,
        not2 text,
        not3 text
    )""")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_database()
