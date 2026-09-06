"""Image Quality Module — real OpenCV checks. Tune thresholds with real
phone photos before the demo."""
import cv2
import numpy as np

BLUR_THRESHOLD = 60.0
BRIGHT_MIN, BRIGHT_MAX = 40, 220
GLARE_RATIO_MAX = 0.15


def check_quality(image_bytes: bytes) -> dict:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return {"accepted": False, "retake_requested": True,
                "reason": "Image could not be decoded (corrupted upload)",
                "metrics": {}}

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness = float(np.mean(gray))
    glare = float(np.count_nonzero(gray > 245) / gray.size)

    metrics = {"blur_score": round(blur, 2), "brightness": round(brightness, 2),
               "glare_ratio": round(glare, 3)}

    if blur < BLUR_THRESHOLD:
        return {"accepted": False, "retake_requested": True,
                "reason": "Image too blurry — hold steady and refocus", "metrics": metrics}
    if not (BRIGHT_MIN <= brightness <= BRIGHT_MAX):
        return {"accepted": False, "retake_requested": True,
                "reason": "Poor lighting — too dark or overexposed", "metrics": metrics}
    if glare > GLARE_RATIO_MAX:
        return {"accepted": False, "retake_requested": True,
                "reason": "Excessive glare over declaration region", "metrics": metrics}

    return {"accepted": True, "retake_requested": False, "reason": None, "metrics": metrics}