import pytest
from scoring.opportunity_score import calculate_niche_score

def test_calculate_niche_score_high_growth():
    """Testa lo scoring con dati di crescita elevata."""
    gt_data = {'trend_slope': 2.0, 'breakout_detected': True}
    red_data = {'total_engagement': 1000, 'engagement_per_post': 20}
    ud_data = {'total_courses': 50, 'competition_density': 0.05}
    weights = {'google_trends': 30, 'reddit_engagement': 40, 'udemy_market': 30}

    score = calculate_niche_score(gt_data, red_data, ud_data, weights)

    # Dovrebbe essere molto alto (>80)
    assert score > 80
    assert score <= 100

def test_calculate_niche_score_low_interest():
    """Testa lo scoring con dati di scarso interesse."""
    gt_data = {'trend_slope': -0.1, 'breakout_detected': False}
    red_data = {'total_engagement': 5, 'engagement_per_post': 0.5}
    ud_data = {'total_courses': 2000, 'competition_density': 2.0}
    weights = {'google_trends': 33, 'reddit_engagement': 33, 'udemy_market': 34}

    score = calculate_niche_score(gt_data, red_data, ud_data, weights)

    # Dovrebbe essere basso (<30)
    assert score < 30

def test_calculate_niche_score_zero_weights():
    """Testa il comportamento con pesi a zero."""
    gt_data = {'trend_slope': 1.0, 'breakout_detected': True}
    red_data = {'total_engagement': 100, 'engagement_per_post': 5}
    ud_data = {'total_courses': 10, 'competition_density': 0.01}
    weights = {'google_trends': 0, 'reddit_engagement': 0, 'udemy_market': 0}

    score = calculate_niche_score(gt_data, red_data, ud_data, weights)
    assert score == 0

def test_calculate_niche_score_missing_keys():
    """Testa la robustezza con chiavi mancanti nei dati."""
    gt_data = {}
    red_data = {}
    ud_data = {}
    weights = {'google_trends': 100}

    # Non deve crashare
    score = calculate_niche_score(gt_data, red_data, ud_data, weights)
    assert isinstance(score, float)

def test_calculate_niche_score_with_manual_data():
    """Testa lo scoring con dati manuali."""
    gt_data = {'trend_slope': 0, 'breakout_detected': False}
    red_data = {'total_engagement': 0, 'engagement_per_post': 0}
    ud_data = {'total_courses': 0, 'competition_density': 0}
    manual_data = {'Gumroad': 500, 'KDP': 500} # Totale 1000 -> 100 score manual
    weights = {'manual_market': 100}

    score = calculate_niche_score(gt_data, red_data, ud_data, weights, manual_data)
    assert score == 100
