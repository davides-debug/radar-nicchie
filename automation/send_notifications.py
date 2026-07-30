import os
import requests
import yaml
import sqlite3
import logging
from typing import List, Dict
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def get_niches_above_threshold(threshold: float) -> List[Dict]:
    """Recupera le nicchie dell'ultima scansione sopra la soglia."""
    db_path = "storage/niches.db"
    if not os.path.exists(db_path):
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Prende l'ultima data
        cursor.execute("SELECT MAX(date) FROM niche_signals")
        latest_date = cursor.fetchone()[0]

        if not latest_date:
            return []

        cursor.execute('''
            SELECT niche, AVG(score) as avg_score
            FROM niche_signals
            WHERE date LIKE ?
            GROUP BY niche
            HAVING avg_score >= ?
            ORDER BY avg_score DESC
        ''', (latest_date[:10] + "%", threshold))

        results = [{"niche": row[0], "score": row[1]} for row in cursor.fetchall()]
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Errore nel recupero dati per notifiche: {e}")
        return []

def send_telegram_message(message: str):
    """Invia un messaggio tramite Telegram Bot API."""
    config = load_config()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    # Priorità a variabile d'ambiente, poi config.yaml
    chat_id = os.getenv("TELEGRAM_CHAT_ID") or config.get("telegram_chat_id")

    if not bot_token or not chat_id:
        logger.warning("Credenziali Telegram mancanti. Salto invio notifica.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code == 200:
            logger.info("Notifica Telegram inviata con successo.")
        else:
            logger.error(f"Errore invio Telegram ({response.status_code}): {response.text}")
    except Exception as e:
        logger.error(f"Errore durante l'invio della notifica Telegram: {e}")

def main():
    logging.basicConfig(level=logging.INFO)
    config = load_config()
    threshold = config.get("alert_threshold", 70)

    niches = get_niches_above_threshold(threshold)

    if not niches:
        logger.info("Nessuna nicchia sopra la soglia. Nessuna notifica inviata.")
        return

    message = "🚀 *Radar-Nicchie: Opportunità Rilevate!*\n\n"
    message += "Le seguenti nicchie hanno superato la soglia di score:\n\n"

    for n in niches:
        message += f"• *{n['niche']}*: {n['score']:.2f}\n"

    message += "\nControlla il report completo su GitHub!"

    send_telegram_message(message)

if __name__ == "__main__":
    main()
