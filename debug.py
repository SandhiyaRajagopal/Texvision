import cv2
import sys
import numpy as np

img_path = "C:\\Users\\admin\\.gemini\\antigravity\\scratch\\project\\uploads\\temp_77bfac65b4a44cb39d56a00fb9a85b5d.jpg"
img = cv2.imread(img_path)
if img is None:
    print("Could not read image")
    sys.exit()

lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
l, a, b = cv2.split(lab)

median_a = np.median(a)
median_b = np.median(b)

dist = np.sqrt(np.square(a.astype(float) - median_a) + np.square(b.astype(float) - median_b))
dist = np.uint8(255 * dist / np.max(dist))

# Smooth the distance map
dist = cv2.GaussianBlur(dist, (15, 15), 0)

_, binary = cv2.threshold(dist, 50, 255, cv2.THRESH_BINARY)

contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

print(f"Total contours: {len(contours)}")
for c in sorted(contours, key=cv2.contourArea, reverse=True)[:5]:
    area = cv2.contourArea(c)
    x, y, w, h = cv2.boundingRect(c)
    print(f"Area: {area}, BoundingBox: x={x}, y={y}, w={w}, h={h}")
