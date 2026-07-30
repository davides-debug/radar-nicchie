import yaml
import logging
from dotenv import load_dotenv
load_dotenv()

from sources.google_trends import fetch_google_trends
from sources.reddit import fetch_reddit_data
from sources.udemy import fetch_udemy_data
from sources.manual_marketplaces import get_latest_manual_data
from scoring.opportunity_score import calculate_niche_score
from storage.db_manager import init_db, save_niche_data
from report.generate_report import generate_markdown_report
from report.generate_dashboard import generate_dashboard
import os

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pipeline.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    with open("config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def run_pipeline():
    logger.info("Avvio della pipeline Radar-Nicchie")
    config = load_config()
    keywords = config.get('keywords', [])
    subreddits = config.get('subreddits', [])
    udemy_topics = config.get('udemy_topics', [])
    weights = config.get('scoring_weights', {})

    init_db()

    # 1. Recupero dati (Fallimento isolato garantito dai try-except nei moduli)
    logger.info("Recupero dati da Google Trends...")
    gt_results = fetch_google_trends(keywords)

    logger.info("Recupero dati da Reddit...")
    reddit_results = fetch_reddit_data(subreddits, keywords)

    logger.info("Recupero dati da Udemy...")
    # Per Udemy mappiamo le keyword ai topic più vicini se necessario,
    # o usiamo direttamente i topic configurati.
    # Qui usiamo i topic per semplicità, ma associamo i risultati alle keyword principali.
    udemy_results = fetch_udemy_data(udemy_topics)

    logger.info("Recupero dati manuali (Gumroad/KDP)...")
    manual_all_data = get_latest_manual_data()

    # 2. Scoring e Storage
    for kw in keywords:
        logger.info(f"Elaborazione punteggio per: {kw}")

        # Associazioni: cerca il topic Udemy che meglio corrisponde alla keyword
        # Se non c'è corrispondenza esatta, prova a vedere se la keyword è contenuta nel topic o viceversa
        topic = None
        for t in udemy_topics:
            if t.lower() in kw.lower() or kw.lower() in t.lower():
                topic = t
                break

        # Fallback se non trovato
        if not topic:
            topic = udemy_topics[0] if udemy_topics else kw

        kw_gt = gt_results.get(kw, {})
        kw_reddit = reddit_results.get(kw, {})
        kw_udemy = udemy_results.get(topic, {})
        kw_manual = manual_all_data.get(kw, {})

        score = calculate_niche_score(kw_gt, kw_reddit, kw_udemy, weights, kw_manual)

        logger.info(f"Nicchia: {kw} | Score: {score}")

        # Salvataggio nel DB (uno per fonte per mantenere lo storico richiesto)
        save_niche_data(kw, "google_trends", kw_gt.get('trend_slope', 0), score)
        save_niche_data(kw, "reddit", kw_reddit.get('total_engagement', 0), score)
        save_niche_data(kw, "udemy", kw_udemy.get('total_courses', 0), score)

        for source, val in kw_manual.items():
            save_niche_data(kw, source, val, score)

    logger.info("Generazione report Markdown...")
    generate_markdown_report()

    logger.info("Generazione dashboard HTML...")
    generate_dashboard()

    logger.info("Pipeline completata con successo. Report: report/latest_report.md | Dashboard: report/dashboard.html")

if __name__ == "__main__":
    run_pipeline()
