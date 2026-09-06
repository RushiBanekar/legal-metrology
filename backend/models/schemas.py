from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class SessionCreateRequest(BaseModel):
    category: str = Field(default="packaged_food", description="Category of rule set to apply")
    rule_version: str = Field(default="1.0.0", description="Rule set version")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Custom inspector or location metadata")


class QualityMetrics(BaseModel):
    is_acceptable: bool
    blur_score: float
    brightness_score: float
    glare_detected: bool
    rejection_reasons: List[str] = Field(default_factory=list)


class DeclarationItem(BaseModel):
    raw_text: str
    normalized_value: Any
    unit: Optional[str] = None
    confidence: float = 1.0
    panel_type: Optional[str] = None
    bounding_box: Optional[List[int]] = None


class ImageUploadResponse(BaseModel):
    image_id: str
    sha256: str
    panel_type: str
    quality: QualityMetrics
    extracted_text: str
    extracted_declarations: Dict[str, DeclarationItem] = Field(default_factory=dict)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)


class CoverageStatus(BaseModel):
    total_required_fields: int = 0
    detected_fields: int = 0
    missing_fields: List[str] = Field(default_factory=list)
    coverage_percentage: float = 0.0


class RuleResult(BaseModel):
    rule_id: str
    rule_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    evidence: Optional[str] = None
    details: Optional[str] = None


class EvaluationResponse(BaseModel):
    session_id: str
    verdict: str  # "COMPLIANT", "NON_COMPLIANT", "INCOMPLETE"
    summary: Dict[str, int]
    rule_results: List[RuleResult] = Field(default_factory=list)
    audit_hash: str
    evaluated_at: datetime = Field(default_factory=datetime.utcnow)


class SessionResponse(BaseModel):
    session_id: str
    category: str
    rule_version: str
    status: str  # "in_progress", "evaluated", "archived"
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)
    images: List[ImageUploadResponse] = Field(default_factory=list)
    declarations: Dict[str, DeclarationItem] = Field(default_factory=dict)
    coverage: CoverageStatus = Field(default_factory=CoverageStatus)
    evaluation: Optional[EvaluationResponse] = None
