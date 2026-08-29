from __future__ import annotations
import json
from ai.groq_client import chat_json

def generate_feedback(summary: dict) -> dict:
    prompt = f'''Create personalized, concise mock-interview feedback from this measured/AI-evaluated summary: {json.dumps(summary)}. Return JSON keys summary, strengths (array), improvements (array), practice_topics (array), disclaimer. Do not diagnose confidence or emotions; call them indicators only.'''
    content = chat_json(prompt)
    if content:
        try:
            return json.loads(content)
        except Exception:
            pass
    return {"summary": f"Your overall mock-interview score is {summary.get('overall', 0):.0f}/100. Build on your strongest areas with deliberate practice.", "strengths": ["Completed a structured mock interview", "Provided answers for review"], "improvements": ["Use a concise answer structure: context, approach, result.", "Add a practical example to technical explanations."], "practice_topics": [summary.get("domain", "your selected domain"), "STAR method", "timed mock answers"], "disclaimer": "Voice and expression values are non-diagnostic indicators based on measured signal features and model observations."}
