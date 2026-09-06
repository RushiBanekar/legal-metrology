"""Versioned Rule Engine — deterministic, no LLM in the compliance decision
path. Rules live as structured JSON so historical findings stay reproducible.
"""
import json
from pathlib import Path

# services/rules_engine.py -> backend/ -> legal-metrology/ -> rules/categories/
RULES_DIR = Path(__file__).resolve().parents[2] / "rules" / "categories"


def load_rules(category: str) -> dict:
    path = RULES_DIR / f"{category.lower()}.json"
    if not path.exists():
        return {"version": None, "rules": []}
    with open(path, "r") as f:
        return json.load(f)


def evaluate_rules(category: str, coverage: dict, measurements: list) -> dict:
    ruleset = load_rules(category)
    findings = []
    has_conflict = any(v == "CONFLICT" for v in coverage.values())
    has_missing = any(v in ("MISSING", "UNCLEAR") for v in coverage.values())
    has_non_compliance = False

    for rule in ruleset.get("rules", []):
        field = rule["evidence_required"]
        status_for_field = coverage.get(field, "NOT_APPLICABLE")

        if status_for_field == "NOT_APPLICABLE":
            continue
        if status_for_field in ("MISSING", "UNCLEAR", "CONFLICT"):
            findings.append({
                "rule_id": rule["rule_id"],
                "requirement": rule["requirement"],
                "status": "INCONCLUSIVE",
                "evidence_image_id": "",
                "explanation": f"Evidence for {field} is {status_for_field.lower()}.",
            })
            continue

        threshold_field = rule.get("threshold_field")
        if threshold_field:
            m = next((m for m in measurements if m.get("field") == threshold_field), None)
            if m is None or m.get("status") == "INCONCLUSIVE":
                findings.append({
                    "rule_id": rule["rule_id"], "requirement": rule["requirement"],
                    "status": "INCONCLUSIVE", "evidence_image_id": "",
                    "explanation": "No valid measurement available for this requirement.",
                })
                continue
            from .measurement import evaluate_against_threshold
            result = evaluate_against_threshold(m["value"], m["uncertainty"], rule["threshold"])
            if result == "POTENTIAL_NON_COMPLIANCE":
                has_non_compliance = True
            findings.append({
                "rule_id": rule["rule_id"], "requirement": rule["requirement"],
                "status": result, "evidence_image_id": "",
                "explanation": f"Measured {m['value']}±{m['uncertainty']}{m['unit']} vs threshold {rule['threshold']}{m['unit']}.",
            })
        else:
            findings.append({
                "rule_id": rule["rule_id"], "requirement": rule["requirement"],
                "status": "COMPLIANT", "evidence_image_id": "",
                "explanation": f"{field} declaration found and present.",
            })

    if has_conflict or has_missing:
        verdict, reason = "INCONCLUSIVE", "One or more required declarations are missing, unclear, or conflicting."
    elif has_non_compliance:
        verdict, reason = "POTENTIAL_NON_COMPLIANCE", "At least one requirement appears violated based on available evidence."
    elif findings:
        verdict, reason = "COMPLIANT", "All applicable requirements satisfied by available evidence."
    else:
        verdict, reason = "INCONCLUSIVE", "No applicable rules were evaluated."

    return {
        "rule_version": ruleset.get("version", "UNVERSIONED"),
        "findings": findings,
        "verdict": verdict,
        "verdict_reason": reason,
    }