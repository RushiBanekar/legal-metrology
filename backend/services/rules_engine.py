import json
from pathlib import Path
from typing import Dict, Any, List
from ..models.schemas import RuleResult, EvaluationResponse, DeclarationItem
from .evidence import generate_audit_hash


class RulesEngine:
    def __init__(self, rules_dir: Path):
        self.rules_dir = rules_dir
        self.rules_cache: Dict[str, Dict[str, Any]] = {}

    def load_category_rules(self, category: str) -> Dict[str, Any]:
        """Loads and caches category JSON rule set."""
        if category in self.rules_cache:
            return self.rules_cache[category]

        rule_path = self.rules_dir / "categories" / f"{category}.json"
        if not rule_path.exists():
            raise FileNotFoundError(f"Rule definition not found for category: {category}")

        with open(rule_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.rules_cache[category] = data
            return data

    def evaluate(
        self,
        session_id: str,
        category: str,
        declarations: Dict[str, DeclarationItem],
    ) -> EvaluationResponse:
        """
        Executes deterministic rules evaluation against extracted declarations.
        """
        rule_set = self.load_category_rules(category)
        mandatory_declarations = rule_set.get("mandatory_declarations", [])

        rule_results: List[RuleResult] = []
        passed_count = 0
        failed_count = 0
        warning_count = 0

        for rule in mandatory_declarations:
            field = rule.get("field")
            rule_id = rule.get("id", "UNKNOWN_RULE")
            rule_name = rule.get("name", "Unnamed Rule")
            severity = rule.get("severity", "MEDIUM")

            if field in declarations and declarations[field].normalized_value is not None:
                item = declarations[field]
                status = "PASS"
                evidence = f"Detected: {item.raw_text}"
                details = f"Confidence: {item.confidence * 100:.0f}% on panel: {item.panel_type or 'unspecified'}"
                passed_count += 1
            else:
                status = "FAIL"
                evidence = "Declaration not detected across captured panels"
                details = rule.get("description", "Missing mandatory declaration.")
                failed_count += 1

            rule_results.append(
                RuleResult(
                    rule_id=rule_id,
                    rule_name=rule_name,
                    status=status,
                    severity=severity,
                    evidence=evidence,
                    details=details,
                )
            )

        verdict = "COMPLIANT" if failed_count == 0 else "NON_COMPLIANT"
        summary = {
            "total_rules": len(mandatory_declarations),
            "passed_rules": passed_count,
            "failed_rules": failed_count,
            "warning_rules": warning_count,
        }

        audit_payload = {
            "session_id": session_id,
            "category": category,
            "verdict": verdict,
            "summary": summary,
            "rule_results": [r.model_dump() for r in rule_results],
        }
        audit_hash = generate_audit_hash(audit_payload)

        return EvaluationResponse(
            session_id=session_id,
            verdict=verdict,
            summary=summary,
            rule_results=rule_results,
            audit_hash=audit_hash,
        )
