import os
import requests
import logging
from typing import Dict, List, Any
from requests.auth import HTTPBasicAuth

logger = logging.getLogger(__name__)

def fetch_udemy_data(topics: List[str]) -> Dict[str, Any]:
    """
    Ottiene dati da Udemy: numero corsi, prezzo medio, recensioni.
    Usa la Udemy Affiliate API.
    """
    client_id = os.getenv("UDEMY_CLIENT_ID")
    client_secret = os.getenv("UDEMY_CLIENT_SECRET")

    if not client_id or not client_secret:
        logger.error("Credenziali Udemy mancanti nelle variabili d'ambiente.")
        return {}

    results = {}
    base_url = "https://www.udemy.com/api-2.0/courses/"

    for topic in topics:
        try:
            logger.info(f"Recupero dati Udemy per topic: {topic}")
            params = {
                "search": topic,
                "page_size": 20,
                "ordering": "relevance"
            }
            response = requests.get(
                base_url,
                params=params,
                auth=HTTPBasicAuth(client_id, client_secret),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                courses = data.get("results", [])
                total_courses = data.get("count", 0)

                avg_price = 0
                total_reviews = 0

                if courses:
                    # In una versione reale, dovremmo fare altre chiamate per dettagli specifici se non inclusi
                    # Qui facciamo una stima dai risultati della ricerca se disponibili
                    prices = []
                    for c in courses:
                        # Nota: i prezzi variano per regione e account
                        p_str = c.get("price", "0").replace("€", "").replace("$", "").strip()
                        try:
                            prices.append(float(p_str))
                        except:
                            pass

                    avg_price = sum(prices) / len(prices) if prices else 0
                    # Udemy API non sempre dà il numero di recensioni nella lista base,
                    # ma usiamo questo come placeholder per la logica.

                results[topic] = {
                    'total_courses': total_courses,
                    'avg_price': avg_price,
                    # Competizione: più corsi ci sono, più è alta
                    'competition_density': total_courses / 1000 if total_courses > 0 else 0
                }
            else:
                logger.error(f"Errore API Udemy ({response.status_code}): {response.text}")
                results[topic] = {'error': response.status_code}

        except Exception as e:
            logger.error(f"Errore durante il recupero dei dati Udemy per {topic}: {e}")
            results[topic] = {'error': str(e)}

    return results

if __name__ == "__main__":
    # Test veloce
    print(fetch_udemy_data(["Python"]))
