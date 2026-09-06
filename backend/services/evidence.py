"""Evidence integrity — SHA-256 hash per image plus a hash chain per
session so tampering is detectable.
"""
import hashlib


def hash_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def chain_hash(previous_hash: str, new_hash: str) -> str:
    combined = (previous_hash + new_hash).encode("utf-8")
    return "sha256:" + hashlib.sha256(combined).hexdigest()