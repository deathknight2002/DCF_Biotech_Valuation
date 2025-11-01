import math
import datetime as dt
from typing import Dict, List
from statistics import mean, pstdev
from .adapters import get_company_outcomes, get_ta_outcomes

HALF_LIFE = 30.0
STREAK_UNIT = 6.0
TA_WEIGHT = 0.35

def _decay(days_ago: float) -> float:
    """Calculate exponential decay factor"""
    return 0.5 ** (days_ago / HALF_LIFE)

def _raw(events: List[tuple]) -> float:
    """Calculate raw momentum score from events"""
    if not events:
        return 0.0
    today = dt.date.today()
    s = 0.0
    for (d, pol, w) in events:
        age = (today-d).days
        s += pol * w * _decay(max(0,age))
    return s

def _streak(events: List[tuple]) -> float:
    """Calculate streak bonus/penalty"""
    if not events:
        return 0.0
    arr = sorted(events, key=lambda x:x[0])
    last = 0
    st = 0
    for (_,pol,_) in arr:
        if pol == last and pol != 0:
            st += 1
        else:
            st = 1
            last = pol
    st = min(5, st) * (1 if last > 0 else -1)
    return STREAK_UNIT * st

def score_company_advanced(company: str) -> Dict:
    """
    Calculate advanced momentum score with peer-neutralization and streak.
    
    Args:
        company: Company name
    
    Returns:
        Dictionary with momentum score and components
    """
    comp = get_company_outcomes(company, lookback_days=730)
    base = _raw(comp)
    streak = _streak(comp)

    ta_map = get_ta_outcomes(lookback_days=730)
    ta_scores = [_raw(v) for v in ta_map.values()] or [0.0]
    z = (base - mean(ta_scores)) / (pstdev(ta_scores) or 1.0)

    combined = base + streak + TA_WEIGHT*z
    score = 50 + 50*math.tanh(0.25*combined)
    return {
        "company": company,
        "momentum_score": round(score,1),
        "components": {
            "base": round(base,3),
            "streak": round(streak,3),
            "ta_z": round(z,3)
        }
    }
