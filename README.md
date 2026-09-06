# Legal Metrology Compliance Verification System

An automated computer vision and OCR-assisted compliance auditing system for Legal Metrology packaged commodity standards (e.g., Legal Metrology Packaged Commodities Rules).

---

## 📁 Repository Structure

```
legal-metrology/
├── README.md
├── API_CONTRACT.md              # Frozen API specification
├── .gitignore
│
├── frontend/
│   ├── capture.html             # Camera capture + multi-side upload UI
│   ├── dashboard.html           # Session list + compliance verdict view
│   └── assets/
│       ├── style.css            # Frontend styles & theme tokens
│       └── app.js               # Capture flow, validation, and dashboard logic
│
├── backend/
│   ├── main.py                  # FastAPI app (4 core endpoints)
│   ├── requirements.txt         # Python dependencies
│   ├── models/
│   │   └── schemas.py           # Pydantic request/response models
│   ├── services/
│   │   ├── quality.py           # Blur, brightness, and glare quality checks
│   │   ├── ocr.py               # Tesseract OCR wrapper & layout parsing
│   │   ├── declarations.py      # Regex & NLP declaration field extractor
│   │   ├── coverage.py          # Evidence coverage calculation engine
│   │   ├── measurement.py       # Pixel-to-metric calibration & uncertainty
│   │   ├── rules_engine.py      # JSON-driven deterministic rules evaluation
│   │   └── evidence.py          # SHA-256 cryptographic hashing & audit trail
│   └── storage/
│       └── db.py                # In-memory storage with JSON persistence
│
├── rules/
│   └── categories/
│       └── packaged_food.json   # Versioned rule definitions for packaged food
│
├── data/
│   └── test_images/             # Sample package inspection photos
│
├── tests/
│   ├── unit/                    # Unit tests for services & extraction
│   └── integration/             # Integration tests for end-to-end API flows
│
└── docs/
    └── architecture.md          # Technical architecture & data flow
```

---

## 🚀 Getting Started

### Backend Setup

1. **Prerequisites**: Python 3.10+, Tesseract OCR installed on system.
2. **Install dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
3. **Run Backend Server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup

Open `frontend/capture.html` or `frontend/dashboard.html` in a web browser, or serve via a lightweight static server:
```bash
# From workspace root
npx serve frontend
```
