from __future__ import annotations
import json
from typing import Any
from interview.models import Question

def parse_questions_json(content: str, expected_count: int) -> list[Question]:
    """Parse a Groq JSON response, tolerating a markdown JSON fence."""
    cleaned = content.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    data: dict[str, Any] = json.loads(cleaned)
    raw = data.get("questions")
    if not isinstance(raw, list) or not raw:
        raise ValueError("Response contains no questions")
    questions = []
    for index, item in enumerate(raw[:expected_count], 1):
        if not isinstance(item, dict) or not str(item.get("question", "")).strip():
            raise ValueError("Question format is invalid")
        questions.append(Question(index, str(item["question"]).strip(), str(item.get("category", "Technical")), str(item.get("difficulty", "Medium"))))
    return questions

def clamp_score(value: float) -> float:
    return round(max(0.0, min(100.0, float(value))), 1)
