# utils/heatmap.py
import cv2
import numpy as np

class HeatmapGenerator:
    def __init__(self, shape):
        self.heat = np.zeros((shape[0], shape[1]), dtype=np.float32)

    def update(self, points):
        for (x, y) in points:
            if 0 <= y < self.heat.shape[0] and 0 <= x < self.heat.shape[1]:
                self.heat[y, x] += 8

    def overlay(self, frame, alpha=0.5):
        heat_norm = cv2.normalize(self.heat, None, 0, 255, cv2.NORM_MINMAX)
        heat_uint8 = heat_norm.astype(np.uint8)
        heat_color = cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)

        return cv2.addWeighted(frame, 1 - alpha, heat_color, alpha, 0)
