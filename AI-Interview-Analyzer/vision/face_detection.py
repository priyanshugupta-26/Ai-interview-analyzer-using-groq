from __future__ import annotations

def face_detection_available() -> bool:
    try:
        import cv2  # noqa: F401
        return True
    except Exception:
        return False
