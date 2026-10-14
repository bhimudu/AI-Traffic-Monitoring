# utils/storage.py
import os
import cv2
from pymongo import MongoClient
from datetime import datetime

class StorageManager:
    def __init__(self, mongo_uri, db_name, collection_name, evidence_dir):
        self.client = MongoClient(mongo_uri)
        self.col = self.client[db_name][collection_name]
        self.evidence_dir = evidence_dir

        os.makedirs(evidence_dir, exist_ok=True)
        os.makedirs(os.path.join(evidence_dir, "overspeed"), exist_ok=True)
        os.makedirs(os.path.join(evidence_dir, "nohelmet"), exist_ok=True)

    def save_snapshot(self, frame, violation_type, track_id):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{violation_type}_{track_id}_{ts}.jpg"
        path = os.path.join(self.evidence_dir, violation_type, filename)
        cv2.imwrite(path, frame)
        return path

    def save_violation(self, data):
        self.col.insert_one(data)
