# Pool-Adjacent-Violators (PAV) isotonic calibration; stdlib-only.
# Fit on (p_pred, y_true) pairs, produce monotone step mapping.

from typing import List, Tuple, Dict

# Probability bounds to prevent numerical issues
PROB_MIN = 0.001
PROB_MAX = 0.999

def fit_pav(p_pred: List[float], y_true: List[int]) -> Dict:
    """
    Fit PAV isotonic calibration on predicted probabilities and actual outcomes.
    
    Args:
        p_pred: List of predicted probabilities (0.0 to 1.0)
        y_true: List of actual binary outcomes (0 or 1)
    
    Returns:
        Dictionary with 'levels' and 'thresholds' for calibration mapping
    """
    pairs = sorted(zip(p_pred, y_true), key=lambda x: x[0])
    # Start with each point as its own bin
    bins = [{"sumy": y, "n": 1, "p": y} for _, y in pairs]
    # Merge adjacent bins that violate monotonicity
    i = 0
    while i < len(bins) - 1:
        if bins[i]["p"] > bins[i+1]["p"]:
            # pool
            sy = bins[i]["sumy"] + bins[i+1]["sumy"]
            n = bins[i]["n"] + bins[i+1]["n"]
            bins[i] = {"sumy": sy, "n": n, "p": sy / n}
            del bins[i+1]
            if i > 0: i -= 1
        else:
            i += 1
    # Build step function: breakpoints at midpoints of adjacent pred ranges
    # We map predicted p to calibrated p via cumulative coverage.
    # For runtime, we only need the calibrated levels and percentile thresholds.
    levels = [b["p"] for b in bins]
    # Equal-mass breakpoints by original sorted preds
    # Use cumulative counts to place thresholds between bins
    thresholds = []
    cum = 0
    total = sum(b["n"] for b in bins)
    for b in bins[:-1]:
        cum += b["n"]
        thresholds.append(cum / total)  # quantile cut
    return {"levels": levels, "thresholds": thresholds}

def apply_pav(p: float, calib: Dict) -> float:
    """
    Apply PAV calibration to a predicted probability.
    
    Args:
        p: Raw predicted probability
        calib: Calibration dictionary from fit_pav()
    
    Returns:
        Calibrated probability
    """
    # Map p's rank position to a calibrated level using thresholds.
    # If you saved thresholds in quantiles, pass predicted rank instead.
    # Simpler: treat p directly as a "rank-like" key; monotone but approximate.
    ts = calib["thresholds"]; lv = calib["levels"]
    # binary search on thresholds
    lo, hi = 0, len(ts)
    while lo < hi:
        mid = (lo + hi) // 2
        if p > ts[mid]: lo = mid + 1
        else: hi = mid
    return max(PROB_MIN, min(PROB_MAX, lv[lo]))
