def generate_suggestion(defect_type: str, severity: str) -> str:
    if defect_type == "Stain":
        if severity == "Minor":
            return "Chemical Wash"
        elif severity == "Moderate":
            return "Spot Clean and Reprocess"
        else:
            return "Reprocess Fabric"
    elif defect_type == "Hole":
        if severity == "Minor":
            return "Manual Stitching"
        elif severity == "Moderate":
            return "Patch Repair"
        else:
            return "Cut Damaged Section"
    elif defect_type == "Tear":
        if severity == "Minor":
            return "Repair"
        elif severity == "Moderate":
            return "Machine Darn"
        else:
            return "Reject Damaged Section"
    return "Inspect Manually"
