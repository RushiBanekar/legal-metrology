"""OCR wrapper — prototype engine: PaddleOCR 3.x.

Sorts detected text top-to-bottom, left-to-right by bounding box position
so declaration extraction sees text in roughly reading order — raw
PaddleOCR order is not guaranteed to match how a human reads the label.
"""
import cv2
import numpy as np
from paddleocr import PaddleOCR

_ocr_engine = PaddleOCR(
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang="en",
    enable_mkldnn=False,
)


def run_ocr(image_bytes: bytes) -> dict:
    arr = np.frombuffer(image_bytes, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)

    results = _ocr_engine.predict(img)

    items = []  # (y, x, text, confidence)
    for res in results:
        texts = res.get("rec_texts", []) if isinstance(res, dict) else getattr(res, "rec_texts", [])
        scores = res.get("rec_scores", []) if isinstance(res, dict) else getattr(res, "rec_scores", [])
        polys = res.get("rec_polys", []) if isinstance(res, dict) else getattr(res, "rec_polys", [])

        for i, text in enumerate(texts):
            if not text or not text.strip():
                continue
            score = scores[i] if i < len(scores) else 0.0
            if i < len(polys):
                poly = polys[i]
                y = float(min(p[1] for p in poly))
                x = float(min(p[0] for p in poly))
            else:
                y, x = 0.0, 0.0
            items.append((y, x, text, score))

    # Sort top-to-bottom (rounded to bucket nearby lines), then left-to-right
    items.sort(key=lambda t: (round(t[0] / 15), t[1]))

    words = [t[2] for t in items]
    confidences = [t[3] * 100 for t in items]

    full_text = " ".join(words)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    if not words:
        state = "NOT_DETECTED"
    elif avg_conf < 50:
        state = "UNCLEAR"
    else:
        state = "DETECTED"

    return {"state": state, "text": full_text, "avg_confidence": round(avg_conf, 1)}