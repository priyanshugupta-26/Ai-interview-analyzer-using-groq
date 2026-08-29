from __future__ import annotations
import json
from ai.groq_client import chat_json

def analyze_answer(question: str, answer: str) -> dict:
    """Use Groq if available; a transparent heuristic remains usable offline."""
    if not answer.strip():
        return {"relevance": 0, "technical_accuracy": 0, "clarity": 0, "completeness": 0, "overall": 0, "strengths": [], "improvements": ["Provide an answer before continuing."]}
    prompt = f'''Evaluate this mock-interview answer. Question: {question}\nAnswer: {answer}\nReturn JSON with 0-10 numbers relevance, technical_accuracy, clarity, completeness, overall; plus short arrays strengths and improvements. Be constructive and do not infer personality.'''
    content = chat_json(prompt)
    if content:
        try:
            data = json.loads(content)
            if all(k in data for k in ("relevance", "technical_accuracy", "clarity", "completeness", "overall")):
                return data
        except Exception:
            pass
    words = len(answer.split())
    score = min(8.0, 3.5 + words / 22)
    return {"relevance": round(score, 1), "technical_accuracy": round(score, 1), "clarity": round(min(8, 4 + words / 30), 1), "completeness": round(min(8, 3 + words / 25), 1), "overall": round(score, 1), "strengths": ["You provided a response with relevant detail."], "improvements": ["Use a clear structure and include one concrete example."]}
