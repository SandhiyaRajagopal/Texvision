from typing import List, Dict, Any

def calculate_quality_score(defects: List[Dict[str, Any]]) -> float:
    if not defects:
        return 100.0
    
    # Base score
    score = 100.0
    
    # Severity deductions
    severity_deductions = {"Minor": 2.0, "Moderate": 10.0, "Critical": 30.0}
    
    for defect in defects:
        sev = defect.get("severity", "Minor")
        score -= severity_deductions.get(sev, 0.0)
    
    # Count deduction
    score -= len(defects) * 1.5
    
    return max(0.0, min(100.0, round(score, 2)))

def determine_final_verdict(quality_score: float, defects: List[Dict[str, Any]]) -> str:
    critical_count = sum(1 for d in defects if d.get("severity") == "Critical")
    
    if critical_count > 1 or quality_score < 40.0:
        return "REJECT"
    elif critical_count == 1 or quality_score < 85.0:
        return "REWORK"
    else:
        return "PASS"
