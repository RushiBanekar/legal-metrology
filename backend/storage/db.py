import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from ..models.schemas import SessionResponse, SessionCreateRequest


class StorageDB:
    def __init__(self, persistence_file: Optional[Path] = None):
        self.persistence_file = persistence_file
        self.sessions: Dict[str, SessionResponse] = {}
        if self.persistence_file and self.persistence_file.exists():
            self._load_from_disk()

    def _load_from_disk(self):
        try:
            with open(self.persistence_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for sess_id, s_data in data.items():
                    self.sessions[sess_id] = SessionResponse(**s_data)
        except Exception:
            pass

    def _save_to_disk(self):
        if not self.persistence_file:
            return
        try:
            self.persistence_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persistence_file, "w", encoding="utf-8") as f:
                serialized = {k: v.model_dump(mode="json") for k, v in self.sessions.items()}
                json.dump(serialized, f, indent=2, default=str)
        except Exception:
            pass

    def create_session(self, session_id: str, request: SessionCreateRequest) -> SessionResponse:
        now = datetime.utcnow()
        session = SessionResponse(
            session_id=session_id,
            category=request.category,
            rule_version=request.rule_version,
            status="in_progress",
            created_at=now,
            updated_at=now,
            metadata=request.metadata,
            images=[],
            declarations={},
        )
        self.sessions[session_id] = session
        self._save_to_disk()
        return session

    def get_session(self, session_id: str) -> Optional[SessionResponse]:
        return self.sessions.get(session_id)

    def list_sessions(self) -> List[SessionResponse]:
        return sorted(self.sessions.values(), key=lambda s: s.created_at, reverse=True)

    def update_session(self, session: SessionResponse) -> SessionResponse:
        session.updated_at = datetime.utcnow()
        self.sessions[session.session_id] = session
        self._save_to_disk()
        return session


# Global singleton instance
_db_instance: Optional[StorageDB] = None


def get_db(persistence_path: Optional[Path] = None) -> StorageDB:
    global _db_instance
    if _db_instance is None:
        _db_instance = StorageDB(persistence_file=persistence_path)
    return _db_instance
