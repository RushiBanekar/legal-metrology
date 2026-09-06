"""Evidence Coverage Engine — merges declaration extraction results across
ALL images in a session into FOUND / UNCLEAR / MISSING / CONFLICT per field.
"""
from .declarations import required_fields_for_category


def build_coverage(category: str, per_image_declarations: dict) -> dict:
    required = required_fields_for_category(category)
    coverage = {}
    sources = {}

    for field in required:
        found_values = []
        any_unclear = False
        for image_id, decls in per_image_declarations.items():
            entry = decls.get(field, {"value": None, "state": "MISSING"})
            if entry["state"] == "FOUND" and entry["value"]:
                found_values.append((image_id, entry["value"]))
            elif entry["state"] == "UNCLEAR":
                any_unclear = True

        distinct_values = {v for _, v in found_values}

        if len(distinct_values) > 1:
            coverage[field] = "CONFLICT"
            sources[field] = {
                "competing_values": [{"image_id": i, "value": v} for i, v in found_values],
                "selection_reason": "CONFLICT_REQUIRES_REVIEW — values disagree across images",
            }
        elif len(distinct_values) == 1:
            image_id, value = found_values[0]
            coverage[field] = "FOUND"
            sources[field] = {"selected_value": value, "source_image": image_id,
                               "selection_reason": "Only consistent value found"}
        elif any_unclear:
            coverage[field] = "UNCLEAR"
            sources[field] = {"selection_reason": "Low OCR confidence on all candidate images"}
        else:
            coverage[field] = "MISSING"
            sources[field] = {"selection_reason": "Not detected in any session image"}

    return {"coverage": coverage, "sources": sources}


RECOMMENDED_VIEW = {
    "MFG_DATE": "BACK",
    "COUNTRY_OF_ORIGIN": "BACK",
    "MRP": "FRONT",
    "NET_QUANTITY": "FRONT",
    "MANUFACTURER": "BACK",
}


def missing_evidence_list(coverage: dict) -> list:
    out = []
    for field, status in coverage.items():
        if status in ("MISSING", "UNCLEAR"):
            out.append({
                "field": field,
                "recommended_view": RECOMMENDED_VIEW.get(field, "OTHER"),
                "tip": "Move closer, hold steady, avoid glare",
            })
    return out