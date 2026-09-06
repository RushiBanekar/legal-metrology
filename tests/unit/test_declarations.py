from backend.services.declarations import extract_declarations


def test_extract_net_quantity():
    sample_text = "Whole Wheat Bread\nNet Weight: 400 g\nStore in cool place"
    decl = extract_declarations(sample_text)
    assert "net_quantity" in decl
    assert decl["net_quantity"].normalized_value == 400.0
    assert decl["net_quantity"].unit == "g"


def test_extract_mrp():
    sample_text = "MRP: Rs. 120.00 (Incl. of all taxes)\nBatch: A102"
    decl = extract_declarations(sample_text)
    assert "mrp" in decl
    assert decl["mrp"].normalized_value == 120.00
    assert decl["mrp"].confidence > 0.8
