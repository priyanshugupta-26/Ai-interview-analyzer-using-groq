"""Deliberately uses a typed-answer fallback; no unverified transcription is claimed."""
from __future__ import annotations

def transcription_available() -> bool:
    return False
