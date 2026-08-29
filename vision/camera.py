from __future__ import annotations

def camera_available() -> bool:
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        available = cap.isOpened()
        cap.release()
        return available
    except Exception:
        return False
