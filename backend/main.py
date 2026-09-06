import uuid
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .models.schemas import (
    SessionCreateRequest,
    SessionResponse,
    ImageUploadResponse,
    EvaluationResponse,
)
from .services import (
    check_image_quality,
    extract_text_from_image,
    extract_declarations,
    calculate_coverage,
    RulesEngine,
    generate_sha256_hash,
)
from .storage import get_db

app = FastAPI(
    title="Legal Metrology Compliance API",
    version="1.0.0",
    description="Automated compliance verification engine for Legal Metrology Packaged Commodities standards.",
)

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
RULES_DIR = BASE_DIR / "rules"
DATA_DIR = BASE_DIR / "data" / "sessions.json"

db = get_db(persistence_path=DATA_DIR)
rules_engine = RulesEngine(rules_dir=RULES_DIR)


@app.get("/")
def root():
    return {
        "service": "Legal Metrology Compliance API",
        "version": "1.0.0",
        "docs_url": "/docs",
    }


# 1. Create Session
@app.post("/api/v1/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(request: SessionCreateRequest):
    session_id = f"sess_{uuid.uuid4()}"
    session = db.create_session(session_id=session_id, request=request)
    return session


# 2. Upload and Process Image
@app.post("/api/v1/sessions/{session_id}/upload", response_model=ImageUploadResponse)
async def upload_panel_image(
    session_id: str,
    file: UploadFile = File(...),
    panel_type: str = Form("general"),
):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": f"Session {session_id} not found"},
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMPTY_FILE", "message": "Uploaded file is empty"},
        )

    # 1. Evidence hash
    img_sha256 = generate_sha256_hash(file_bytes)
    image_id = f"img_{uuid.uuid4().hex[:8]}"

    # 2. Quality check
    quality = check_image_quality(file_bytes)

    # 3. OCR extraction
    extracted_text = extract_text_from_image(file_bytes)

    # 4. Declarations extraction
    new_declarations = extract_declarations(extracted_text, panel_type=panel_type)

    upload_result = ImageUploadResponse(
        image_id=image_id,
        sha256=img_sha256,
        panel_type=panel_type,
        quality=quality,
        extracted_text=extracted_text,
        extracted_declarations=new_declarations,
    )

    # Merge into session state
    session.images.append(upload_result)
    for field_name, item in new_declarations.items():
        session.declarations[field_name] = item

    # Update coverage
    try:
        rule_data = rules_engine.load_category_rules(session.category)
        req_rules = rule_data.get("mandatory_declarations", [])
        session.coverage = calculate_coverage(session.declarations, req_rules)
    except Exception:
        pass

    db.update_session(session)
    return upload_result


# 3. Evaluate Compliance
@app.post("/api/v1/sessions/{session_id}/evaluate", response_model=EvaluationResponse)
def evaluate_compliance(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": f"Session {session_id} not found"},
        )

    evaluation = rules_engine.evaluate(
        session_id=session.session_id,
        category=session.category,
        declarations=session.declarations,
    )

    session.evaluation = evaluation
    session.status = "evaluated"
    db.update_session(session)

    return evaluation


# 4. Get Session Details
@app.get("/api/v1/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: str):
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error_code": "SESSION_NOT_FOUND", "message": f"Session {session_id} not found"},
        )
    return session


# Helper: List all sessions
@app.get("/api/v1/sessions", response_model=List[SessionResponse])
def list_sessions():
    return db.list_sessions()
