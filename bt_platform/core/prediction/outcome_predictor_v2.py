from typing import Dict, List, Optional
from dataclasses import dataclass
from .adapters import Catalyst
from .calibration import apply_pav

PHASE_PRIOR = {"P1":0.63,"P2":0.30,"P3":0.48,"FDA":0.85}
TA_ABS_UP = {"Rare Disease": 0.14}

# Default log-odds increments ≈ your v1 multipliers; can be replaced from JSON
LOG_ODDS = {
  "prior_phase_success": 0.1398,   # ~ +15% odds  -> ln(1.15)
  "biomarker_enrichment": 0.0953,  # ~ +10% odds  -> ln(1.10)
  "hard_endpoints": 0.0488,        # ~ +5%  odds  -> ln(1.05)
  "large_trial": 0.0296            # ~ +3%  odds  -> ln(1.03)
}

@dataclass
class OutcomeV2:
    """Outcome prediction result with calibration metadata"""
    probability_of_success: float
    prior_probability: float
    evidence_factors: List[Dict[str,str]]
    calibrated: bool

def _p2o(p: float) -> float:
    """Convert probability to odds"""
    p = max(1e-6, min(1-1e-6, p))
    return p/(1-p)

def _o2p(o: float) -> float:
    """Convert odds to probability"""
    return o/(1+o)

def predict_outcome_bayesian_v2(
    c: Catalyst,
    pav_calibrator: Optional[Dict] = None,
    log_odds: Optional[Dict] = None
) -> OutcomeV2:
    """
    Predict outcome probability using Bayesian inference in odds space.
    
    Args:
        c: Catalyst object with evidence factors
        pav_calibrator: Optional PAV calibration dictionary
        log_odds: Optional custom log-odds coefficients
    
    Returns:
        OutcomeV2 object with probability and evidence details
    """
    lo = log_odds or LOG_ODDS
    # prior
    prior = PHASE_PRIOR.get(c.phase or "P3", 0.48)
    if c.therapeutic_area in TA_ABS_UP:
        prior = max(0.001, min(0.999, prior + TA_ABS_UP[c.therapeutic_area]))
    odds = _p2o(prior)

    evidence = []
    def add(flag: bool, key: str, label: str):
        nonlocal odds
        if flag:
            odds *= (2.718281828 ** lo[key])
            pct = int(round(( (2.718281828 ** lo[key]) - 1 ) * 100))
            evidence.append({"factor": label, "impact": f"+{pct}%"})

    add(c.prior_phase_success, "prior_phase_success", "prior_phase_success")
    add(c.biomarker_enrichment, "biomarker_enrichment", "biomarker_enrichment")
    add(c.hard_endpoints, "hard_endpoints", "hard_endpoints")
    add(c.large_trial, "large_trial", "large_trial")

    raw_p = max(0.01, min(0.97, _o2p(odds)))
    p = apply_pav(raw_p, pav_calibrator) if pav_calibrator else raw_p
    return OutcomeV2(
        probability_of_success=round(p,4),
        prior_probability=round(prior,4),
        evidence_factors=evidence,
        calibrated=bool(pav_calibrator)
    )
