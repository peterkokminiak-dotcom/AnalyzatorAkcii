# 📊 Pokus 2: Relační systém s uživateli

Tato verze projektu obsahuje pokročilou databázovou strukturu se dvěma propojenými tabulkami a systémem přihlašování.

## 1. ER Diagram (Vztah 1:N)

```mermaid
erDiagram
    UZIVATELE ||--o{ HISTORIE : "vytváří"
    UZIVATELE {
        int id PK "Primární klíč"
        string jmeno "Unikátní jméno uživatele"
    }
    HISTORIE {
        int id PK "Primární klíč"
        int uzivatel_id FK "Cizí klíč (odkaz na uživatele)"
        string ticker "Symbol akcie"
        string nazev "Název firmy"
        float cena "Tržní cena"
        float zmena "Změna v %"
        string mena "Měna"
        datetime cas_dotazu "Čas uložení"
    }
```

## 2. Funkcionalita
- **Systém uživatelů:** Každý uživatel má své vlastní konto.
- **Relace:** Tabulka `historie` je propojena s tabulkou `uzivatele` pomocí cizího klíče `uzivatel_id`.
- **Personalizace:** Uživatel vidí pouze svou historii hledání.
- **Automatická registrace:** Pokud jméno v databázi neexistuje, systém jej při prvním přihlášení vytvoří.

## 3. Jak spustit
1. Jdi do složky `pokus2`.
2. Spusť `python analyzator.py`.
3. Otevři `http://127.0.0.1:5001`.
