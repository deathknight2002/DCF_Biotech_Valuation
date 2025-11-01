# BT Platform - Prediction API v2

## Overview

The BT Platform provides advanced prediction models for biotech catalyst analysis, including timing prediction, outcome probability, momentum scoring, and alpha calculation. This v2 upgrade adds:

- **Hazard spikes**: Calendar-aware timing with conference/PDUFA windows
- **PAV calibration**: Isotonic reliability calibration for probabilities
- **Peer-neutral momentum**: Z-scored momentum with streak detection
- **Alpha scoring**: Expected value with downside risk weighting

## Architecture

The platform is organized as follows:

```
bt_platform/
├── core/
│   └── prediction/
│       ├── adapters.py              # Data access layer (TODO: implement DB)
│       ├── calibration.py           # PAV isotonic calibration
│       ├── timing_predictor_v2.py   # Weibull timing with hazards
│       ├── outcome_predictor_v2.py  # Bayesian outcome in odds space
│       ├── momentum_scorer_v2.py    # Peer-neutral momentum
│       └── alpha_scorer.py          # Expected alpha calculation
└── endpoints/
    └── predictions_v2.py            # WSGI REST API server
```

## API Endpoints

### Start the Server

```bash
cd /path/to/DCF_Biotech_Valuation
python3 bt_platform/endpoints/predictions_v2.py
```

Server runs on `http://localhost:8081`

### GET /v2/predict/timing/{id}

Predict quarterly probability distribution for catalyst timing.

**Example:**
```bash
curl http://localhost:8081/v2/predict/timing/CAT-001
```

**Response:**
```json
{
  "catalyst_id": "CAT-001",
  "type": "TRIAL_READOUT",
  "reference": "Weibull_v2(TA_scale=0.9)",
  "quarterly_probabilities": [0.1108, 0.1936, 0.1647, 0.1309],
  "bins": [
    ["2025-11-01", "2025-12-01"],
    ["2026-01-01", "2026-03-01"],
    ["2026-04-01", "2026-06-01"],
    ["2026-07-01", "2026-09-01"]
  ],
  "outside_window": 0.4
}
```

### GET /v2/predict/outcome/{id}

Predict probability of success using Bayesian evidence stacking.

**Example:**
```bash
curl http://localhost:8081/v2/predict/outcome/CAT-001
```

**Response:**
```json
{
  "probability_of_success": 0.5581,
  "prior_probability": 0.48,
  "evidence_factors": [
    {"factor": "prior_phase_success", "impact": "+15%"},
    {"factor": "biomarker_enrichment", "impact": "+10%"},
    {"factor": "hard_endpoints", "impact": "+5%"},
    {"factor": "large_trial", "impact": "+3%"}
  ],
  "calibrated": false
}
```

### GET /v2/momentum/company/{name}

Calculate momentum score for a company (0-100 scale).

**Example:**
```bash
curl "http://localhost:8081/v2/momentum/company/Example%20Biotech"
```

**Response:**
```json
{
  "company": "Example Biotech",
  "momentum_score": 99.8,
  "components": {
    "base": 0.201,
    "streak": 12.0,
    "ta_z": 0.445
  }
}
```

### GET /v2/momentum/therapeutic-areas

Get momentum scores by therapeutic area.

**Example:**
```bash
curl http://localhost:8081/v2/momentum/therapeutic-areas
```

**Response:**
```json
{
  "Oncology": 0.334,
  "Cardiovascular": -0.322,
  "Neurology": 0.195,
  "Rare Disease": 0.157
}
```

### GET /v2/upcoming

List upcoming catalysts with timing and outcome predictions.

**Parameters:**
- `limit` (default: 20): Maximum number of catalysts
- `min_confidence` (default: 0.6): Minimum timing confidence threshold

**Example:**
```bash
curl "http://localhost:8081/v2/upcoming?limit=10&min_confidence=0.6"
```

**Response:**
```json
{
  "upcoming": [
    {
      "catalyst_id": "CAT-001",
      "ticker": "BIOT1",
      "company": "Biotech Company 1",
      "therapeutic_area": "Oncology",
      "timing": { ... },
      "outcome": { ... }
    }
  ]
}
```

### GET /v2/alpha/top

Get top catalysts ranked by expected alpha (edge score).

**Parameters:**
- `limit` (default: 20): Maximum number of results

**Example:**
```bash
curl "http://localhost:8081/v2/alpha/top?limit=5"
```

**Response:**
```json
{
  "top": [
    {
      "catalyst_id": "CAT-001",
      "ticker": "BIOT1",
      "company": "Biotech Company 1",
      "therapeutic_area": "Oncology",
      "prob_success": 0.71,
      "mu_up": 0.23,
      "mu_down": 0.19,
      "ev": 0.065,
      "edge_score": 73.4,
      "timing_confidence": 0.60,
      "timing": { ... }
    }
  ]
}
```

## Core Modules

### Calibration (calibration.py)

Provides PAV (Pool-Adjacent-Violators) isotonic calibration for probability reliability.

**Training (offline):**
```python
from bt_platform.core.prediction.calibration import fit_pav
import json

# Historical predictions vs actual outcomes
p_pred = [0.3, 0.5, 0.7, 0.8, 0.9]
y_true = [0, 0, 1, 1, 1]

# Fit and save
calibrator = fit_pav(p_pred, y_true)
with open('calibrator.json', 'w') as f:
    json.dump(calibrator, f)
```

