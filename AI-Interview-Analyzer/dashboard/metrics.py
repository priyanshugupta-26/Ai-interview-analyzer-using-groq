from __future__ import annotations
def score_label(value: float) -> str:
    if value >= 80: return "Strong"
    if value >= 60: return "Developing"
    return "Practice focus"
