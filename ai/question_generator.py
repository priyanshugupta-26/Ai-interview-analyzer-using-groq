from __future__ import annotations
from ai.groq_client import chat_json
from interview.question_bank import fallback_questions
from utils.validators import parse_questions_json

def generate_questions(domain: str, experience: str, count: int, difficulty: str, interview_type: str) -> tuple[list, bool, str]:
    prompt = f'''Generate exactly {count} progressive interview questions for domain {domain}. Candidate experience: {experience}; difficulty: {difficulty}; interview type: {interview_type}. Cover practical and foundational concepts appropriate to this domain. Return JSON: {{"domain":"{domain}","questions":[{{"id":1,"question":"...","category":"Technical or HR","difficulty":"Easy|Medium|Hard"}}]}}.'''
    content = chat_json(prompt)
    if content:
        try:
            return parse_questions_json(content, count), False, "Questions generated with Groq AI."
        except Exception:
            pass
    return fallback_questions(domain, count, difficulty, interview_type), True, "Groq AI is unavailable right now; using the curated local question bank."
