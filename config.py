# config.py

VIDEO_PATH = "videos/test.mp4"

# YOLO models
VEHICLE_MODEL = "yolov8n.pt"          # vehicles + person
HELMET_MODEL = "yolov8n.pt"           # replace with helmet trained model
PLATE_MODEL = "yolov8n.pt"            # replace with plate detection model

# speed estimation
SPEED_LIMIT_KMPH = 60

# calibration (IMPORTANT)
# Example: 1 pixel = 0.05 meters (you must tune this for your camera)
PIXEL_TO_METER = 0.05

# MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "traffic_ai"
COLLECTION_NAME = "violations"

# Evidence saving
EVIDENCE_DIR = "evidence"
