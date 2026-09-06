"""Prototype storage: in-memory dict, mirrored to a JSON file so a demo
restart doesn't lose everything.
"""
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

DATA_FILE = Path(__file__).resolve().parent / "sessions.json"
_lock = Lock()
_sessions: dict = {}


def _persist():
    with open(DATA_FILE, "w") as f:
        json.dump(_sessions, f, default=str, indent=2)


def _load():
    global _sessions
    if DATA_FILE.exists():
        with open(DATA_FILE, "r") as f:
            _sessions = json.load(f)


_load()


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def create_session(inspector_id: str, location: str, category: str, product_identifier: str) -> dict:
    with _lock:
        session_id = new_id("sess")
        session = {
            "session_id": session_id,
            "inspector_id": inspector_id,
            "location": location,
            "category": category,
            "product_identifier": product_identifier,
            "status": "CREATED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "images": {},
            "last_chain_hash": "sha256:" + "0" * 64,
            "last_evaluation": None,
        }
        _sessions[session_id] = session
        _persist()
        return session


def get_session(session_id: str):
    return _sessions.get(session_id)


def add_image(session_id: str, image_id: str, record: dict):
    with _lock:
        _sessions[session_id]["images"][image_id] = record
        _persist()


def save_evaluation(session_id: str, evaluation: dict):
    with _lock:
        _sessions[session_id]["last_evaluation"] = evaluation
        _persist()