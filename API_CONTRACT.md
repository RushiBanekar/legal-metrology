# API Contract - Legal Metrology Verification System

> **Status**: Frozen (v1.0.0)  
> **Base URL**: `http://localhost:8000/api/v1`

---

## 1. Overview & Core Endpoints

The backend provides 4 core REST endpoints designed to support the complete lifecycle of a Legal Metrology inspection session:

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/sessions` | Initialize a new inspection session |
| `POST` | `/sessions/{session_id}/upload` | Upload panel/side image, perform quality check & OCR |
| `POST` | `/sessions/{session_id}/evaluate` | Run deterministic rules engine & produce compliance verdict |
| `GET` | `/sessions/{session_id}` | Retrieve full session state, coverage summary, and verdict |
| `GET` | `/sessions` | List inspection sessions with pagination & filtering |

---

## 2. Endpoint Specifications

### 2.1. Create Session
- **`POST /sessions`**
- **Request Body**:
```json
{
  "category": "packaged_food",
  "rule_version": "1.0.0",
  "metadata": {
    "inspector_id": "INSP-402",
    "location": "Warehouse-East",
    "product_name_hint": "Whole Grain Oats"
  }
}
```
- **Response `201 Created`**:
```json
{
  "session_id": "sess_89f13c6a-4d2b-4e6f-8703-b1d9fa490c01",
  "category": "packaged_food",
  "rule_version": "1.0.0",
  "status": "in_progress",
  "created_at": "2026-09-06T10:30:00Z",
  "images": [],
  "declarations": {},
  "coverage": {
    "total_required_fields": 8,
    "detected_fields": 0,
    "coverage_percentage": 0.0
  }
}
```

---

### 2.2. Upload & Process Image
- **`POST /sessions/{session_id}/upload`**
- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: Image binary (JPEG / PNG / WebP)
  - `panel_type`: String enum (`front`, `back`, `top`, `bottom`, `left`, `right`, `general`)
  - `reference_dimension_mm`: (Optional) Known reference width/height for calibration
- **Response `200 OK`**:
```json
{
  "image_id": "img_5a17e0b2",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "panel_type": "front",
  "quality": {
    "is_acceptable": true,
    "blur_score": 142.5,
    "brightness_score": 0.68,
    "glare_detected": false,
    "rejection_reasons": []
  },
  "extracted_text": "Net Weight: 500 g\nMRP Rs. 150.00...",
  "extracted_declarations": {
    "net_quantity": {
      "value": "500",
      "unit": "g",
      "confidence": 0.96,
      "bounding_box": [120, 340, 260, 380]
    },
    "mrp": {
      "value": 150.00,
      "currency": "INR",
      "confidence": 0.94,
      "bounding_box": [130, 400, 280, 440]
    }
  }
}
```

---

### 2.3. Evaluate Compliance
- **`POST /sessions/{session_id}/evaluate`**
- **Response `200 OK`**:
```json
{
  "session_id": "sess_89f13c6a-4d2b-4e6f-8703-b1d9fa490c01",
  "verdict": "NON_COMPLIANT",
  "summary": {
    "total_rules": 9,
    "passed_rules": 7,
    "failed_rules": 2,
    "warning_rules": 0
  },
  "rule_results": [
    {
      "rule_id": "REQ_NET_QUANTITY",
      "rule_name": "Net Quantity Declaration",
      "status": "PASS",
      "evidence": "500 g on front panel",
      "details": "Quantity format conforms to Schedule II"
    },
    {
      "rule_id": "REQ_FONT_SIZE_MIN",
      "rule_name": "Minimum Principal Display Font Size",
      "status": "FAIL",
      "evidence": "Font height measured at 1.8mm (required: >= 2.0mm for net weight <= 500g)",
      "details": "Calculated height 1.80mm (+/- 0.15mm)"
    }
  ],
  "audit_hash": "7a35e89a2b531...sha256_of_entire_verdict_bundle",
  "evaluated_at": "2026-09-06T10:35:00Z"
}
```

---

### 2.4. Get Session Details
- **`GET /sessions/{session_id}`**
- **Response `200 OK`**: Returns full session object with image evidence, parsed declarations, rule evaluations, and audit trail.

---

## 3. Standard Error Format

All 4xx/5xx responses adhere to this structure:
```json
{
  "detail": {
    "error_code": "INVALID_IMAGE_QUALITY",
    "message": "Image failed quality check due to severe motion blur.",
    "field": "file",
    "details": {
      "blur_score": 38.2,
      "min_threshold": 80.0
    }
  }
}
```
