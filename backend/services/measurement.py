from typing import Dict, Any, Optional


def calculate_font_measurements(
    bbox_height_px: int,
    reference_dimension_px: Optional[float] = None,
    reference_dimension_mm: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Computes calibrated real-world font height (mm) and uncertainty interval.
    If reference dimensions are provided (e.g. coin or card calibration target),
    computes scale factor: px_per_mm.
    """
    if reference_dimension_px and reference_dimension_mm and reference_dimension_mm > 0:
        px_per_mm = reference_dimension_px / reference_dimension_mm
        estimated_height_mm = round(bbox_height_px / px_per_mm, 2)
        # Uncertainty estimation (+/- 5% or pixel quantization error)
        uncertainty_mm = round(max(0.1, 1.0 / px_per_mm), 2)
    else:
        # Default approximation based on standard DPI assumption (e.g., 300 DPI -> ~11.8 px/mm)
        default_px_per_mm = 11.81
        estimated_height_mm = round(bbox_height_px / default_px_per_mm, 2)
        uncertainty_mm = 0.25

    return {
        "estimated_height_mm": estimated_height_mm,
        "uncertainty_mm": uncertainty_mm,
        "lower_bound_mm": round(estimated_height_mm - uncertainty_mm, 2),
        "upper_bound_mm": round(estimated_height_mm + uncertainty_mm, 2),
    }
