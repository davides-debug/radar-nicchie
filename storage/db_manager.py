import sqlite3
import logging
from datetime import datetime
from typing import List, Tuple, Any

logger = logging.getLogger(__name__)

DB_PATH = "storage/niches.db"

def init_db():
    """Inizializza il database e crea la tabella se non esiste."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS niche_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                niche TEXT NOT NULL,
                date TEXT NOT NULL,
                signal_source TEXT NOT NULL,
                raw_value REAL,
                score REAL
            )
        ''')
        conn.commit()
        logger.info(f"Database inizializzato in {DB_PATH}")
    except Exception as e:
        logger.error(f"Errore durante l'inizializzazione del database: {e}")
    finally:
        if conn:
            conn.close()

def save_niche_data(niche: str, signal_source: str, raw_value: float, score: float):
    """Salva un singolo segnale per una nicchia."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
            INSERT INTO niche_signals (niche, date, signal_source, raw_value, score)
            VALUES (?, ?, ?, ?, ?)
        ''', (niche, date_str, signal_source, raw_value, score))
        conn.commit()
    except Exception as e:
        logger.error(f"Errore durante il salvataggio dei dati per {niche}: {e}")
    finally:
        if conn:
            conn.close()

def get_latest_niches(limit: int = 10) -> List[Tuple]:
    """Recupera le ultime nicchie con il punteggio più alto."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Calcoliamo la media degli score per nicchia nell'ultima esecuzione (stessa data approssimativa)
        cursor.execute('''
            SELECT niche, MAX(date) as last_date, AVG(score) as avg_score
            FROM niche_signals
            GROUP BY niche
            ORDER BY avg_score DESC
            LIMIT ?
        ''', (limit,))
        results = cursor.fetchall()
        return results
    except Exception as e:
        logger.error(f"Errore durante il recupero dei dati: {e}")
        return []
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()
