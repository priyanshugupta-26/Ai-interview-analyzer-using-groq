"""Application configuration, loaded without exposing secrets."""
from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "AI Interview Analyzer"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SCORE_WEIGHTS = {"answer": 0.40, "communication": 0.20, "voice": 0.20, "behavior": 0.20}
DOMAINS = ["Python", "Data Science", "Machine Learning", "Artificial Intelligence", "Deep Learning", "Computer Vision", "Web Development", "Data Analytics", "SQL / DBMS", "Java", "C / C++", "Cloud Computing", "Cyber Security", "DevOps", "Business / Management", "HR", "Marketing", "Finance", "General Software Engineering", "Other"]
