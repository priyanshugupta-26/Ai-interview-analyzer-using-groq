"""Purposeful local questions used whenever the online generator is unavailable."""
from __future__ import annotations
from interview.models import Question

_BANK = {
    "Python": ["Explain the difference between a list and a tuple.", "What are generators, and when would you use one?", "How does exception handling work in Python?", "Describe inheritance and polymorphism with a Python example.", "What is a decorator and what problem can it solve?"],
    "Machine Learning": ["Differentiate supervised and unsupervised learning.", "What is overfitting, and how can it be reduced?", "Why do we use cross-validation?", "How would you evaluate an imbalanced classifier?", "Explain feature selection in a practical ML workflow."],
    "Data Science": ["How do you approach missing values in a dataset?", "What makes a feature useful for a model?", "Explain correlation versus causation.", "How would you communicate an insight to a non-technical stakeholder?", "Describe a data-cleaning workflow."],
    "HR": ["Tell me about yourself in a structured way.", "Describe a challenging team situation and how you handled it.", "How do you respond to constructive feedback?", "Why are you interested in this role?", "Tell me about a time you learned something quickly."],
}

def fallback_questions(domain: str, count: int, difficulty: str = "Mixed", interview_type: str = "Technical") -> list[Question]:
    prompts = _BANK.get(domain, [
        f"What are the core concepts you would prioritize when working in {domain}?",
        f"Describe a practical problem in {domain} and how you would solve it.",
        f"Which trade-offs matter most in a {domain} project?",
        f"How would you validate the quality of work in {domain}?",
        f"Tell us about a relevant project or learning experience in {domain}.",
    ])
    return [Question(i + 1, prompts[i % len(prompts)], "HR" if interview_type == "HR" else "Technical", difficulty if difficulty != "Mixed" else ("Easy" if i < 2 else "Medium" if i < 4 else "Hard")) for i in range(count)]
