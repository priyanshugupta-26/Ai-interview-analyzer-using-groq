"""Optional Groq transcription for browser-captured interview audio."""
from __future__ import annotations
from io import BytesIO
import numpy as np
from scipy.io import wavfile
from ai.groq_client import get_client

def transcription_available() -> bool:
    return get_client() is not None

def transcribe_audio(samples: np.ndarray, sample_rate: int) -> str:
    """Return a transcript, or an empty string when speech recognition fails."""
    if samples is None or len(samples) < sample_rate:
        return ""
    try:
        audio = np.asarray(samples, dtype=np.float32)
        peak = float(np.max(np.abs(audio))) or 1.0
        pcm = (audio / peak * 32767).astype(np.int16)
        buffer = BytesIO()
        wavfile.write(buffer, sample_rate, pcm)
        buffer.seek(0)
        client = get_client()
        if not client:
            return ""
        response = client.audio.transcriptions.create(
            file=("interview-answer.wav", buffer.read()),
            model="whisper-large-v3-turbo",
            response_format="json",
        )
        return str(getattr(response, "text", "")).strip()
    except Exception:
        return ""
