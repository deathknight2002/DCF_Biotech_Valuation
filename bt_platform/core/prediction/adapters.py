"""
Data adapters for accessing catalyst and outcome data.
This module provides the data access layer for the prediction system.

TODO_DB: Replace mock implementations with actual database queries.
"""

import datetime as dt
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

@dataclass
class Catalyst:
    """Represents a clinical or regulatory catalyst event"""
    id: str
    company: str
    ticker: str
    therapeutic_area: str
    catalyst_type: str  # "TRIAL_READOUT", "PDUFA", "FDA"
    phase: Optional[str] = None  # "P1", "P2", "P3", "FDA"
    pdufa_date: Optional[dt.date] = None
    anchor_date: Optional[dt.date] = None
    
    # Evidence factors for outcome prediction
    prior_phase_success: bool = False
    biomarker_enrichment: bool = False
    hard_endpoints: bool = False
    large_trial: bool = False


def get_catalyst_by_id(catalyst_id: str) -> Catalyst:
    """
    Retrieve catalyst details by ID.
    
    TODO_DB: Implement database query to fetch catalyst by ID.
    """
    # Mock implementation - returns a sample catalyst
    return Catalyst(
        id=catalyst_id,
        company="Example Biotech",
        ticker="EXBIO",
        therapeutic_area="Oncology",
        catalyst_type="TRIAL_READOUT",
        phase="P3",
        anchor_date=dt.date.today() - dt.timedelta(days=365),
        prior_phase_success=True,
        biomarker_enrichment=True,
        hard_endpoints=True,
        large_trial=True
    )


def list_upcoming_catalysts(limit: int = 20) -> List[Catalyst]:
    """
    List upcoming catalysts sorted by expected timing.
    
    TODO_DB: Implement database query to fetch upcoming catalysts.
    """
    # Mock implementation - returns sample catalysts
    return [
        Catalyst(
            id=f"CAT-{i:03d}",
            company=f"Biotech Company {i}",
            ticker=f"BIOT{i}",
            therapeutic_area=["Oncology", "Cardiovascular", "Neurology", "Rare Disease"][i % 4],
            catalyst_type=["TRIAL_READOUT", "PDUFA", "FDA"][i % 3],
            phase=["P1", "P2", "P3"][i % 3],
            anchor_date=dt.date.today() - dt.timedelta(days=200 + i*10),
            prior_phase_success=(i % 2 == 0),
            biomarker_enrichment=(i % 3 == 0),
            hard_endpoints=(i % 2 == 1),
            large_trial=(i % 3 == 1)
        )
        for i in range(min(limit, 20))
    ]


def get_company_outcomes(company: str, lookback_days: int = 730) -> List[Tuple[dt.date, int, float]]:
    """
    Get historical outcome events for a company.
    
    Returns list of (date, polarity, weight) tuples where:
    - polarity: +1 for success, -1 for failure, 0 for neutral
    - weight: importance weighting (e.g., 1.0 for standard, 2.0 for major)
    
    TODO_DB: Implement database query to fetch company outcomes.
    """
    # Mock implementation - returns sample outcomes
    today = dt.date.today()
    return [
        (today - dt.timedelta(days=90), 1, 1.5),
        (today - dt.timedelta(days=180), 1, 1.0),
        (today - dt.timedelta(days=270), -1, 1.0),
        (today - dt.timedelta(days=450), 1, 2.0),
    ]


def get_ta_outcomes(lookback_days: int = 730) -> Dict[str, List[Tuple[dt.date, int, float]]]:
    """
    Get historical outcomes grouped by therapeutic area.
    
    Returns dict mapping TA name to list of (date, polarity, weight) tuples.
    
    TODO_DB: Implement database query to fetch TA outcomes.
    """
    # Mock implementation - returns sample TA outcomes
    today = dt.date.today()
    return {
        "Oncology": [
            (today - dt.timedelta(days=60), 1, 1.0),
            (today - dt.timedelta(days=120), 1, 1.5),
            (today - dt.timedelta(days=200), -1, 1.0),
        ],
        "Cardiovascular": [
            (today - dt.timedelta(days=45), -1, 1.0),
            (today - dt.timedelta(days=150), 1, 1.0),
        ],
        "Neurology": [
            (today - dt.timedelta(days=100), 1, 2.0),
            (today - dt.timedelta(days=250), -1, 1.0),
        ],
        "Rare Disease": [
            (today - dt.timedelta(days=80), 1, 1.0),
        ]
    }


def get_reaction_samples(company: str, ta: str, catal_type: str, direction: str) -> List[float]:
    """
    Return list of historical next-day (or 3-day) returns for similar events.
    Priority:
      1) same company + catalyst type
      2) same TA + catalyst type
      3) global baseline by catalyst type
    Positive values for "up" samples, negative for "down" samples.
    
    TODO_DB: Implement from your event-price join table.
    """
    # Mock fallback
    if direction == "up":
        return [0.08, 0.12, 0.22, 0.15, 0.10, 0.18, 0.25, 0.14]
    else:
        return [-0.10, -0.20, -0.25, -0.15, -0.12, -0.18, -0.22, -0.16]
