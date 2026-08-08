import os
from detection.inference import DefectDetector

detector = DefectDetector()
img_path = "C:\\Users\\admin\\.gemini\\antigravity\\scratch\\project\\uploads\\temp_77bfac65b4a44cb39d56a00fb9a85b5d.jpg"

print("1. Testing YOLO Predict")
results = detector.predict(img_path, conf_threshold=0.15)
raw_defects = detector.process_results(results)
print(f"YOLO Defects: {len(raw_defects)}")
for d in raw_defects:
    print(d)
    
if not raw_defects:
    print("2. Testing Fallback")
    raw_defects = detector.fallback_detect(img_path, 0.15)
    print(f"Fallback Defects: {len(raw_defects)}")
    for d in raw_defects:
        print(d)
