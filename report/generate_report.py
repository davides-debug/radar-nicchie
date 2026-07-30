import sqlite3
import logging
import yaml
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

logger = logging.getLogger(__name__)
DB_PATH = "storage/niches.db"

def load_config():
    try:
        with open("config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except:
        return {}

def generate_markdown_report(only_above_threshold: bool = False) -> Optional[str]:
    """Genera un report Markdown con le top 10 nicchie."""
    if not os.path.exists(DB_PATH):
        logger.error("Database non trovato. Impossibile generare il report.")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Recupera la data più recente e quella di una settimana fa circa
        cursor.execute("SELECT MAX(date) FROM niche_signals")
        latest_date = cursor.fetchone()[0]

        if not latest_date:
            logger.error("Nessun dato presente nel database. Esegui prima main.py.")
            return None

        one_week_ago = (datetime.strptime(latest_date, "%Y-%m-%d %H:%M:%S") - timedelta(days=6)).strftime("%Y-%m-%d")

        # Top 10 per score attuale
        cursor.execute('''
            SELECT niche, AVG(score) as avg_score, MAX(date) as last_seen
            FROM niche_signals
            WHERE date LIKE ?
            GROUP BY niche
            ORDER BY avg_score DESC
            LIMIT 10
        ''', (latest_date[:10] + "%",))
        current_tops = cursor.fetchall()

        # Score di una settimana fa per calcolare WoW
        cursor.execute('''
            SELECT niche, AVG(score) as old_score
            FROM niche_signals
            WHERE date LIKE ?
            GROUP BY niche
        ''', (one_week_ago + "%",))
        old_scores = {row[0]: row[1] for row in cursor.fetchall()}

        # Report Content
        report = f"# 🚀 Radar-Nicchie: Report Opportunità\n"
        report += f"Data generazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "## 🏆 Top 10 Nicchie per Opportunity Score\n"
        report += "| Posizione | Nicchia | Score | Var. WoW | Ultimo Aggiornamento |\n"
        report += "| :--- | :--- | :--- | :--- | :--- |\n"

        config = load_config()
        threshold = config.get('alert_threshold', 0)

        added_rows = 0
        for i, (niche, score, last_seen) in enumerate(current_tops, 1):
            if only_above_threshold and score < threshold:
                continue

            old_score = old_scores.get(niche)
            variation_str = "N/A"
            if old_score is not None:
                variation = score - old_score
                variation_str = f"{variation:+.2f}"

            report += f"| {i} | **{niche}** | {score:.2f} | {variation_str} | {last_seen} |\n"
            added_rows += 1

        if added_rows == 0 and only_above_threshold:
            return None # Nessuna nicchia sopra la soglia per il report Issue

        report += "\n---\n"
        report += "*Nota: Lo score è calcolato combinando segnali da Google Trends, Reddit e Udemy.*"

        # Salva il report
        with open("report/latest_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        logger.info("Report generato con successo in report/latest_report.md")
        return report

    except Exception as e:
        logger.error(f"Errore durante la generazione del report: {e}")
        return None
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    generate_markdown_report()
