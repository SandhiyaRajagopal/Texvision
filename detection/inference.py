import cv2
import numpy as np
from ultralytics import YOLO
from config.settings import MODEL_PATH, DEFECT_CLASSES, DEFECT_CLASS_MAP
import utils.logger as log_utils

logger = log_utils.setup_logger("detection")

# Color map per class
CLASS_COLORS = {
    "Hole":  (0, 0, 255),    # Red
    "Stain": (0, 165, 255),  # Orange
    "Knot":  (0, 255, 255),  # Yellow
    "Line":  (255, 0, 255),  # Magenta
}

class DefectDetector:
    def __init__(self):
        self.model = None
        try:
            logger.info(f"Loading model: {MODEL_PATH}")
            # Ultralytics automatically uses ONNX Runtime with CUDA if onnxruntime-gpu is installed
            self.model = YOLO(MODEL_PATH, task="detect")
            logger.info(f"Model loaded. Classes: {self.model.names}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None

    def predict(self, image_path: str, conf_threshold: float = 0.25):
        if not self.model:
            raise RuntimeError("Model is not loaded.")
        # device=0 forces CUDA GPU inference
        results = self.model(
            image_path,
            conf=conf_threshold,
            device=0,        # NVIDIA GPU
            verbose=False
        )
        return results

    def process_results(self, results):
        defects = []
        for result in results:
            if result.boxes is None:
                continue
            for box in result.boxes:
                cls_id = int(box.cls[0].item())
                raw_name = result.names.get(cls_id, "Unknown")
                # Map to canonical class
                class_name = DEFECT_CLASS_MAP.get(raw_name, raw_name)
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].tolist()
                defects.append({
                    "class_name": class_name,
                    "raw_class":  raw_name,
                    "confidence": round(conf, 3),
                    "box": xyxy
                })
        return defects

    def fallback_detect(self, image_path: str, conf_threshold: float):
        """LAB color-space anomaly detection fallback when model misses defects."""
        img = cv2.imread(image_path)
        if img is None:
            return []

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)

        median_a = np.median(a)
        median_b = np.median(b)

        dist = np.sqrt(
            np.square(a.astype(float) - median_a) +
            np.square(b.astype(float) - median_b)
        )
        max_dist = np.max(dist)
        if max_dist == 0:
            return []

        dist = np.uint8(255 * dist / max_dist)
        dist = cv2.GaussianBlur(dist, (15, 15), 0)
        _, binary = cv2.threshold(dist, 50, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        defects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 100:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            # Skip whole-image false positives
            if w > img.shape[1] * 0.9 or h > img.shape[0] * 0.9:
                continue
            conf = min(0.99, round(0.5 + (area / 10000.0), 2))
            if conf >= conf_threshold:
                defects.append({
                    "class_name": "Stain",
                    "raw_class":  "Stain (CV Fallback)",
                    "confidence": conf,
                    "box": [float(x), float(y), float(x + w), float(y + h)]
                })
        return defects

    def annotate_image(self, image_path: str, defects: list, output_path: str):
        img = cv2.imread(image_path)
        if img is None:
            logger.error(f"Could not read image: {image_path}")
            return None

        for defect in defects:
            x1, y1, x2, y2 = map(int, defect["box"])
            label = f"{defect['class_name']} {defect['confidence']:.2f}"
            color = CLASS_COLORS.get(defect["class_name"], (0, 255, 0))

            # Bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Label background
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
            cv2.rectangle(img, (x1, y1 - th - 8), (x1 + tw + 4, y1), color, -1)
            cv2.putText(img, label, (x1 + 2, y1 - 4),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

        cv2.imwrite(output_path, img)
        return output_path
