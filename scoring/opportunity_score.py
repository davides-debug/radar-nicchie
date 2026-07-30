import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def calculate_niche_score(
    google_data: Dict[str, Any],
    reddit_data: Dict[str, Any],
    udemy_data: Dict[str, Any],
    weights: Dict[str, float],
    manual_data: Optional[Dict[str, float]] = None
) -> float:
    """
    Calcola un punteggio di opportunità da 0 a 100 per una nicchia.

    Pesi configurabili:
    - google_trends: Importanza del trend di ricerca (segno di interesse crescente).
    - reddit_engagement: Importanza della discussione attiva (segno di community calda).
    - udemy_market: Importanza della domanda pagante vs competizione.
    """

    # 1. Score Google Trends (0-100)
    # Basato su pendenza trend e query breakout
    gt_slope = google_data.get('trend_slope', 0)
    gt_breakout = 100 if google_data.get('breakout_detected', False) else 0
    # Normalizziamo la pendenza: una pendenza di 2 (crescita veloce) è ottima
    gt_slope_score = min(max(gt_slope * 50, 0), 100)
    gt_final_score = (gt_slope_score * 0.7) + (gt_breakout * 0.3)

    # 2. Score Reddit (0-100)
    # Basato su engagement totale e engagement per post
    r_total = reddit_data.get('total_engagement', 0)
    r_per_post = reddit_data.get('engagement_per_post', 0)
    # Euristiche di normalizzazione
    r_total_score = min(r_total / 10, 100) # 1000 engagement = 100
    r_per_post_score = min(r_per_post * 5, 100) # 20 eng/post = 100
    r_final_score = (r_total_score * 0.4) + (r_per_post_score * 0.6)

    # 3. Score Udemy (0-100)
    # Basato su inverso della densità di competizione
    u_comp = udemy_data.get('competition_density', 0)
    # Se ci sono troppi corsi (alta densità), lo score scende
    # 0 corsi = 100 score (ma forse poca domanda), 500 corsi = 50 score, >1000 corsi = basso score
    u_comp_score = max(100 - (u_comp * 50), 0)
    # Bonus se c'è comunque un volume minimo di corsi (segno che il mercato esiste)
    u_total = udemy_data.get('total_courses', 0)
    u_demand_bonus = 20 if u_total > 10 else 0
    u_final_score = min(u_comp_score + u_demand_bonus, 100)

    # 4. Score Manual Market (0-100) - Gumroad / KDP
    m_final_score = 0
    if manual_data:
        # Esempio: valore è una stima di revenue potenziale o numero di bestseller
        # Normalizziamo assumendo che un valore di 1000 (euro/prodotti) sia ottimo
        # Sommiamo Gumroad e KDP se entrambi presenti
        total_manual_value = sum(manual_data.values())
        m_final_score = min(total_manual_value / 10, 100)

    # Calcolo pesato finale
    total_weight = sum(weights.values())
    if total_weight == 0:
        return 0

    weighted_score = (
        (gt_final_score * weights.get('google_trends', 0)) +
        (r_final_score * weights.get('reddit_engagement', 0)) +
        (u_final_score * weights.get('udemy_market', 0)) +
        (m_final_score * weights.get('manual_market', 0))
    ) / total_weight

    return round(min(max(weighted_score, 0), 100), 2)

if __name__ == "__main__":
    # Test della logica
    sample_gt = {'trend_slope': 1.5, 'breakout_detected': True}
    sample_red = {'total_engagement': 500, 'engagement_per_post': 15}
    sample_ud = {'total_courses': 100, 'competition_density': 0.1}
    sample_weights = {'google_trends': 35, 'reddit_engagement': 40, 'udemy_market': 25}

    print(f"Score calcolato: {calculate_niche_score(sample_gt, sample_red, sample_ud, sample_weights)}")
