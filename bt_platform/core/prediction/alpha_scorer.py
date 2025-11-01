from typing import Dict, List, Optional
from statistics import median
from .adapters import get_reaction_samples, Catalyst
from .outcome_predictor_v2 import predict_outcome_bayesian_v2
from .timing_predictor_v2 import predict_quarterly_distribution_v2

# Fallback values for expected moves when historical data is unavailable
DEFAULT_MU_UP = 0.12  # Default +12% upside
DEFAULT_MU_DOWN = 0.18  # Default -18% downside

def _robust_mean(xs: List[float]) -> float:
    """Calculate robust mean using trimmed average"""
    if not xs:
        return 0.0
    xs = sorted(xs)
    n = len(xs)
    lo = xs[max(0, n//10)]
    hi = xs[min(n-1, int(n*0.9))]
    mid = xs[n//2]
    return 0.25*lo + 0.5*mid + 0.25*hi

def expected_alpha_for_catalyst(
    c: Catalyst,
    pav_calib: Optional[Dict] = None,
    hazard_windows: Optional[List] = None
) -> Dict:
    """
    Calculate expected alpha (expected value) for a catalyst.
    
    Combines:
    - Outcome probability (success/failure)
    - Expected price moves (from historical reactions)
    - Timing confidence (near-term likelihood)
    - Downside penalty (risk-aware EV)
    
    Args:
        c: Catalyst object
        pav_calib: Optional PAV calibration dictionary
        hazard_windows: Optional hazard spike windows for timing
    
    Returns:
        Dictionary with alpha metrics and edge score
    """
    # Outcome
    out = predict_outcome_bayesian_v2(c, pav_calibrator=pav_calib)
    p = out.probability_of_success

    # Expected moves from your own history (company first, then TA fallback, then global)
    up_samples   = get_reaction_samples(c.company, c.therapeutic_area, c.catalyst_type, direction="up")
    down_samples = get_reaction_samples(c.company, c.therapeutic_area, c.catalyst_type, direction="down")
    mu_up   = abs(_robust_mean(up_samples))   or DEFAULT_MU_UP
    mu_down = abs(_robust_mean(down_samples)) or DEFAULT_MU_DOWN

    # Timing confidence to weight near-term alpha (if you care about 4Q window)
    t = predict_quarterly_distribution_v2(c, hazard_windows=hazard_windows)
    conf = 1.0 - t.get("outside_window", 0.4)

    # Expected alpha (directional EV), risk-aware: penalize downside heavier
    downside_penalty = 1.1
    ev = p*mu_up - (1-p)*downside_penalty*mu_down

    # Edge score 0-100 from EV (squash), scaled by timing confidence
    raw = ev * 100.0
    score = max(0.0, min(100.0, (50 + 15*raw))) * conf

    return {
        "catalyst_id": c.id,
        "ticker": c.ticker,
        "company": c.company,
        "therapeutic_area": c.therapeutic_area,
        "prob_success": p,
        "mu_up": round(mu_up,4),
        "mu_down": round(mu_down,4),
        "ev": round(ev,4),
        "edge_score": round(score,2),
        "timing_confidence": round(conf,3),
        "timing": t
    }
