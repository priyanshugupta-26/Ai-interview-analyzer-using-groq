"""Lazy DeepFace wrapper; expressions are observations, never psychological conclusions."""
from __future__ import annotations

def analyze_frame(frame) -> dict:
    try:
        from deepface import DeepFace
        result = DeepFace.analyze(frame, actions=["emotion"], enforce_detection=False, silent=True)
        item = result[0] if isinstance(result, list) else result
        emotions = item.get("emotion", {})
        dominant = item.get("dominant_emotion", max(emotions, key=emotions.get) if emotions else "neutral")
        return {"dominant_emotion": dominant, "distribution": {k: round(float(v), 1) for k, v in emotions.items()}, "available": True}
    except Exception:
        return {"dominant_emotion": "Not available", "distribution": {}, "available": False}
