# AI Interview Analyzer

A polished Streamlit mock-interview platform for a B.Tech project expo. It generates domain-specific questions with Groq, evaluates typed answers, optionally extracts audio and facial-expression features, shows explainable analytics, and creates a downloadable PDF report.

## Features

- Groq-generated, validated JSON question sets by domain, level, type and difficulty
- Curated local fallback bank when no API key, network, or model is available
- Persistent Streamlit interview state and an explicitly labelled Expo Demo Mode
- Typed-answer workflow; optional local audio signal analysis and optional DeepFace expression observations
- Transparent weighted scores: answer 40%, communication 20%, voice features 20%, expression-based indicator 20%
- Plotly dashboard, question-level feedback, and in-memory PDF report generation

## Architecture

```text
app.py → ai/ (Groq) | interview/ (session, fallback, scoring)
       → audio/ (signal features) | vision/ (optional DeepFace)
       → dashboard/ (Plotly) | utils/ (validation, PDF)
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

Add your own key in `.env`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

The key is read by `python-dotenv`, never displayed, and `.env` is ignored by Git.

## How the analysis works

Groq is asked to return strict JSON for questions, answer evaluation, and final feedback. Responses are validated and the app falls back safely if a call or JSON validation fails.

Voice analysis computes RMS energy, silence ratio, duration, and level consistency from a supplied/local audio signal. DeepFace, when installed and operational, samples a supplied camera frame and reports a detected facial expression. These values are supportive, non-diagnostic indicators—not proof of confidence, nervousness, personality, emotion, or suitability.

## Testing

```bash
python -m pytest tests -q
```

## Deployment

Streamlit Community Cloud can deploy this app after adding `GROQ_API_KEY` in its Secrets settings rather than committing `.env`. Typed answers work in hosted environments. Server-side OpenCV/sounddevice camera and microphone access can vary in browsers/containers, so the application remains functional with its typed-answer fallback and Demo Mode. For browser-native media capture, add a reviewed Streamlit component appropriate to the deployment environment.

## Limitations and future scope

LLM evaluation may be imperfect and should guide practice, not make hiring decisions. Facial-expression models and microphone availability vary across people, devices, light, accents, and browsers. Future work could add consent-based browser capture, user-corrected transcription, and fairness evaluation.
