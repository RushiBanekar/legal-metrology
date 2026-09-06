from pathlib import Path
from backend.services.rules_engine import RulesEngine
from backend.models.schemas import DeclarationItem


def test_rules_engine_evaluation():
    rules_dir = Path(__file__).resolve().parent.parent.parent / "rules"
    engine = RulesEngine(rules_dir=rules_dir)

    declarations = {
        "commodity_name": DeclarationItem(raw_text="Rolled Oats", normalized_value="Rolled Oats"),
        "net_quantity": DeclarationItem(raw_text="500 g", normalized_value=500.0, unit="g"),
        "mrp": DeclarationItem(raw_text="Rs. 150", normalized_value=150.0, unit="INR"),
    }

    result = engine.evaluate(
        session_id="test_sess_001",
        category="packaged_food",
        declarations=declarations,
    )

    assert result.session_id == "test_sess_001"
    assert result.summary["total_rules"] > 0
    assert result.summary["passed_rules"] == 3
    assert result.verdict == "NON_COMPLIANT"  # Missing other mandatory fields
