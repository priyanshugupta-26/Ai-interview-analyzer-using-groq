"""Application configuration, loaded without exposing secrets."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AI Interview Analyzer"

# Streamlit Community Cloud injects secrets via st.secrets, not os.environ.
# Fall back to os.getenv so local .env files still work.
def _get_secret(key: str, default: str = "") -> str:
    try:
        import streamlit as st
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

GROQ_API_KEY = _get_secret("GROQ_API_KEY")
GROQ_MODEL = _get_secret("GROQ_MODEL", "llama-3.3-70b-versatile")
SCORE_WEIGHTS = {"answer": 0.40, "communication": 0.20, "voice": 0.20, "behavior": 0.20}
DOMAINS = ["Python", "Data Science", "Machine Learning", "Artificial Intelligence", "Deep Learning", "Computer Vision", "Web Development", "Data Analytics", "SQL / DBMS", "Java", "C / C++", "Cloud Computing", "Cyber Security", "DevOps", "Business / Management", "HR", "Marketing", "Finance", "General Software Engineering", "Other"]
