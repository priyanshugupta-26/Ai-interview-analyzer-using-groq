"""Optional local microphone recorder. Browser deployment should use typed answers."""
from __future__ import annotations
import numpy as np

def load_wav(uploaded_file) -> tuple[np.ndarray, int]:
    """Read a user-provided WAV file for browser-compatible feature analysis."""
    try:
        from scipy.io import wavfile
        rate, samples = wavfile.read(uploaded_file)
        samples = np.asarray(samples)
        scale = np.iinfo(samples.dtype).max if np.issubdtype(samples.dtype, np.integer) else 1.0
        samples = samples.astype(np.float32)
        if samples.ndim > 1:
            samples = samples.mean(axis=1)
        samples = samples / scale
        return samples, int(rate)
    except Exception as exc:
        raise RuntimeError("That WAV file could not be read.") from exc

def record_audio(seconds: int = 10, sample_rate: int = 16000) -> np.ndarray:
    try:
        import sounddevice as sd
        recording = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        return recording.reshape(-1)
    except Exception as exc:
        raise RuntimeError("Microphone recording is unavailable on this device.") from exc
