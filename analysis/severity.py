from config.settings import SEVERITY_THRESHOLDS

def determine_severity(defect_type: str, area_cm2: float) -> str:
    thresholds = SEVERITY_THRESHOLDS.get(defect_type, SEVERITY_THRESHOLDS["Stain"])
    
    # Need to check in descending order to avoid catching criticals in minor
    if area_cm2 >= thresholds["Critical"]:
        return "Critical"
    elif area_cm2 >= thresholds["Moderate"]:
        return "Moderate"
    else:
        return "Minor"
