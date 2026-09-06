import re
from typing import Dict, Optional
from ..models.schemas import DeclarationItem


def extract_declarations(text: str, panel_type: Optional[str] = None) -> Dict[str, DeclarationItem]:
    """
    Extracts Legal Metrology mandatory declarations using pattern matchers.
    """
    declarations: Dict[str, DeclarationItem] = {}

    # 1. Net Quantity (e.g., "Net Wt: 500 g", "Net Quantity: 1 kg", "500ml", "1.5 L")
    net_qty_match = re.search(
        r"(?:net\s*(?:wt|weight|qty|quantity)?[:\s\-]*)?(\d+(?:\.\d+)?)\s*(g|gm|gms|kg|ml|l|ltr|litres?)\b",
        text,
        re.IGNORECASE,
    )
    if net_qty_match:
        val_str, unit_raw = net_qty_match.groups()
        unit_norm = unit_raw.lower()
        if unit_norm in ["gm", "gms"]:
            unit_norm = "g"
        elif unit_norm in ["ltr", "litres", "litre"]:
            unit_norm = "l"

        declarations["net_quantity"] = DeclarationItem(
            raw_text=net_qty_match.group(0).strip(),
            normalized_value=float(val_str),
            unit=unit_norm,
            confidence=0.92,
            panel_type=panel_type,
        )

    # 2. Maximum Retail Price (MRP)
    mrp_match = re.search(
        r"(?:m\.?r\.?p\.?|max(?:imum)?\s*retail\s*price)[:\s\.\-]*([₹Rs\.]*\s*[\d,]+(?:\.\d{2})?)",
        text,
        re.IGNORECASE,
    )
    if mrp_match:
        price_str = re.sub(r"[^\d.]", "", mrp_match.group(1))
        has_tax_clause = bool(re.search(r"incl(?:usive)?\s*(?:of)?\s*all\s*taxes", text, re.IGNORECASE))
        declarations["mrp"] = DeclarationItem(
            raw_text=mrp_match.group(0).strip(),
            normalized_value=float(price_str) if price_str else None,
            unit="INR",
            confidence=0.95 if has_tax_clause else 0.75,
            panel_type=panel_type,
        )

    # 3. Date of Manufacture / Packing (e.g., "Mfg Date: 05/2026", "Pkd: Jun 2026")
    mfg_match = re.search(
        r"(?:mfd|mfg|pkd|packed|manufactured)[\s\.\:\-]*((?:\d{1,2}[\/\-\.]\d{2,4})|(?:[A-Za-z]{3,9}\s*\d{2,4}))",
        text,
        re.IGNORECASE,
    )
    if mfg_match:
        declarations["mfg_date"] = DeclarationItem(
            raw_text=mfg_match.group(0).strip(),
            normalized_value=mfg_match.group(1).strip(),
            confidence=0.88,
            panel_type=panel_type,
        )

    # 4. Best Before / Expiry (e.g., "Best before 12 months from manufacture", "Expiry: 12/2027")
    expiry_match = re.search(
        r"(?:best\s*before|use\s*by|exp(?:iry)?\s*date?)[\s\.\:\-]*([^\n\r]+)",
        text,
        re.IGNORECASE,
    )
    if expiry_match:
        declarations["expiry_date"] = DeclarationItem(
            raw_text=expiry_match.group(0).strip(),
            normalized_value=expiry_match.group(1).strip(),
            confidence=0.85,
            panel_type=panel_type,
        )

    # 5. Manufacturer / Packer Details
    mfg_details_match = re.search(
        r"(?:manufactured\s*by|mfg\s*by|marketed\s*by|packed\s*by)[\s\.\:\-]+([^\n\r]+(?:\n[^\n\r]+)?)",
        text,
        re.IGNORECASE,
    )
    if mfg_details_match:
        declarations["manufacturer_details"] = DeclarationItem(
            raw_text=mfg_details_match.group(0).strip(),
            normalized_value=mfg_details_match.group(1).strip(),
            confidence=0.80,
            panel_type=panel_type,
        )

    # 6. Consumer Care / Grievance Details
    care_match = re.search(
        r"(?:consumer\s*care|customer\s*care|feedback|grievance|helpline)[\s\.\:\-]+([^\n\r]+)",
        text,
        re.IGNORECASE,
    )
    if care_match:
        declarations["consumer_care"] = DeclarationItem(
            raw_text=care_match.group(0).strip(),
            normalized_value=care_match.group(1).strip(),
            confidence=0.82,
            panel_type=panel_type,
        )

    # 7. Country of Origin
    origin_match = re.search(
        r"(?:country\s*of\s*origin|made\s*in|product\s*of)[\s\.\:\-]+([A-Za-z\s]+)",
        text,
        re.IGNORECASE,
    )
    if origin_match:
        declarations["country_of_origin"] = DeclarationItem(
            raw_text=origin_match.group(0).strip(),
            normalized_value=origin_match.group(1).strip(),
            confidence=0.90,
            panel_type=panel_type,
        )

    return declarations
