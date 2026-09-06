from typing import Dict, List, Any
from ..models.schemas import CoverageStatus, DeclarationItem


def calculate_coverage(
    declarations: Dict[str, DeclarationItem],
    required_rules: List[Dict[str, Any]],
) -> CoverageStatus:
    """
    Computes evidence coverage percentage based on mandatory fields found in session declarations.
    """
    required_fields = [r.get("field") for r in required_rules if r.get("required") and r.get("field")]
    total_required = len(required_fields)

    detected_count = 0
    missing_fields = []

    for field in required_fields:
        if field in declarations and declarations[field].normalized_value is not None:
            detected_count += 1
        else:
            missing_fields.append(field)

    coverage_pct = round((detected_count / total_required * 100.0), 1) if total_required > 0 else 100.0

    return CoverageStatus(
        total_required_fields=total_required,
        detected_fields=detected_count,
        missing_fields=missing_fields,
        coverage_percentage=coverage_pct,
    )
