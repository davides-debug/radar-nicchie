import csv
import os
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

MANUAL_DATA_FILE = "storage/manual_market_data.csv"

def init_manual_storage():
    """Inizializza il file CSV per i dati manuali se non esiste."""
    if not os.path.exists(MANUAL_DATA_FILE):
        os.makedirs(os.path.dirname(MANUAL_DATA_FILE), exist_ok=True)
        with open(MANUAL_DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'niche', 'source', 'value', 'notes'])
        logger.info(f"File dati manuali creato: {MANUAL_DATA_FILE}")

def record_manual_observation(niche: str, source: str, value: float, notes: str = ""):
    """Registra una singola osservazione manuale (es. da Gumroad o KDP)."""
    init_manual_storage()
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        with open(MANUAL_DATA_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date_str, niche, source, value, notes])
        logger.info(f"Osservazione registrata per {niche} su {source}: {value}")
    except Exception as e:
        logger.error(f"Errore durante la registrazione manuale: {e}")

def get_latest_manual_data() -> Dict[str, Dict[str, float]]:
    """
    Legge gli ultimi dati manuali per ogni nicchia e fonte.
    Restituisce un dizionario: {niche: {source: value}}
    """
    if not os.path.exists(MANUAL_DATA_FILE):
        return {}

    results = {}
    try:
        with open(MANUAL_DATA_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Leggiamo tutto e teniamo solo l'ultima voce per coppia (niche, source)
            for row in reader:
                niche = row['niche']
                source = row['source']
                try:
                    value = float(row['value'])
                except ValueError:
                    continue

                if niche not in results:
                    results[niche] = {}
                results[niche][source] = value
    except Exception as e:
        logger.error(f"Errore nella lettura dei dati manuali: {e}")

    return results

if __name__ == "__main__":
    # Esempio di utilizzo via CLI
    import sys
    if len(sys.argv) > 3:
        # python sources/manual_marketplaces.py "personal finance" "Gumroad" 150
        niche = sys.argv[1]
        source = sys.argv[2]
        value = float(sys.argv[3])
        record_manual_observation(niche, source, value)
    else:
        print("Uso: python sources/manual_marketplaces.py <nicchia> <fonte> <valore>")
