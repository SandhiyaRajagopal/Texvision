import pytest
from measurement.calculator import calculate_dimensions
from analysis.severity import determine_severity
from suggestion_engine.rules import generate_suggestion
from decision_engine.scorer import calculate_quality_score, determine_final_verdict

def test_calculate_dimensions():
    # Mock pixel ratio is 0.05
    box = [100, 100, 200, 300] # w=100px, h=200px
    dims = calculate_dimensions(box)
    assert dims['width_cm'] == 5.0
    assert dims['height_cm'] == 10.0
    assert dims['area_cm2'] == 50.0

def test_determine_severity():
    assert determine_severity("Hole", 1.0) == "Minor"
    assert determine_severity("Hole", 15.0) == "Moderate"
    assert determine_severity("Hole", 1500.0) == "Critical"

def test_generate_suggestion():
    assert generate_suggestion("Stain", "Minor") == "Chemical Wash"
    assert generate_suggestion("Tear", "Moderate") == "Machine Darn"

def test_decision_engine():
    defects = [
        {"severity": "Minor"},
        {"severity": "Moderate"}
    ]
    score = calculate_quality_score(defects)
    # Base 100 - (2.0 + 10.0) - (2 * 1.5) = 100 - 12 - 3 = 85.0
    assert score == 85.0
    
    verdict = determine_final_verdict(score, defects)
    assert verdict == "PASS"

    defects_critical = [{"severity": "Critical"}, {"severity": "Critical"}]
    verdict_crit = determine_final_verdict(30.0, defects_critical)
    assert verdict_crit == "REJECT"
