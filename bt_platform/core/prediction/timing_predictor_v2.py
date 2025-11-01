import math
import datetime as dt
from typing import Dict, List, Tuple, Optional
from .adapters import Catalyst

# Defaults; override via calibration JSON when ready
DEFAULT_WEIBULL = {"P1": (1.2, 180.0), "P2": (1.4, 360.0), "P3": (1.6, 540.0), "FDA": (2.0, 300.0)}
TA_SCALE = {"Oncology": 0.90, "Cardiovascular": 1.00, "Neurology": 1.05}  # tweak as you learn

def weibull_cdf(t: float, k: float, lam: float) -> float:
    """Weibull cumulative distribution function"""
    return 0.0 if t <= 0 else 1.0 - math.exp(- (t/lam)**k)

def days(a: dt.date, b: dt.date) -> int:
    """Calculate days between two dates"""
    return (b - a).days

def quarterly_bins(start: dt.date, n=4) -> List[Tuple[dt.date, dt.date]]:
    """Generate n quarterly bins starting from start date"""
    s = dt.date(start.year, start.month, 1)
    out = []
    for _ in range(n):
        q = ((s.month - 1)//3)+1
        end_month = q*3
        end = dt.date(s.year, end_month, 1)
        out.append((s, end))
        m = end_month+1
        y = s.year + (1 if m>12 else 0)
        m = 1 if m>12 else m
        s = dt.date(y, m, 1)
    return out

def _daily_mass(anchor: dt.date, k: float, lam: float, d0: dt.date, d1: dt.date) -> List[Tuple[dt.date, float]]:
    """Calculate per-day mass between [d0,d1) using Weibull distribution"""
    masses = []
    cur = d0
    while cur < d1:
        t0 = max(0, days(anchor, cur))
        t1 = t0+1
        p = max(0.0, weibull_cdf(t1, k, lam) - weibull_cdf(t0, k, lam))
        masses.append((cur, p))
        cur += dt.timedelta(days=1)
    return masses

def predict_quarterly_distribution_v2(
    c: Catalyst,
    hazard_windows: Optional[List[Tuple[dt.date, dt.date, float]]] = None,
    mixture: Optional[Tuple[float, Tuple[float,float], Tuple[float,float]]] = None,
    confidence_default: float = 0.60
) -> Dict:
    """
    Predict quarterly probability distribution for catalyst timing.
    
    Args:
        c: Catalyst object
        hazard_windows: Optional list of (start_date, end_date, boost_factor) for hazard spikes
        mixture: Optional (weight, (k1,lam1), (k2,lam2)) for two-component Weibull mixture
        confidence_default: Default confidence level for timing estimates
    
    Returns:
        Dictionary with quarterly probabilities and metadata
    """
    today = dt.date.today()

    # PDUFA (pointy): put 90% mass on the known quarter; smear the rest
    if c.catalyst_type == "PDUFA" and c.pdufa_date:
        bins = quarterly_bins(today, 4)
        probs = [0.0]*4
        idx = next((i for i,(b0,b1) in enumerate(bins) if b0 <= c.pdufa_date < b1), None)
        if idx is not None:
            probs[idx] = 0.90
            neighbors = [i for i in [idx-1, idx+1] if 0<=i<4]
            for i in neighbors:
                probs[i] += 0.10/max(1,len(neighbors))
        else:
            probs[0] = 0.10  # overflow outside 4Q not modeled
        return {
            "catalyst_id": c.id,
            "type": c.catalyst_type,
            "reference": "PDUFA-fixed(90%)",
            "quarterly_probabilities": [round(p,4) for p in probs],
            "bins": [(str(b0), str(b1)) for (b0,b1) in bins],
            "outside_window": 0.10
        }

    # TRIAL READOUT / FDA timing via Weibull, TA scale, optional mixture, hazard boosts
    phase = c.phase or "P3"
    k, lam = DEFAULT_WEIBULL.get(phase, (1.6, 540.0))
    lam *= TA_SCALE.get(c.therapeutic_area, 1.0)

    if mixture:
        w, (k1,lam1), (k2,lam2) = mixture
    else:
        w, (k1,lam1), (k2,lam2) = 1.0, (k,lam), (k,lam)  # degenerate

    anchor = c.anchor_date or (today - dt.timedelta(days=int(lam)))
    bins = quarterly_bins(today, 4)
    q_mass = [0.0,0.0,0.0,0.0]

    for i,(b0,b1) in enumerate(bins):
        # daily mass with hazard boosts
        daily1 = _daily_mass(anchor, k1, lam1, b0, b1)
        daily2 = _daily_mass(anchor, k2, lam2, b0, b1)
        for (d, p1), (_, p2) in zip(daily1, daily2):
            p = w*p1 + (1.0-w)*p2
            if hazard_windows:
                for (h0,h1,boost) in hazard_windows:
                    if h0 <= d < h1:
                        p *= boost
            q_mass[i] += p

    total = sum(q_mass)
    if total <= 0:
        q = [1.0,0.0,0.0,0.0]
    else:
        q = [m/total for m in q_mass]

    conf = confidence_default if (c.catalyst_type=="TRIAL_READOUT" and phase=="P3") else 0.50
    q = [round(p*conf,4) for p in q]
    return {
        "catalyst_id": c.id,
        "type": c.catalyst_type,
        "reference": f"Weibull_v2(TA_scale={TA_SCALE.get(c.therapeutic_area,1.0)})",
        "quarterly_probabilities": q,
        "bins": [(str(b0), str(b1)) for (b0,b1) in bins],
        "outside_window": round(1.0 - conf, 4)
    }
