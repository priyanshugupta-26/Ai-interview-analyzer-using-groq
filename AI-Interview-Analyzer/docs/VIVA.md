# AI Interview Analyzer — Viva Notes

## Project overview

AI Interview Analyzer is an AI-assisted mock-interview application. A candidate configures a domain and interview style, receives a question set, answers questions, reviews analytics, and downloads a report. It is a practice tool, not an automated hiring system.

## Problem statement and objectives

Interview preparation is often unstructured and feedback is delayed. The project provides repeatable domain-focused practice, structured answer feedback, measurable audio-feature summaries, optional facial-expression observations, and an explainable score breakdown.

## Technology and architecture

Python and Streamlit provide the UI and workflow. Groq generates JSON question sets and feedback. NumPy processes audio samples. OpenCV accesses video devices where available; DeepFace is used lazily for optional expression classification. Plotly renders charts and ReportLab produces PDFs. Modules isolate AI, audio, vision, interview/scoring, dashboard, and report concerns.

## How the components work

- **Groq:** The app sends a constrained prompt and requests JSON-only output. A validator checks its shape; a curated question bank is used on failure.
- **OpenCV:** It provides camera/frame access, if the runtime permits it. It does not itself infer emotion.
- **DeepFace and CNNs:** DeepFace wraps pretrained face-analysis models, commonly convolutional neural networks. A CNN learns image filters in layers to recognize visual patterns. This project does not train its own CNN.
- **Voice signal processing:** RMS represents signal energy; framed energy estimates silence/activity; variation in active-frame energy estimates level consistency. These form a bounded voice-feature indicator.
- **Scoring:** `0.40 answer + 0.20 communication + 0.20 voice + 0.20 expression-based indicator`. The weights are visible in `config/settings.py` and can be changed.

## Honesty, limitations, and safeguards

Facial expressions do not prove nervousness or confidence. Audio level does not prove confidence. The app uses the terms “detected facial expression” and “indicator”, not diagnosis. Results can be affected by lighting, background noise, model bias, answer transcription availability, network access, and LLM variability. It aims for structured practice, not bias-free or autonomous recruitment.

## Advantages and future scope

The app is modular, resilient to missing API/device access, supports Demo Mode, and produces immediate visual feedback. Future work: consent-based browser capture, speech-to-text with user correction, more diverse validation, human rubrics, and accessibility testing.

## Likely viva questions with answers

1. **What problem does it solve?** It gives candidates structured, repeatable mock-interview practice and feedback.
2. **Why Streamlit?** It enables a Python-first, interactive dashboard quickly and is easy to demonstrate.
3. **Why Groq?** It offers hosted LLM inference suited to domain-specific question/feedback generation.
4. **Is the API key exposed?** No. It is loaded from `.env`/deployment secrets and ignored by Git.
5. **What if Groq fails?** Validated local fallback questions keep the workflow available.
6. **Why JSON from Groq?** Structured data is safer to parse and render than free-form text.
7. **How is JSON validated?** The app checks for a non-empty question list and required question text.
8. **What is DeepFace used for?** Optional pretrained facial-expression classification from representative frames.
9. **Did you train a CNN?** No; DeepFace provides pretrained model access.
10. **What is a CNN?** A layered neural network that learns spatial image features via convolutions.
11. **What does OpenCV do?** It supports camera/video frame operations when a local device is available.
12. **Can it detect nervousness?** No. It only reports model-detected expressions, which are not psychological proof.
13. **What audio features are measured?** RMS energy, duration, silence ratio, and energy consistency.
14. **Does loud volume mean confidence?** No; the score uses several bounded signal features and remains non-diagnostic.
15. **How is the voice score calculated?** A transparent weighted combination of energy, excessive silence, and consistency.
16. **What is the scoring formula?** 40% answer, 20% communication, 20% voice-feature indicator, 20% expression-based indicator.
17. **Why make weights configurable?** It makes the rubric explainable and adjustable for a learning context.
18. **How does Demo Mode help?** It provides clearly labelled sample-compatible signals for an expo if hardware/network fails.
19. **How is state preserved?** `st.session_state` stores configuration, questions, answers, and results across Streamlit reruns.
20. **Why use fallback typed answers?** Browser/server audio access is inconsistent; typed answers keep deployments reliable.
21. **What charts are available?** A gauge, radar chart, question-score line chart, and expression distribution bar chart.
22. **How is the PDF created?** ReportLab builds an in-memory, downloadable report.
23. **What security measures exist?** No hardcoded key; `.env` is ignored; errors fall back instead of exposing traces.
24. **Can this be deployed?** Yes, on Streamlit Community Cloud with secret configuration; media has graceful fallbacks.
25. **What are major limitations?** LLM variability, device quality, expression-model bias, and no diagnostic validity.
26. **What future improvement is most important?** Consent-based browser capture with user-corrected speech transcription and fairness testing.
