# utils/speed.py
import math
import time

class SpeedEstimator:
    def __init__(self, pixel_to_meter=0.05):
        self.pixel_to_meter = pixel_to_meter
        self.prev_positions = {}   # id -> (x, y, time)

    def estimate_speed(self, track_id, cx, cy):
        now = time.time()

        if track_id not in self.prev_positions:
            self.prev_positions[track_id] = (cx, cy, now)
            return 0

        px, py, pt = self.prev_positions[track_id]
        dt = now - pt
        if dt <= 0:
            return 0

        pixel_dist = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)
        meter_dist = pixel_dist * self.pixel_to_meter

        mps = meter_dist / dt
        kmph = mps * 3.6

        self.prev_positions[track_id] = (cx, cy, now)
        return kmph
