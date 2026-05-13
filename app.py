from flask import Flask, render_template, request, redirect, session, Response
import sqlite3
from veritabani import veritabani_olustur

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

veritabani_olustur()


def fraud_kontrol(musteri_adi, tutar, kanal, odeme_onayli, erisim_tipi):
    risk_skoru = 0
    nedenler = []

    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    # Temel kurallar
    if odeme_onayli == "Hayır":
        risk_skoru += 50
        nedenler.append("Ödeme doğrulanmadı")

    if erisim_tipi == "Bypass":
        risk_skoru += 60
        nedenler.append("Bypass erişim girişimi")

    if erisim_tipi == "Şüpheli":
        risk_skoru += 25
        nedenler.append("Şüpheli erişim tipi")

    if tutar >= 10000:
        risk_skoru += 30
        nedenler.append("Yüksek tutarlı işlem")

    if kanal == "Nakit" and tutar >= 5000:
        risk_skoru += 20
        nedenler.append("Nakit kanalda yüksek tutar")

    if kanal == "Mobil Para":
        risk_skoru += 10
        nedenler.append("Mobil para kanalı ek kontrol gerektirir")

    # AI benzeri davranış analizi - aynı müşteri kaç işlem yapmış?
    cursor.execute("""
        SELECT COUNT(*) FROM islemler
        WHERE musteri_adi = ?
    """, (musteri_adi,))
    onceki_islem = cursor.fetchone()[0]

    if onceki_islem >= 2:
        risk_skoru += 25
        nedenler.append("Davranış analizi: müşteri kısa sürede çok işlem yaptı")

    # AI benzeri davranış analizi - müşterinin geçmişte riskli işlemi var mı?
    cursor.execute("""
        SELECT COUNT(*) FROM islemler
        WHERE musteri_adi = ?
        AND (durum='Şüpheli' OR durum='Engellendi')
    """, (musteri_adi,))
    supheli_gecmis = cursor.fetchone()[0]

    if supheli_gecmis >= 1:
        risk_skoru += 20
        nedenler.append("Davranış analizi: müşterinin geçmişte riskli işlemi var")

    # AI benzeri davranış analizi - aynı kanal çok yoğun kullanılmış mı?
    cursor.execute("""
        SELECT COUNT(*) FROM islemler
        WHERE kanal = ?
    """, (kanal,))
    kanal_kullanim = cursor.fetchone()[0]

    if kanal_kullanim >= 5:
        risk_skoru += 15
        nedenler.append("Davranış analizi: ödeme kanalı yoğun kullanılıyor")

    conn.close()

    # Risk seviyesini belirleme
    if risk_skoru >= 80:
        durum = "Engellendi"
        risk_seviyesi = "Yüksek"
    elif risk_skoru >= 40:
        durum = "Şüpheli"
        risk_seviyesi = "Orta"
    else:
        durum = "Normal"
        risk_seviyesi = "Düşük"

    if not nedenler:
        aciklama = "İşlem normal olarak değerlendirildi."
    else:
        aciklama = ", ".join(nedenler)

    return durum, risk_seviyesi, risk_skoru, aciklama


@app.route("/", methods=["GET", "POST"])
def giris():
    hata = None

    if request.method == "POST":
        kullanici_adi = request.form["kullanici_adi"]
        sifre = request.form["sifre"]

        conn = sqlite3.connect("dolandiricilik.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM kullanicilar WHERE kullanici_adi=? AND sifre=?",
            (kullanici_adi, sifre)
        )
        kullanici = cursor.fetchone()
        conn.close()

        if kullanici:
            session["kullanici"] = kullanici_adi
            session["rol"] = kullanici[3]
            return redirect("/panel")
        else:
            hata = "Kullanıcı adı veya şifre hatalı!"

    return render_template("giris.html", hata=hata)


