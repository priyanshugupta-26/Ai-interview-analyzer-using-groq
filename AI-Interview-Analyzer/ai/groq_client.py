from __future__ import annotations
from config.settings import GROQ_API_KEY, GROQ_MODEL

def get_client():
    if not GROQ_API_KEY or GROQ_API_KEY == "PASTE_YOUR_KEY_HERE":
        return None
    try:
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY)
    except Exception:
        return None

def chat_json(prompt: str) -> str | None:
    client = get_client()
    if not client:
        return None
    try:
        response = client.chat.completions.create(model=GROQ_MODEL, messages=[{"role": "system", "content": "Return only valid JSON. Never wrap it in prose."}, {"role": "user", "content": prompt}], temperature=0.35, response_format={"type": "json_object"})
        return response.choices[0].message.content
    except Exception:
        return None