**Runtime:**
```python
from bt_platform.core.prediction.calibration import apply_pav
import json

# Load calibrator
with open('calibrator.json') as f:
    calib = json.load(f)

# Apply to new predictions
raw_p = 0.65
calibrated_p = apply_pav(raw_p, calib)
```

### Timing Predictor v2 (timing_predictor_v2.py)

Uses Weibull distributions with:
- Therapeutic area scaling factors
- Hazard spike windows (conferences, FDA meetings)
- Optional two-component mixtures for bimodal trials

**Hazard Windows:**
```python
import datetime as dt
from bt_platform.core.prediction.timing_predictor_v2 import predict_quarterly_distribution_v2

# Define hazard windows (e.g., ASCO week)
hazards = [
    (dt.date(2025, 6, 1), dt.date(2025, 6, 15), 1.3)  # 30% boost
]

timing = predict_quarterly_distribution_v2(catalyst, hazard_windows=hazards)
```

### Outcome Predictor v2 (outcome_predictor_v2.py)

Bayesian inference in odds space with:
- Phase-specific priors
- Evidence stacking (prior success, biomarkers, endpoints, trial size)
- Optional PAV calibration

### Momentum Scorer v2 (momentum_scorer_v2.py)

Advanced momentum with:
- Exponential decay (30-day half-life)
- Streak detection (capped at 5)
- Therapeutic area z-score normalization

### Alpha Scorer (alpha_scorer.py)

Expected value calculation:
```
EV = P(success) × E[up_move] - P(failure) × penalty × E[down_move]
```

Factors:
- Historical reaction samples (company/TA/global hierarchy)
- Robust mean estimation (trimmed)
- Timing confidence weighting
- Downside penalty (1.1x)

## Data Adapters (adapters.py)

The `adapters.py` module contains **TODO_DB** placeholders for database integration:

- `get_catalyst_by_id(catalyst_id)` - Fetch catalyst details
- `list_upcoming_catalysts(limit)` - List upcoming events
- `get_company_outcomes(company, lookback_days)` - Historical outcomes
- `get_ta_outcomes(lookback_days)` - TA-grouped outcomes
- `get_reaction_samples(company, ta, catal_type, direction)` - Price reactions

Currently uses mock data. Replace with actual database queries.

## Configuration

### Runtime Configuration (predictions_v2.py)

```python
# Load calibrator (optional)
import json
with open('calibrator.json') as f:
    PAV_CALIBRATOR = json.load(f)

# Define hazard windows (optional)
HAZARD_WINDOWS = [
    (dt.date(2025, 6, 1), dt.date(2025, 6, 15), 1.3),  # ASCO
    (dt.date(2025, 11, 16), dt.date(2025, 11, 22), 1.2)  # AHA
]
```

### Model Parameters

Edit constants in the respective modules:

**Timing (timing_predictor_v2.py):**
```python
DEFAULT_WEIBULL = {
    "P1": (1.2, 180.0),   # shape, scale
    "P2": (1.4, 360.0),
    "P3": (1.6, 540.0),
    "FDA": (2.0, 300.0)
}

TA_SCALE = {
    "Oncology": 0.90,
    "Cardiovascular": 1.00,
    "Neurology": 1.05
}
```

**Outcome (outcome_predictor_v2.py):**
```python
PHASE_PRIOR = {
    "P1": 0.63,
    "P2": 0.30,
    "P3": 0.48,
    "FDA": 0.85
}

LOG_ODDS = {
    "prior_phase_success": 0.1398,
    "biomarker_enrichment": 0.0953,
    "hard_endpoints": 0.0488,
    "large_trial": 0.0296
}
```

## Development Workflow

### Day 0-1: Initial Setup
- ✅ Drop in all modules
- ✅ Implement adapter TODOs
- ✅ Test all endpoints
- ⚠️ Add hazard windows configuration

### Day 2-3: Calibration & Backtesting
- Export historical predictions vs outcomes
- Fit PAV calibrator
- Export event reactions by company/TA/type
- Verify Brier score improvement (target: ↓10%)

### Day 4: Production
- Deploy calibrator JSON
- Configure hazard windows
- Monitor `/v2/alpha/top` for hunt list

### Day 5+: Optimization
- TA-specific Weibull parameters
- Mixture models for bimodal trials
- Learned log-odds coefficients

## Testing

Run manual tests:

```bash
# Start server
python3 bt_platform/endpoints/predictions_v2.py

# Test endpoints (in another terminal)
curl http://localhost:8081/v2/predict/timing/TEST-001
curl http://localhost:8081/v2/predict/outcome/TEST-001
curl http://localhost:8081/v2/momentum/company/Example%20Biotech
curl http://localhost:8081/v2/momentum/therapeutic-areas
curl "http://localhost:8081/v2/upcoming?limit=5"
curl "http://localhost:8081/v2/alpha/top?limit=5"
```

## Dependencies

All modules use **stdlib only** for production runtime. No external dependencies required beyond Python 3.8+.

Optional offline training may use:
- `sklearn` for calibration fitting
- `pandas` for data manipulation
- `numpy` for numerical computing

But all trained parameters are serialized to JSON for stdlib-only runtime.

## License

Part of the DCF_Biotech_Valuation project.
