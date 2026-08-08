from config.settings import PIXEL_TO_CM_RATIO

def calculate_dimensions(box) -> dict:
    # YOLO box format: [x1, y1, x2, y2]
    x1, y1, x2, y2 = box
    width_px = x2 - x1
    height_px = y2 - y1
    
    width_cm = width_px * PIXEL_TO_CM_RATIO
    height_cm = height_px * PIXEL_TO_CM_RATIO
    area_cm2 = width_cm * height_cm
    
    x_center = x1 + (width_px / 2)
    y_center = y1 + (height_px / 2)
    
    return {
        "width_cm": round(width_cm, 2),
        "height_cm": round(height_cm, 2),
        "area_cm2": round(area_cm2, 2),
        "x_center": round(x_center, 2),
        "y_center": round(y_center, 2)
    }
