import logging
from typing import Dict, List, Any
from pytrends.request import TrendReq
from pytrends.exceptions import TooManyRequestsError
import time

logger = logging.getLogger(__name__)

# Google Trends non ha una API ufficiale: pytrends simula il traffico del sito
# e Google applica rate-limit (HTTP 429) in modo aggressivo e imprevedibile.
# Questo retry con backoff esponenziale riduce le richieste fallite, ma non
# elimina il rischio: se Google continua a rispondere 429, la keyword resta
# a 0 e viene segnalata nei log invece di far fallire l'intera pipeline.
MAX_RETRIES = 3
BASE_BACKOFF_SECONDS = 20
REQUEST_DELAY_SECONDS = 5


def _fetch_keyword_data(pytrends: TrendReq, kw: str) -> Dict[str, Any]:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            pytrends.build_payload([kw], cat=0, timeframe='today 3-m', geo='', gprop='')

            # Interest Over Time
            iot = pytrends.interest_over_time()
            trend_slope = 0
            if not iot.empty and kw in iot:
                # Calcola una pendenza semplice (differenza tra fine e inizio periodo)
                recent_values = iot[kw].values
                if len(recent_values) > 1:
                    trend_slope = (recent_values[-1] - recent_values[0]) / len(recent_values)

            # Related Queries (Rising / Breakout)
            related = pytrends.related_queries()
            rising_queries = []
            if kw in related and related[kw]['rising'] is not None:
                rising_df = related[kw]['rising']
                if not rising_df.empty:
                    rising_queries = rising_df.to_dict('records')

            return {
                'trend_slope': trend_slope,
                'rising_queries_count': len(rising_queries),
                'breakout_detected': any(q['value'] == 'breakout' for q in rising_queries if isinstance(q.get('value'), str)) or any(q.get('value', 0) > 1000 for q in rising_queries if isinstance(q.get('value'), (int, float)))
            }

        except TooManyRequestsError as e:
            if attempt == MAX_RETRIES:
                raise
            wait = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
            logger.warning(
                f"Google Trends ha risposto 429 (rate-limit) per '{kw}' "
                f"(tentativo {attempt}/{MAX_RETRIES}). Riprovo tra {wait}s..."
            )
            time.sleep(wait)

    raise TooManyRequestsError("Rate-limit persistente da Google Trends")


def fetch_google_trends(keywords: List[str]) -> Dict[str, Any]:
    """
    Ottiene dati da Google Trends per una lista di keyword.
    Gestisce errori e rate-limit con retry a backoff esponenziale.

    Nota: pytrends usa l'endpoint non ufficiale di Google Trends. Google può
    bloccare le richieste (429) indipendentemente dal volume o dalla
    correttezza del codice. Se i 429 persistono, valuta di aumentare
    REQUEST_DELAY_SECONDS o di eseguire la pipeline con meno keyword per volta.
    """
    results = {}
    pytrends = TrendReq(hl='en-US', tz=360)

    for kw in keywords:
        try:
            logger.info(f"Recupero dati Google Trends per: {kw}")
            results[kw] = _fetch_keyword_data(pytrends, kw)

        except Exception as e:
            logger.error(f"Errore durante il recupero dei dati per {kw} da Google Trends: {e}")
            results[kw] = {
                'trend_slope': 0,
                'rising_queries_count': 0,
                'breakout_detected': False,
                'error': str(e)
            }

        # Pausa tra keyword per ridurre il rischio di rate limit
        time.sleep(REQUEST_DELAY_SECONDS)

    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Test veloce
    test_keywords = ["AI automation", "sustainable fashion"]
    print(fetch_google_trends(test_keywords))
