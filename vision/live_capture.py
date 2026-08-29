"""Browser live-camera processors used by streamlit-webrtc.

Frames and audio are retained only in memory for the current answer; the app
does not save raw interview video by default.
"""
from __future__ import annotations
from threading import Lock
import numpy as np

try:
    from streamlit_webrtc import VideoProcessorBase, AudioProcessorBase
except ImportError:  # Allows a friendly UI fallback before dependencies are installed.
    VideoProcessorBase = object
    AudioProcessorBase = object

class InterviewVideoProcessor(VideoProcessorBase):
    def __init__(self) -> None:
        self.latest_frame = None
        self.frame_count = 0
        self.lock = Lock()

    def recv(self, frame):
        image = frame.to_ndarray(format="bgr24")
        with self.lock:
            self.frame_count += 1
            # Sampling every 30 frames keeps later vision work light.
            if self.frame_count % 30 == 0:
                self.latest_frame = image.copy()
        return frame

    def frame_for_analysis(self):
        with self.lock:
            return None if self.latest_frame is None else self.latest_frame.copy()

class InterviewAudioProcessor(AudioProcessorBase):
    def __init__(self) -> None:
        self.chunks: list[np.ndarray] = []
        self.sample_rate = 48000
        self.lock = Lock()

    def recv(self, frame):
        samples = frame.to_ndarray()
        with self.lock:
            self.sample_rate = frame.sample_rate or self.sample_rate
            # Convert channel-first audio frames into a mono sequence.
            mono = samples.mean(axis=0) if samples.ndim > 1 else samples
            self.chunks.append(np.asarray(mono, dtype=np.float32).copy())
            # Bound in-memory capture to 5 minutes per question.
            if sum(len(chunk) for chunk in self.chunks) > self.sample_rate * 300:
                self.chunks = self.chunks[-300:]
        return frame

    def audio_for_analysis(self) -> tuple[np.ndarray, int]:
        with self.lock:
            if not self.chunks:
                return np.array([], dtype=np.float32), self.sample_rate
            return np.concatenate(self.chunks), self.sample_rate
