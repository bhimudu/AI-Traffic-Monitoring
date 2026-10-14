# utils/tracker.py
from ultralytics import YOLO

def track_objects(model: YOLO, frame):
    """
    Returns tracked results using YOLO + ByteTrack
    """
    results = model.track(frame, persist=True, verbose=False)
    return results
