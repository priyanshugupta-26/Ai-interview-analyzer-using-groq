"""Explainable weighted scoring. Components are 0–100 values."""
from __future__ import annotations
from config.settings import SCORE_WEIGHTS
from utils.validators import clamp_score

def behavioral_indicator(emotion: dict) -> float:
    distribution = emotion.get("distribution", {}) if emotion else {}
    if not distribution:
        return 60.0  # neutral unavailable-data baseline, labelled clearly in UI
    neutral_happy = distribution.get("neutral", 0) + distribution.get("happy", 0)
    return clamp_score(45 + neutral_happy * .55)

def calculate_scores(results: list[dict], weights: dict | None = None) -> dict:
    if not results:
        return {"overall": 0, "technical": 0, "communication": 0, "voice": 0, "behavior": 0}
    weights = weights or SCORE_WEIGHTS
    technical = sum(float(r["answer_score"]) for r in results) / len(results)
    communication = sum(float(r["communication_score"]) for r in results) / len(results)
    voice = sum(float(r.get("voice", {}).get("voice_score", 60)) for r in results) / len(results)
    behavior = sum(behavioral_indicator(r.get("emotion", {})) for r in results) / len(results)
    overall = weights["answer"] * technical + weights["communication"] * communication + weights["voice"] * voice + weights["behavior"] * behavior
    return {"overall": clamp_score(overall), "technical": clamp_score(technical), "communication": clamp_score(communication), "voice": clamp_score(voice), "behavior": clamp_score(behavior)}
