"""Conservative camera-engagement estimate based on visible frontal eyes.

This does not determine attention, confidence, or a person's intent. It only
describes whether a face and both eyes are visible in a representative frame.
"""
from __future__ import annotations

def analyze_eye_visibility(frame) -> dict:
    try:
        import cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=5)
        if len(faces) == 0:
            return {"eye_contact_score": 0.0, "face_visible": False, "eyes_visible": 0, "label": "Face not detected"}
        x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
        eyes = eye_cascade.detectMultiScale(gray[y:y + h, x:x + w], scaleFactor=1.1, minNeighbors=5)
        visible = min(len(eyes), 2)
        score = 85.0 if visible >= 2 else 50.0 if visible == 1 else 20.0
        return {"eye_contact_score": score, "face_visible": True, "eyes_visible": visible, "label": "Both eyes visible" if visible >= 2 else "Partial eye visibility" if visible else "Eyes not detected"}
    except Exception:
        return {"eye_contact_score": 0.0, "face_visible": False, "eyes_visible": 0, "label": "Camera analysis unavailable"}
