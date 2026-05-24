from flask import Flask, render_template, request, redirect, url_for, flash, session
import urllib.request
import json
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'pokus2_user_system_2026'
DB_NAME = "database/system_v3.db"

def inicializuj_databazi():
    if not os.path.exists("database"):
        os.makedirs("database")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uzivatele (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jmeno TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uzivatel_id INTEGER NOT NULL,
            ticker TEXT NOT NULL,
            nazev TEXT,
            cena REAL,
            zmena REAL,
            high REAL,
            low REAL,
            mena TEXT,
            cas_dotazu TEXT,
            FOREIGN KEY (uzivatel_id) REFERENCES uzivatele (id)
        )
    ''')
    conn.commit()
    conn.close()

def stahni_data(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
        meta = data['chart']['result'][0]['meta']
        return {
            "ticker": ticker,
            "nazev": meta.get('symbol', ticker),
            "cena": float(meta['regularMarketPrice']),
            "zmena": ((float(meta['regularMarketPrice']) - float(meta['previousClose'])) / float(meta['previousClose'])) * 100,
            "high": float(meta.get('regularMarketDayHigh', 0)),
            "low": float(meta.get('regularMarketDayLow', 0)),
            "mena": meta.get('currency', 'USD')
        }
    except: return None

def aktualizuj_export_markdown():
    """Automaticky vygeneruje soubor PREHLED_DATABAZE.md pro GitHub."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        query = '''
            SELECT u.jmeno, h.ticker, h.nazev, h.cena, h.zmena, h.cas_dotazu 
            FROM historie h 
            JOIN uzivatele u ON h.uzivatel_id = u.id 
            ORDER BY h.id DESC
        '''
        cursor.execute(query)
        vsechny_radky = cursor.fetchall()
        conn.close()

        with open("PREHLED_DATABAZE.md", "w", encoding="utf-8") as f:
            f.write("# 📋 Přehled databáze (Automatický export pro GitHub)\n\n")
            f.write(f"*Poslední aktualizace: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}*\n\n")
            if not vsechny_radky:
                f.write("Databáze je momentálně prázdná.\n")
            else:
                f.write("| Uživatel | Symbol | Název firmy | Cena | Změna | Čas dotazu |\n")
                f.write("| :--- | :--- | :--- | :--- | :--- | :--- |\n")
                for r in vsechny_radky:
                    f.write(f"| {r[0]} | **{r[1]}** | {r[2]} | {r[3]:.2f} | {r[4]:+.2f}% | {r[5]} |\n")
    except Exception as e:
        print(f"Chyba při exportu: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    vysledek = None
    if request.method == 'POST':
        ticker = request.form.get('ticker', '').upper().strip()
        if ticker:
            data = stahni_data(ticker)
            if data:
                vysledek = data
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO historie (uzivatel_id, ticker, nazev, cena, zmena, high, low, mena, cas_dotazu)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (session['user_id'], data['ticker'], data['nazev'], data['cena'], data['zmena'], data['high'], data['low'], data['mena'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit()
                conn.close()
                aktualizuj_export_markdown() # AUTOMATICKÁ AKTUALIZACE
                flash(f"Data pro {ticker} úspěšně načtena.", "success")
            else:
                flash(f"Chyba: Symbol {ticker} nebyl nalezen.", "error")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, nazev, cena, zmena, mena, cas_dotazu, id FROM historie WHERE uzivatel_id = ? ORDER BY id DESC LIMIT 8', (session['user_id'],))
    historie = cursor.fetchall()
    
    # Načtení všech uživatelů pro ukázku v postranním panelu (Sidebar)
    cursor.execute('SELECT jmeno FROM uzivatele ORDER BY id')
    vsichni_uzivatele = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('index.html', historie=historie, vysledek=vysledek, user_name=session['user_name'], vsichni_uzivatele=vsichni_uzivatele)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        jmeno = request.form.get('jmeno', '').strip()
        if jmeno:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute('INSERT OR IGNORE INTO uzivatele (jmeno) VALUES (?)', (jmeno,))
            cursor.execute('SELECT id FROM uzivatele WHERE jmeno = ?', (jmeno,))
            user = cursor.fetchone()
            conn.commit()
            conn.close()
            session['user_id'] = user[0]
            session['user_name'] = jmeno
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/force_reset')
def force_reset():
    """Tato cesta vynutí odhlášení a promazání session pro testování."""
    session.clear()
    return "Session vymazána. <a href='/login'>Klikni zde pro přihlášení</a>"

@app.route('/smazat/<int:id>')
def smazat(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM historie WHERE id = ? AND uzivatel_id = ?', (id, session['user_id']))
    conn.commit()
    conn.close()
    aktualizuj_export_markdown() # AKTUALIZACE PO SMAZÁNÍ
    flash("Záznam odstraněn.", "info")
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM historie WHERE uzivatel_id = ?', (session['user_id'],))
    conn.commit()
    conn.close()
    aktualizuj_export_markdown() # AKTUALIZACE PO VYMAZÁNÍ
    flash("Vaše historie byla vymazána.", "warning")
    return redirect(url_for('index'))

if __name__ == "__main__":
    inicializuj_databazi()
    app.run(debug=True, port=5001)
