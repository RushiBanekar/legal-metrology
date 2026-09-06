import io
import numpy as np
from PIL import Image, ImageStat
from ..models.schemas import QualityMetrics


def check_image_quality(image_bytes: bytes) -> QualityMetrics:
    """
    Evaluates image quality for OCR readiness:
    - Blur score using Laplacian variance proxy / high frequency gradients
    - Brightness score based on average pixel luminance
    - Glare detection checking overexposed clipped highlights
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("L")
        img_arr = np.array(img, dtype=np.float32)

        # 1. Blur evaluation using simple gradient variance
        gy, gx = np.gradient(img_arr)
        gnorm = np.sqrt(gx**2 + gy**2)
        blur_score = float(np.var(gnorm))

        # 2. Brightness evaluation (0.0 to 1.0)
        stat = ImageStat.Stat(img)
        brightness_score = float(stat.mean[0] / 255.0)

        # 3. Glare evaluation (% of saturated highlight pixels)
        glare_ratio = float(np.mean(img_arr > 250))
        glare_detected = glare_ratio > 0.08

        rejection_reasons = []
        if blur_score < 15.0:
            rejection_reasons.append("Image is too blurry. Please stabilize camera and refocus.")
        if brightness_score < 0.20:
            rejection_reasons.append("Image is underexposed/too dark. Please increase lighting.")
        elif brightness_score > 0.90:
            rejection_reasons.append("Image is overexposed/too bright.")
        if glare_detected:
            rejection_reasons.append("Excessive reflection or glare detected on package surface.")

        is_acceptable = len(rejection_reasons) == 0

        return QualityMetrics(
            is_acceptable=is_acceptable,
            blur_score=round(blur_score, 2),
            brightness_score=round(brightness_score, 2),
            glare_detected=glare_detected,
            rejection_reasons=rejection_reasons,
        )
    except Exception as e:
        return QualityMetrics(
            is_acceptable=False,
            blur_score=0.0,
            brightness_score=0.0,
            glare_detected=False,
            rejection_reasons=[f"Failed to process image: {str(e)}"],
        )
