import os
import praw
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

def fetch_reddit_data(subreddits: List[str], keywords: List[str]) -> Dict[str, Any]:
    """
    Ottiene dati da Reddit: engagement sui post recenti relativi alle keyword.
    """
    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "RadarNicchie/0.1")

    if not client_id or not client_secret:
        logger.error("Credenziali Reddit mancanti nelle variabili d'ambiente.")
        return {}

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
    except Exception as e:
        logger.error(f"Errore nella connessione a Reddit: {e}")
        return {}

    results = {}
    time_limit = datetime.utcnow() - timedelta(days=7)

    for kw in keywords:
        kw_engagement = 0
        kw_posts_count = 0
        subscriber_growth = 0 # Placeholder per compatibilità se decidessimo di implementarlo

        for sub_name in subreddits:
            try:
                subreddit = reddit.subreddit(sub_name)
                # Cerca post nell'ultima settimana per misurare la "velocità" di discussione
                # (Post nuovi = interesse recente)
                for submission in subreddit.search(kw, time_filter='week', limit=50):
                    created_at = datetime.utcfromtimestamp(submission.created_utc)
                    if created_at > time_limit:
                        # Engagement pesato: commenti valgono più dei semplici upvote (mostrano interesse profondo)
                        engagement = submission.score + (submission.num_comments * 2)
                        kw_engagement += engagement
                        kw_posts_count += 1
            except Exception as e:
                logger.warning(f"Errore nel subreddit r/{sub_name} per la keyword '{kw}': {e}")
                continue

        results[kw] = {
            'total_engagement': kw_engagement,
            'posts_count': kw_posts_count,
            'engagement_per_post': kw_engagement / kw_posts_count if kw_posts_count > 0 else 0,
            # 'velocity' è la densità di post nell'ultima settimana
            'velocity': kw_posts_count / 7.0
        }

    return results

if __name__ == "__main__":
    # Test veloce (richiede variabili d'ambiente)
    print(fetch_reddit_data(["solopreneur"], ["saas"]))
