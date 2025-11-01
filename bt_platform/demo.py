#!/usr/bin/env python3
"""
Demo script for BT Platform v2 Prediction API

Shows examples of all major features:
- Timing prediction with hazard spikes
- Outcome prediction with calibration
- Momentum scoring
- Alpha calculation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime as dt
from bt_platform.core.prediction.adapters import get_catalyst_by_id, list_upcoming_catalysts
from bt_platform.core.prediction.timing_predictor_v2 import predict_quarterly_distribution_v2
from bt_platform.core.prediction.outcome_predictor_v2 import predict_outcome_bayesian_v2
from bt_platform.core.prediction.momentum_scorer_v2 import score_company_advanced
from bt_platform.core.prediction.alpha_scorer import expected_alpha_for_catalyst
from bt_platform.core.prediction.calibration import fit_pav, apply_pav

def demo_timing():
    """Demonstrate timing prediction"""
    print("\n" + "="*70)
    print("TIMING PREDICTION DEMO")
    print("="*70)
    
    catalyst = get_catalyst_by_id("DEMO-001")
    
    # Basic timing prediction
    print(f"\n1. Basic Timing for {catalyst.company} ({catalyst.phase} {catalyst.catalyst_type})")
    timing = predict_quarterly_distribution_v2(catalyst)
    print(f"   Quarterly probabilities: {timing['quarterly_probabilities']}")
    print(f"   Outside window: {timing['outside_window']}")
    
    # With hazard spikes (e.g., ASCO conference)
    print(f"\n2. Timing with Hazard Spikes (ASCO week boost)")
    hazards = [
        (dt.date(2025, 6, 1), dt.date(2025, 6, 15), 1.3)  # 30% boost during ASCO
    ]
    timing_hazard = predict_quarterly_distribution_v2(catalyst, hazard_windows=hazards)
    print(f"   Quarterly probabilities: {timing_hazard['quarterly_probabilities']}")
    print(f"   Reference: {timing_hazard['reference']}")

def demo_outcome():
    """Demonstrate outcome prediction"""
    print("\n" + "="*70)
    print("OUTCOME PREDICTION DEMO")
    print("="*70)
    
    catalyst = get_catalyst_by_id("DEMO-001")
    
    # Without calibration
    print(f"\n1. Raw Bayesian Prediction for {catalyst.company}")
    outcome = predict_outcome_bayesian_v2(catalyst)
    print(f"   Prior: {outcome.prior_probability}")
    print(f"   Posterior: {outcome.probability_of_success}")
    print(f"   Evidence factors:")
    for factor in outcome.evidence_factors:
        print(f"     - {factor['factor']}: {factor['impact']}")
    
    # With calibration
    print(f"\n2. Calibrated Prediction")
    # Mock calibration data
    p_train = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    y_train = [0, 0, 0, 1, 1, 1, 1]
    calibrator = fit_pav(p_train, y_train)
    
    outcome_cal = predict_outcome_bayesian_v2(catalyst, pav_calibrator=calibrator)
    print(f"   Raw probability: {outcome.probability_of_success}")
    print(f"   Calibrated probability: {outcome_cal.probability_of_success}")
    print(f"   Calibrated: {outcome_cal.calibrated}")

def demo_momentum():
    """Demonstrate momentum scoring"""
    print("\n" + "="*70)
    print("MOMENTUM SCORING DEMO")
    print("="*70)
    
    print(f"\n1. Company Momentum (peer-neutral with streak)")
    companies = ["Example Biotech", "Biotech Company 0", "Biotech Company 1"]
    for company in companies:
        score = score_company_advanced(company)
        print(f"   {company}:")
        print(f"     Score: {score['momentum_score']}/100")
        print(f"     Components: base={score['components']['base']:.3f}, "
              f"streak={score['components']['streak']:.1f}, "
              f"ta_z={score['components']['ta_z']:.3f}")

def demo_alpha():
    """Demonstrate alpha scoring"""
    print("\n" + "="*70)
    print("ALPHA SCORING DEMO")
    print("="*70)
    
    print(f"\n1. Expected Alpha Calculation")
    catalysts = list_upcoming_catalysts(limit=5)
    
    results = []
    for c in catalysts:
        alpha = expected_alpha_for_catalyst(c)
        results.append(alpha)
    
    # Sort by edge score
    results.sort(key=lambda x: x['edge_score'], reverse=True)
    
    print(f"\nTop 3 Catalysts by Edge Score:")
    for i, alpha in enumerate(results[:3], 1):
        print(f"\n   {i}. {alpha['company']} ({alpha['ticker']})")
        print(f"      Edge Score: {alpha['edge_score']}/100")
        print(f"      Expected Value: {alpha['ev']:.2%}")
        print(f"      P(success): {alpha['prob_success']:.1%}")
        print(f"      Expected moves: +{alpha['mu_up']:.1%} / -{alpha['mu_down']:.1%}")
        print(f"      Timing confidence: {alpha['timing_confidence']:.1%}")

def demo_full_workflow():
    """Demonstrate complete workflow for a single catalyst"""
    print("\n" + "="*70)
    print("COMPLETE WORKFLOW DEMO")
    print("="*70)
    
    catalyst = get_catalyst_by_id("DEMO-001")
    
    print(f"\nAnalyzing: {catalyst.company} ({catalyst.ticker})")
    print(f"Type: {catalyst.catalyst_type} - {catalyst.phase}")
    print(f"Therapeutic Area: {catalyst.therapeutic_area}")
    
    # Timing
    timing = predict_quarterly_distribution_v2(catalyst)
    print(f"\n📅 Timing:")
    for i, (prob, (start, end)) in enumerate(zip(timing['quarterly_probabilities'], timing['bins']), 1):
        print(f"   Q{i} ({start} to {end}): {prob:.1%}")
    
    # Outcome
    outcome = predict_outcome_bayesian_v2(catalyst)
    print(f"\n🎯 Outcome:")
    print(f"   Success Probability: {outcome.probability_of_success:.1%}")
    print(f"   Evidence: {', '.join([f['factor'] for f in outcome.evidence_factors])}")
    
    # Momentum
    momentum = score_company_advanced(catalyst.company)
    print(f"\n📈 Momentum:")
    print(f"   Score: {momentum['momentum_score']}/100")
    
    # Alpha
    alpha = expected_alpha_for_catalyst(catalyst)
    print(f"\n💰 Alpha:")
    print(f"   Edge Score: {alpha['edge_score']:.1f}/100")
    print(f"   Expected Value: {alpha['ev']:.2%}")
    print(f"   Risk/Reward: +{alpha['mu_up']:.1%} upside vs -{alpha['mu_down']:.1%} downside")

def main():
    """Run all demos"""
    print("\n" + "="*70)
    print(" BT PLATFORM v2 - PREDICTION API DEMONSTRATION")
    print("="*70)
    print("\nThis demo showcases the v2 prediction models:")
    print("  • Timing: Weibull distributions with hazard spikes")
    print("  • Outcome: Bayesian inference with PAV calibration")
    print("  • Momentum: Peer-neutral scoring with streak detection")
    print("  • Alpha: Expected value with downside risk penalty")
    
    try:
        demo_timing()
        demo_outcome()
        demo_momentum()
        demo_alpha()
        demo_full_workflow()
        
        print("\n" + "="*70)
        print(" DEMO COMPLETE")
        print("="*70)
        print("\nNext steps:")
        print("  1. Start API server: python3 bt_platform/endpoints/predictions_v2.py")
        print("  2. Test endpoints: curl http://localhost:8081/v2/alpha/top?limit=5")
        print("  3. Implement adapter TODOs in bt_platform/core/prediction/adapters.py")
        print("  4. Calibrate models with historical data")
        print("\nSee bt_platform/README.md for full documentation.")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
