"""Physical Measurement + Uncertainty. Never guess a physical value — if no
reliable calibration reference exists, report INCONCLUSIVE.
"""
BASE_UNCERTAINTY_MM = 0.08


def measure_with_reference(reference_width_mm: float, reference_width_px: int,
                            target_height_px: int) -> dict:
    if reference_width_px <= 0:
        return {"status": "INCONCLUSIVE", "reason": "Invalid reference bounding box"}

    px_to_mm = reference_width_mm / reference_width_px
    value_mm = round(target_height_px * px_to_mm, 2)

    return {
        "field": "TARGET_HEIGHT_MM",
        "value": value_mm,
        "uncertainty": BASE_UNCERTAINTY_MM,
        "unit": "mm",
        "calibration": "VALID",
        "confidence": "HIGH" if BASE_UNCERTAINTY_MM < 0.1 else "MEDIUM",
    }


def measure_without_reference() -> dict:
    return {
        "status": "INCONCLUSIVE",
        "reason": "No reliable calibration reference found. Capture a photo "
                  "with a known reference (ruler/calibration card) alongside "
                  "the declaration to enable measurement.",
    }


def evaluate_against_threshold(value_mm: float, uncertainty_mm: float, threshold_mm: float) -> str:
    low, high = value_mm - uncertainty_mm, value_mm + uncertainty_mm
    if low > threshold_mm:
        return "COMPLIANT"
    if high < threshold_mm:
        return "POTENTIAL_NON_COMPLIANCE"
    return "INCONCLUSIVE"