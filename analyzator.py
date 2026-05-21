from flask import Flask, render_template, request, redirect, url_for
import urllib.request
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB_NAME = "historie_akcii.db"

def inicializuj_databazi():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historie_hledani (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT NOT NULL,
            cena REAL,
            zmena REAL,
            mena TEXT,
            cas_dotazu TEXT
        )
    ''')
    conn.commit()
    conn.close()

def uloz_do_databaze(ticker, cena, zmena, mena):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    aktualni_cas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO historie_hledani (ticker, cena, zmena, mena, cas_dotazu)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticker, cena, zmena, mena, aktualni_cas))
    conn.commit()
    conn.close()

    def uloz_do_databaze(ticker, cena, zmena, mena):
    # 1. Uložení do SQL databáze (pro splnění zadání)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    aktualni_cas = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO historie_hledani (ticker, cena, zmena, mena, cas_dotazu)
        VALUES (?, ?, ?, ?, ?)
    ''', (ticker, cena, zmena, mena, aktualni_cas))
    conn.commit()
    
    # 2. Vytáhnutí kompletní historie pro Markdown soubor
    cursor.execute('SELECT cas_dotazu, ticker, cena, zmena, mena FROM historie_hledani ORDER BY id DESC')
    vsechny_radky = cursor.fetchall()
    conn.close()
    
    # 3. Zápis do souboru historie.md ve formátu GitHub tabulky
    with open("historie.md", "w", encoding="utf-8") as f:
        f.write("# 📊 Historie vyhledávání akcií\n\n")
        f.write("| Čas dotazu | Ticker | Cena | Změna |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for radek in vsechny_radky:
            cas, tk, c, zm, mn = radek
            smer = "📈" if zm >= 0 else "📉"
            f.write(f"| {cas} | **{tk}** | {c:.2f} {mn} | {zm:+.2f}% {smer} |\n")

def ziskej_historii():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, cena, zmena, mena, cas_dotazu FROM historie_hledani ORDER BY id DESC LIMIT 10')
    radky = cursor.fetchall()
    conn.close()
    return radky

def stahni_data_akcie(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            
        result = data.get('chart', {}).get('result')
        if not result or result[0] is None:
            return None

        meta = result[0].get('meta', {})
        cena = float(meta.get('regularMarketPrice', 0))
        predchozi_cl = float(meta.get('previousClose', 0))
        mena = meta.get('currency', 'USD')
        
        zmena = ((cena - predchozi_cl) / predchozi_cl) * 100 if predchozi_cl > 0 else 0.0
        
        return {"ticker": ticker, "cena": cena, "zmena": zmena, "mena": mena}
    except:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    vysledek = None
    chyba = None
    
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').upper().strip()
        if ticker:
            data = stahni_data_akcie(ticker)
            if data:
                vysledek = data
                uloz_do_databaze(data['ticker'], data['cena'], data['zmena'], data['mena'])
            else:
                chyba = f"Ticker '{ticker}' nebyl nalezen nebo selhalo spojení."
                
    historie = ziskej_historii()
    return render_template('index.html', vysledek=vysledek, chyba=chyba, historie=historie)

if __name__ == "__main__":
    inicializuj_databazi()
    # Spustí webový server na adrese http://127.0.0.1:5000
    app.run(debug=True)
