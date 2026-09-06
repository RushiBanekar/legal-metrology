import hashlib
import json
from typing import Any, Dict


def generate_sha256_hash(data: bytes) -> str:
    """Generates SHA-256 hexadecimal digest for binary data."""
    hasher = hashlib.sha256()
    hasher.update(data)
    return hasher.hexdigest()


def generate_audit_hash(payload: Dict[str, Any]) -> str:
    """Generates deterministic SHA-256 hash of a JSON-serializable evaluation bundle."""
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
