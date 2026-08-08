import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
DATABASE_DIR = BASE_DIR / "database"
LOG_DIR = BASE_DIR / "logs"
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
REPORTS_DIR = OUTPUT_DIR / "reports"

# Ensure directories exist
for directory in [MODELS_DIR, DATABASE_DIR, LOG_DIR, UPLOAD_DIR, OUTPUT_DIR, REPORTS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_DIR}/inspection.db")

# Model Paths - using custom trained ONNX model
MODEL_PATH = os.getenv("MODEL_PATH", str(MODELS_DIR / "best.onnx"))

# Defect Classes - matches the custom trained model
# Model outputs: {0: 'Hole', 1: 'Knot', 2: 'Line', 3: 'Stain'}
DEFECT_CLASSES = ["Hole", "Knot", "Line", "Stain"]

# For severity/suggestion mapping, group these:
DEFECT_CLASS_MAP = {
    "Hole": "Hole",
    "Knot": "Tear",   # treat knot similar to tear
    "Line": "Tear",   # treat line similar to tear
    "Stain": "Stain"
}

# Severity Thresholds (Area in cm^2)
SEVERITY_THRESHOLDS = {
    "Hole": {"Minor": 2.0, "Moderate": 10.0, "Critical": 1000.0},
    "Tear": {"Minor": 5.0, "Moderate": 15.0, "Critical": 1000.0},
    "Stain": {"Minor": 10.0, "Moderate": 30.0, "Critical": 1000.0}
}

# Quality Score Weights
WEIGHT_SEVERITY = 0.4
WEIGHT_COUNT = 0.3
WEIGHT_DENSITY = 0.3

# Calibration (pixels to cm) - Dummy value for now
PIXEL_TO_CM_RATIO = 0.05
