# 📡 Radar-Nicchie

Radar-Nicchie è un sistema automatizzato per monitorare la domanda e individuare nicchie di mercato potenzialmente redditizie. Il sistema analizza dati da Google Trends, Reddit e Udemy per calcolare un "Opportunity Score".

## 🚀 Setup

### Requisiti
- Python 3.11+ (richiesto da `pandas`, dipendenza indiretta di `pytrends`;
  versioni precedenti falliscono l'installazione delle dipendenze)
- Chiavi API per Reddit (PRAW) e Udemy (Affiliate API) — **opzionali**, vedi
  limitazioni note qui sotto

### Installazione Locale
1. Clona il repository.
2. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```
3. Configura le variabili d'ambiente: copia `.env.example` in `.env` e
   compila i valori.
   ```bash
   cp .env.example .env
   ```
   Il file `.env` viene caricato automaticamente da `main.py` (tramite
   `python-dotenv`), quindi non servono comandi `export`/`set` manuali né
   differenze tra Windows, macOS e Linux. Le chiavi richieste sono:
   - `REDDIT_CLIENT_ID` / `REDDIT_CLIENT_SECRET` (necessarie per i dati Reddit)
   - `UDEMY_CLIENT_ID` / `UDEMY_CLIENT_SECRET` (necessarie per i dati Udemy)
   - `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` (opzionali, per le notifiche)

   Se una fonte non ha credenziali configurate, la pipeline non si
   interrompe: registra un errore nei log e prosegue con le altre fonti.
4. Esegui la pipeline:
   ```bash
   python main.py
   ```
   Il comando calcola gli score, aggiorna `storage/niches.db` e genera in
   automatico sia il report (`report/latest_report.md`) sia la dashboard
   (`report/dashboard.html`).

## ⚙️ Configurazione

Tutta la configurazione avviene tramite il file `config.yaml`:
- `keywords`: Lista di termini da monitorare su Google Trends e Reddit.
- `subreddits`: Community Reddit da analizzare.
- `udemy_topics`: Argomenti per tracciare la competizione su Udemy.
- `scoring_weights`: Pesi per il calcolo dello score finale.

## 📊 Interpretazione dello Score

L'**Opportunity Score (0-100)** è una media pesata di quattro fattori. I pesi
di default in `config.yaml` sono:
1. **Google Trends (30%)**: Analizza la pendenza del trend e la presenza di query "breakout".
2. **Reddit Engagement (10%)**: Misura il volume di discussioni e l'interesse attivo della community. Peso ridotto di default perché Reddit non rilascia più chiavi API gratuite a nuovi sviluppatori senza approvazione (vedi sotto) — se hai le credenziali, puoi alzarlo di nuovo.
3. **Udemy Market (25%)**: Valuta il rapporto tra domanda esistente e densità della competizione su Udemy.
4. **Manual Market (35%)**: Include dati inseriti manualmente per Gumroad e Amazon KDP — è la fonte più affidabile perché interamente sotto il tuo controllo.

## 🤖 Automazione (GitHub Actions)

Il sistema è configurato per girare ogni lunedì mattina tramite GitHub Actions.
Per configurarlo:
1. Vai in `Settings > Secrets and variables > Actions` nel tuo repository GitHub.
2. Aggiungi i seguenti Secret:
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
   - `UDEMY_CLIENT_ID`
   - `UDEMY_CLIENT_SECRET`

Il workflow aggiornerà automaticamente `storage/niches.db`, genererà una dashboard interattiva in `report/dashboard.html` e aprirà una **Issue** con il report settimanale.

## ⚠️ Limitazione nota: Google Trends

Google non offre una API ufficiale gratuita per Google Trends. La libreria
`pytrends` simula il traffico del sito e Google può rispondere con errori
429 (rate-limit) in modo imprevedibile, indipendentemente dal volume di
richieste. La pipeline gestisce il caso con retry automatici a backoff
esponenziale (`sources/google_trends.py`), ma se il rate-limit persiste la
keyword riceverà uno score parziale (basato solo su Reddit/Udemy/dati
manuali) invece di far fallire l'intera esecuzione. Se noti 429 frequenti,
riduci il numero di keyword monitorate in `config.yaml` o esegui la
pipeline meno spesso.

## ⚠️ Limitazione nota: accesso API Reddit

Dal 2025/2026 Reddit **non rilascia più nuove chiavi API gratuite in modo
self-service**: la vecchia pagina `reddit.com/prefs/apps` ora richiede di
accettare la "Responsible Builder Policy" e, per i nuovi sviluppatori,
un'approvazione tramite il Reddit Developer Platform prima di poter creare
un'app e ottenere `client_id`/`client_secret`. Se non riesci ad attivare
questa fonte:
- il software **funziona comunque**: la pipeline non si interrompe, la
  fonte Reddit contribuisce semplicemente 0 al punteggio;
- il peso di default di `reddit_engagement` in `config.yaml` è stato
  abbassato (10%) proprio per non penalizzare chi parte senza queste
  credenziali;
- se disponi già di credenziali Reddit da un progetto precedente, puoi
  comunque usarle e alzare di nuovo il peso nello scoring.

## 📲 Notifiche Telegram (opzionale)

Se configuri `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` nel file `.env`,
puoi inviare un riepilogo delle nicchie sopra soglia direttamente su
Telegram:
```bash
python -m automation.send_notifications
```
Questo script è già incluso nel workflow settimanale, ma può anche essere
eseguito manualmente in qualsiasi momento dopo `python main.py`.

## 📈 Dashboard Interattiva

Oltre ai report testuali, il sistema genera una dashboard HTML interattiva che mostra l'andamento storico dell'Opportunity Score per tutte le nicchie monitorate.
- **File**: `report/dashboard.html`
- **Come visualizzarla**: Scarica il file e aprilo in qualsiasi browser per interagire con i grafici.

## 🛒 Marketplace Manuali (Gumroad/KDP)

Per evitare violazioni dei ToS (niente scraping automatico), i dati di Gumroad e Amazon KDP vengono inseriti tramite un modulo "assistito".
Per registrare nuovi dati:
```bash
python sources/manual_marketplaces.py "nome nicchia" "Gumroad" 150
```
Il valore (es. 150) rappresenta una metrica di domanda (es. numero di prodotti top o revenue stimata). Questi dati verranno inclusi automaticamente nella prossima esecuzione della pipeline.

## 🎨 Etsy API

L'integrazione di Etsy è pronta a livello di ricerca. Per attivarla:
1. Registra un'app su [Etsy Developers](https://www.etsy.com/developers).
2. Segui le istruzioni in `sources/etsy_info.md`.

## 🛠 Aggiungere una Nuova Fonte Dati

1. Crea un nuovo script in `sources/nome_fonte.py`.
2. Implementa una funzione che restituisca un dizionario di metriche.
3. Aggiorna `scoring/opportunity_score.py` per includere la nuova fonte nel calcolo.
4. Integra la chiamata in `main.py`.

## 📄 Licenza

Distribuito con licenza commerciale, vedi [LICENSE.md](LICENSE.md).
