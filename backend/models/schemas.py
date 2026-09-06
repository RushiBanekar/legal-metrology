"""Pydantic models — keep in sync with API_CONTRACT.md."""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ViewType(str, Enum):
    FRONT = "FRONT"
    BACK = "BACK"
    LEFT_SIDE = "LEFT_SIDE"
    RIGHT_SIDE = "RIGHT_SIDE"
    TOP = "TOP"
    BOTTOM = "BOTTOM"
    CLOSE_UP = "CLOSE_UP"
    OTHER = "OTHER"


class Verdict(str, Enum):
    COMPLIANT = "COMPLIANT"
    POTENTIAL_NON_COMPLIANCE = "POTENTIAL_NON_COMPLIANCE"
    INCONCLUSIVE = "INCONCLUSIVE"


class SessionCreateRequest(BaseModel):
    inspector_id: str
    location: str
    category: str = Field(..., description="e.g. PACKAGED_FOOD")
    product_identifier: str