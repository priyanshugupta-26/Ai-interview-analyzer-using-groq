from __future__ import annotations
import streamlit as st

DEFAULTS = {"page": "Home", "questions": [], "current_question": 0, "answers": [], "candidate": {}, "final_scores": None, "feedback": None, "demo_mode": False}

def init_session() -> None:
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_interview() -> None:
    for key, value in DEFAULTS.items():
        st.session_state[key] = value.copy() if isinstance(value, dict) else list(value) if isinstance(value, list) else value
