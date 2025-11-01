import sys
import os
from pathlib import Path

# Add parent directory to path for imports
PACKAGE_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PACKAGE_ROOT))

from wsgiref.simple_server import make_server
from urllib.parse import parse_qs
import json
import re
import datetime as dt

from bt_platform.core.prediction.adapters import get_catalyst_by_id, list_upcoming_catalysts
from bt_platform.core.prediction.timing_predictor_v2 import predict_quarterly_distribution_v2
from bt_platform.core.prediction.outcome_predictor_v2 import predict_outcome_bayesian_v2
from bt_platform.core.prediction.momentum_scorer_v2 import score_company_advanced
from bt_platform.core.prediction.alpha_scorer import expected_alpha_for_catalyst

# Load optional runtime calibrator + hazard windows (from JSON file or env)
PAV_CALIBRATOR = None   # plug your saved {levels, thresholds}
HAZARD_WINDOWS = []     # e.g., [(dt.date(2025,6,1), dt.date(2025,6,15), 1.3)]

def _json(start, obj, code="200 OK"):
    """Helper to return JSON response"""
    b = json.dumps(obj, default=str).encode()
    start(code, [
        ("Content-Type","application/json"),
        ("Content-Length",str(len(b))),
        ("Access-Control-Allow-Origin","*")
    ])
    return [b]

def _404(start):
    """Helper to return 404 response"""
    return _json(start, {"error":"not found"}, "404 Not Found")

def app(environ, start_response):
    """WSGI application handler for v2 prediction API"""
    m = environ.get("REQUEST_METHOD","GET")
    path = environ.get("PATH_INFO","/")
    qs = parse_qs(environ.get("QUERY_STRING",""))

    # GET /v2/predict/timing/{id}
    g = re.fullmatch(r"/v2/predict/timing/([^/]+)", path)
    if m=="GET" and g:
        c = get_catalyst_by_id(g.group(1))
        return _json(start_response, predict_quarterly_distribution_v2(c, hazard_windows=HAZARD_WINDOWS))

    # GET /v2/predict/outcome/{id}
    g = re.fullmatch(r"/v2/predict/outcome/([^/]+)", path)
    if m=="GET" and g:
        c = get_catalyst_by_id(g.group(1))
        o = predict_outcome_bayesian_v2(c, pav_calibrator=PAV_CALIBRATOR)
        return _json(start_response, o.__dict__)

    # GET /v2/momentum/company/{name}
    g = re.fullmatch(r"/v2/momentum/company/(.+)", path)
    if m=="GET" and g:
        return _json(start_response, score_company_advanced(g.group(1)))

    # GET /v2/momentum/therapeutic-areas
    if m=="GET" and path=="/v2/momentum/therapeutic-areas":
        from bt_platform.core.prediction.momentum_scorer_v2 import _raw
        from bt_platform.core.prediction.adapters import get_ta_outcomes
        ta_map = get_ta_outcomes()
        out = {ta: round(_raw(v),3) for ta,v in ta_map.items()}
        return _json(start_response, out)

    # GET /v2/upcoming?limit=20&min_confidence=0.6
    if m=="GET" and path=="/v2/upcoming":
        limit = int(qs.get("limit",["20"])[0])
        min_conf = float(qs.get("min_confidence",["0.6"])[0])
        rows = []
        for c in list_upcoming_catalysts(limit=limit):
            t = predict_quarterly_distribution_v2(c, hazard_windows=HAZARD_WINDOWS)
            conf = 1.0 - t.get("outside_window", 0.4)
            if conf >= min_conf:
                o = predict_outcome_bayesian_v2(c, pav_calibrator=PAV_CALIBRATOR)
                rows.append({
                    "catalyst_id": c.id,
                    "ticker": c.ticker,
                    "company": c.company,
                    "therapeutic_area": c.therapeutic_area,
                    "timing": t,
                    "outcome": {
                        "probability_of_success": o.probability_of_success,
                        "prior_probability": o.prior_probability,
                        "evidence_factors": o.evidence_factors,
                        "calibrated": o.calibrated
                    }
                })
        return _json(start_response, {"upcoming": rows})

    # GET /v2/alpha/top?limit=20
    if m=="GET" and path=="/v2/alpha/top":
        limit = int(qs.get("limit",["20"])[0])
        cands = list_upcoming_catalysts(limit=limit*3)  # oversample then rank
        scored = [
            expected_alpha_for_catalyst(c, pav_calib=PAV_CALIBRATOR, hazard_windows=HAZARD_WINDOWS)
            for c in cands
        ]
        scored.sort(key=lambda r: r["edge_score"], reverse=True)
        return _json(start_response, {"top": scored[:limit]})

    return _404(start_response)

if __name__ == "__main__":
    with make_server("", 8081, app) as httpd:
        print("Prediction API v2 on :8081")
        httpd.serve_forever()