@app.route("/panel")
def panel():
    if "kullanici" not in session:
        return redirect("/")

    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM islemler")
    toplam = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM islemler WHERE durum='Normal'")
    normal = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM islemler WHERE durum='Şüpheli'")
    supheli = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM islemler WHERE durum='Engellendi'")
    engellendi = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM alarmlar")
    alarm_sayisi = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(risk_skoru) FROM islemler")
    toplam_risk = cursor.fetchone()[0]

    if toplam_risk is None:
        toplam_risk = 0

    conn.close()

    return render_template(
        "panel.html",
        toplam=toplam,
        normal=normal,
        supheli=supheli,
        engellendi=engellendi,
        alarm_sayisi=alarm_sayisi,
        toplam_risk=toplam_risk
    )


@app.route("/islem-ekle", methods=["GET", "POST"])
def islem_ekle():
    if "kullanici" not in session:
        return redirect("/")

    if session["rol"] != "Admin":
        return redirect("/panel")

    if request.method == "POST":
        musteri_adi = request.form["musteri_adi"]
        tutar = float(request.form["tutar"])
        kanal = request.form["kanal"]
        odeme_onayli = request.form["odeme_onayli"]
        erisim_tipi = request.form["erisim_tipi"]

        durum, risk_seviyesi, risk_skoru, aciklama = fraud_kontrol(
            musteri_adi,
            tutar,
            kanal,
            odeme_onayli,
            erisim_tipi
        )

        conn = sqlite3.connect("dolandiricilik.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO islemler
            (musteri_adi, tutar, kanal, odeme_onayli, erisim_tipi, durum, risk_seviyesi, risk_skoru, aciklama)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            musteri_adi,
            tutar,
            kanal,
            odeme_onayli,
            erisim_tipi,
            durum,
            risk_seviyesi,
            risk_skoru,
            aciklama
        ))

        islem_id = cursor.lastrowid

        if risk_skoru >= 40:
            cursor.execute("""
                INSERT INTO alarmlar
                (islem_id, alarm_mesaji, risk_skoru)
                VALUES (?, ?, ?)
            """, (islem_id, aciklama, risk_skoru))

        conn.commit()
        conn.close()

        return redirect("/islemler")

    return render_template("islem_ekle.html")


@app.route("/islemler")
def islemler():
    if "kullanici" not in session:
        return redirect("/")

    durum_filtre = request.args.get("durum")

    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    if durum_filtre and durum_filtre != "Tümü":
        cursor.execute(
            "SELECT * FROM islemler WHERE durum=? ORDER BY id DESC",
            (durum_filtre,)
        )
    else:
        cursor.execute("SELECT * FROM islemler ORDER BY id DESC")

    islemler = cursor.fetchall()
    conn.close()

    return render_template(
        "islemler.html",
        islemler=islemler,
        secili_durum=durum_filtre
    )


@app.route("/alarm-kayitlari")
def alarm_kayitlari():
    if "kullanici" not in session:
        return redirect("/")

    if session["rol"] != "Admin":
        return redirect("/panel")

    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT alarmlar.id, alarmlar.islem_id, alarmlar.alarm_mesaji,
               alarmlar.risk_skoru, alarmlar.tarih,
               islemler.musteri_adi, islemler.durum
        FROM alarmlar
        INNER JOIN islemler ON alarmlar.islem_id = islemler.id
        ORDER BY alarmlar.id DESC
    """)

    alarmlar = cursor.fetchall()
    conn.close()

    return render_template("alarm_kayitlari.html", alarmlar=alarmlar)


@app.route("/rapor-indir")
def rapor_indir():
    if "kullanici" not in session:
        return redirect("/")

    if session["rol"] != "Admin":
        return redirect("/panel")

    conn = sqlite3.connect("dolandiricilik.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM islemler")
    veriler = cursor.fetchall()

    conn.close()

    output = "\ufeff"

    basliklar = [
        "ID",
        "Müşteri",
        "Tutar",
        "Kanal",
        "Ödeme",
        "Erişim",
        "Durum",
        "Risk Seviyesi",
        "Risk Skoru",
        "Açıklama",
        "Tarih"
    ]

    output += ";".join(basliklar) + "\n"

    for satir in veriler:
        satir = [str(veri).replace(";", ",") for veri in satir]
        output += ";".join(satir) + "\n"

    return Response(
        output,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=islem_raporu.csv"
        }
    )


@app.route("/cikis")
def cikis():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)