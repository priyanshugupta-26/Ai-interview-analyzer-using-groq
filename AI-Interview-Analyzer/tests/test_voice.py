import numpy as np
from audio.voice_analysis import analyze_audio

def test_voice_features_are_bounded():
    data = np.sin(np.linspace(0, 100, 16000)) * .05
    result = analyze_audio(data)
    assert 0 <= result["voice_score"] <= 100
    assert result["duration_seconds"] == 1.0
