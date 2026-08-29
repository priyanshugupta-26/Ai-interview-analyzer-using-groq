"""Non-diagnostic audio feature extraction and transparent indicator calculation."""
from __future__ import annotations
import numpy as np
from utils.validators import clamp_score

def analyze_audio(samples: np.ndarray, sample_rate: int = 16000) -> dict:
    if samples is None or len(samples) < 10:
        return {"voice_score": 0.0, "duration_seconds": 0.0, "rms_energy": 0.0, "silence_ratio": 1.0, "level_consistency": 0.0}
    signal = np.asarray(samples, dtype=float).reshape(-1)
    duration = len(signal) / sample_rate
    rms = float(np.sqrt(np.mean(signal ** 2)))
    frame = max(1, int(sample_rate * 0.1))
    energies = np.array([np.sqrt(np.mean(signal[i:i + frame] ** 2)) for i in range(0, len(signal), frame)])
    active = energies > max(0.008, rms * 0.20)
    silence = 1 - float(np.mean(active))
    consistency = float(max(0, 1 - np.std(energies[active]) / (np.mean(energies[active]) + 1e-8))) if active.any() else 0.0
    # A bounded signal-quality indicator, not a psychological assessment.
    energy_score = min(100, rms / 0.08 * 100)
    silence_score = max(0, 100 - max(0, silence - .35) * 150)
    score = clamp_score(.35 * energy_score + .35 * silence_score + .30 * consistency * 100)
    return {"voice_score": score, "duration_seconds": round(duration, 1), "rms_energy": round(rms, 4), "silence_ratio": round(silence, 3), "level_consistency": round(consistency, 3)}
