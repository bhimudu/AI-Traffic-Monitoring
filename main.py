import cv2
from ultralytics import YOLO
from datetime import datetime

from config import (
    VIDEO_PATH, VEHICLE_MODEL, HELMET_MODEL, PLATE_MODEL,
    SPEED_LIMIT_KMPH, PIXEL_TO_METER,
    MONGO_URI, DB_NAME, COLLECTION_NAME,
    EVIDENCE_DIR
)

from utils.tracker import track_objects
from utils.speed import SpeedEstimator
from utils.heatmap import HeatmapGenerator
from utils.anpr import read_plate
from utils.storage import StorageManager

# ------------------ LOAD MODELS ------------------
vehicle_model = YOLO(VEHICLE_MODEL)
helmet_model = YOLO(HELMET_MODEL)
plate_model = YOLO(PLATE_MODEL)

# ------------------ INIT HELPERS ------------------
speed_estimator = SpeedEstimator(pixel_to_meter=PIXEL_TO_METER)
storage = StorageManager(MONGO_URI, DB_NAME, COLLECTION_NAME, EVIDENCE_DIR)

cap = cv2.VideoCapture(VIDEO_PATH)

ret, first_frame = cap.read()
if not ret:
    print("❌ Video not found or cannot read.")
    exit()

heatmap = HeatmapGenerator(first_frame.shape)

# to avoid saving repeated evidence every frame
saved_overspeed = set()
saved_nohelmet = set()

# ------------------ MAIN LOOP ------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    points_for_heatmap = []

    results = track_objects(vehicle_model, frame)
    r = results[0]

    if r.boxes is None:
        cv2.imshow("Traffic AI", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        continue

    for box in r.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        xyxy = box.xyxy[0].cpu().numpy()
        x1, y1, x2, y2 = map(int, xyxy)

        # object ID
        track_id = None
        if box.id is not None:
            track_id = int(box.id[0])

        # center point
        cx = int((x1 + x2) / 2)
        cy = int((y1 + y2) / 2)
        points_for_heatmap.append((cx, cy))

        # draw bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        label = f"ID:{track_id} Conf:{conf:.2f}"
        cv2.putText(frame, label, (x1, y1 - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # -------- SPEED ESTIMATION ----------
        if track_id is not None:
            speed = speed_estimator.estimate_speed(track_id, cx, cy)
            cv2.putText(frame, f"{speed:.1f} km/h", (x1, y2 + 18),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            # Overspeed detection
            if speed > SPEED_LIMIT_KMPH and track_id not in saved_overspeed:
                saved_overspeed.add(track_id)

                # evidence snapshot
                snap_path = storage.save_snapshot(frame, "overspeed", track_id)

                # ANPR plate detection
                plate_text = None
                plate_results = plate_model(frame, verbose=False)

                if len(plate_results) > 0 and plate_results[0].boxes is not None:
                    for pbox in plate_results[0].boxes:
                        pxyxy = pbox.xyxy[0].cpu().numpy()
                        px1, py1, px2, py2 = map(int, pxyxy)
                        plate_crop = frame[py1:py2, px1:px2]
                        plate_text = read_plate(plate_crop)
                        if plate_text:
                            break

                data = {
                    "type": "OVERSPEED",
                    "track_id": track_id,
                    "speed": round(float(speed), 2),
                    "speed_limit": SPEED_LIMIT_KMPH,
                    "plate_number": plate_text,
                    "snapshot": snap_path,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                storage.save_violation(data)

                print("🚨 Overspeed Violation:", data)

    # -------- UPDATE HEATMAP ----------
    heatmap.update(points_for_heatmap)
    heat_overlay = heatmap.overlay(frame, alpha=0.7)

    cv2.imshow("Traffic AI (Heatmap + Detection)", heat_overlay)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
print("✅ Done.")
