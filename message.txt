# 📊 FinAnalyzer v2.0 — Dokumentace Informačního Systému

Tento soubor slouží jako kompletní podklad a technický průvodce k obhajobě školního projektu webové aplikace "FinAnalyzer" s napojením na relační SQL databázi.

## 🏛️ 1. Architektura a Datový Model (ER Diagram)

Aplikace využívá **relační databázový model** (SQLite) se dvěma hlavními entitami propojenými logickou vazbou typu **1:N** (*jedna ku mnoha*). Pro vnitřní potřeby správy automatického číslování klíčů systém využívá také skrytou systémovou tabulku `sqlite_sequence`.

### 📊 Logická struktura entit

#### 1. Tabulka: `uzivatele`
Ukládá identitu registrovaných uživatelů aplikace.
* **`id` (INTEGER, PK)**: Primární klíč. Unikátní identifikátor uživatele s vlastností `AUTOINCREMENT`.
* **`jmeno` (TEXT)**: Přihlašovací jméno uživatele. Má vlastnosti `UNIQUE NOT NULL`, což zajišťuje, že v systému nemohou existovat dva uživatelé se stejným jménem.

#### 2. Tabulka: `historie`
Ukládá podrobné záznamy o všech úspěšně vyhledaných akciích napříč celým systémem.
* **`id` (INTEGER, PK)**: Primární klíč záznamu vyhledávání s vlastností `AUTOINCREMENT`.
* **`uzivatel_id` (INTEGER, FK)**: Cizí klíč (*Foreign Key*), který odkazuje na konkrétní `id` v tabulce `uzivatele`. Zajišťuje relační integritu systému.
* **`ticker` (TEXT)**: Textová burzovní zkratka akcie, např. *AAPL*, *NVDA*, *TSLA*.
* **`nazev` (TEXT)**: Kompletní oficiální název společnosti stažený z API (např. *Apple Inc.*).
* **`cena` (REAL)**: Aktuální tržní cena akcie (uloženo jako desetinné číslo).
* **`zmena` (REAL)**: Denní procentuální změna hodnoty (uloženo jako desetinné číslo).
* **`high` (REAL)**: Nejvyšší dosažená cena akcie během aktuálního obchodního dne.
* **`low` (REAL)**: Nejnižší dosažená cena akcie během aktuálního obchodního dne.
* **`mena` (TEXT)**: Třípísmenný kód měny, ve které je akcie obchodována (např. *USD*, *EUR*).
* **`cas_dotazu` (TEXT)**: Časové razítko pořízení záznamu ve formátu `YYYY-MM-DD HH:MM:SS`.

#### 3. Pomocná tabulka: `sqlite_sequence`
Systémová tabulka spravovaná samotným SQLite engine. Hlídá stav interních čítačů pro tabulky využívající `AUTOINCREMENT`.
* **`name` (TEXT)**: Název sledované tabulky (obsahuje hodnoty `"uzivatele"` a `"historie"`).
* **`seq` (INTEGER)**: Poslední přiřazená hodnota primárního klíče.

---

## 🔗 2. Definice Databázových Vztahů a Typů

### Kardinalita Vazby (1:N)
Vazba mezi tabulkou `uzivatele` a `historie` je definována vztahem **1:N** (Jeden ku Mnoha) pomocí klauzule `FOREIGN KEY (uzivatel_id) REFERENCES uzivatele(id)`.
* **Interpretace vztahu:** **Jeden** uživatel může v systému vygenerovat libovolné množství (**N**) dotazů a záznamů v historii vyhledávání. Naopak **jeden konkrétní záznam** v historii patří vždy právě **jednomu** přihlášenému uživateli.

### Použité datové typy v SQLite
Při návrhu databáze a ER diagramu je nutné striktně používat nativní datové typy SQLite:
* **`TEXT`**: Využívá se místo programátorského typu `string` pro textová jména, tickery i formátovaná časová razítka.
* **`REAL`**: Využívá se místo typu `float` pro reálná desetinná čísla, což je ideální pro ceny akcií, denní rozsahy a procentuální změny.
* **`INTEGER`**: Celočíselný typ pro primární a cizí klíče.
* **Absence typu `DATETIME`**: SQLite nativně nemá samostatný datový typ pro datum a čas. Proto se pole `cas_dotazu` definuje jako `TEXT`. Formát textu generovaný backendem umožňuje řazení a běžné vyhodnocování.

---

## 🎯 3. Tahák k Obhajobě (Očekávané otázky zkoušejícího)

Přehled otázek, na které se učitelé u obhajob nejčastěji ptají, spolu s připravenými technickými odpověďmi:

### 💬 Otázka 1: „Jak máte vyřešenou relační strukturu a propojování tabulek?“
**Odpověď:** „Náš informační systém plně staví na relačním principu. Máme oddělenou entitu `uzivatele` a entitu `historie`. Vazbu zajišťuje cizí klíč `uzivatel_id` v tabulce `historie`, který referencuje primární klíč `id` v tabulce `uzivatele`. Jedná se o relaci 1:N. V databázi je tato integrita striktně vynucena pomocí omezení `FOREIGN KEY`.“

### 💬 Otázka 2: „Kde přesně berete hodnotu pro sloupec 'nazev' a jaký má význam?“
**Odpověď:** „Když uživatel odešle burzovní symbol, backend v Pythonu kontaktuje API Yahoo Finance. Získaná data obsahují oficiální název společnosti. Tento název ukládáme do sloupce `nazev` jako typ `TEXT`. Zvyšuje to uživatelskou hodnotu systému — uživatel v historii i na dashboardu ihned vidí srozumitelný název firmy (např. *Apple Inc.*), nejen zkratku *AAPL*.“

### 💬 Otázka 3: „Proč máte v historii typy jako REAL a TEXT a ne float nebo datetime?“
**Odpověď:** „ER diagram i definice v kódu reflektují vnitřní specifikaci databázového stroje SQLite. SQLite nepodporuje datové typy `float` nebo `datetime`. Typ `REAL` odpovídá typu s plovoucí desetinnou čárkou a slouží pro ceny akcií. Datum a čas ukládáme jako formátovaný `TEXT` ve standardu ISO, se kterým umí databáze spolehlivě provádět řazení pomocí `ORDER BY`.“

### 💬 Otázka 4: „K čemu je v diagramu tabulka sqlite_sequence, když ji nemáte v kódu?“
**Odpověď:** „Tabulka `sqlite_sequence` je interní systémová tabulka, kterou si SQLite vytváří automaticky na pozadí, jakmile v databázi definujeme tabulku s vlastností `AUTOINCREMENT`. Slouží k ukládání nejvyššího dosaženého ID pro dané tabulky. V diagramu ji uvádíme pro úplnost, aby bylo zřejmé, že rozumíme vnitřní struktuře použitého databázového stroje.“

### 💬 Otázka 5: „Jakým způsobem zajišťujete, že uživatel vidí pouze svou historii?“
**Odpověď:** „Při přihlášení uživatele si aplikace uloží jeho vygenerované `user_id` do zabezpečené serverové `session`. SQL dotaz pro vykreslení historie na dashboardu obsahuje omezující klauzuli: `WHERE uzivatel_id = ?`. Tím je přímo na úrovni databáze zajištěna personalizace, izolace dat a multi-user přístup.“