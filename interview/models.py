from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

@dataclass
class Question:
    id: int
    question: str
    category: str = "Technical"
    difficulty: str = "Medium"

@dataclass
class AnswerResult:
    question_id: int
    answer_text: str
    answer_score: float
    communication_score: float
    voice: dict[str, Any] = field(default_factory=dict)
    emotion: dict[str, Any] = field(default_factory=dict)
    feedback: dict[str, Any] = field(default_factory=dict)
