import cv2
import numpy as np


class DrawingService:
    def __init__(self, thickness: int = 5):
        self.thickness = thickness
        self.canvas = None
        self.last_draw_point = None

    def ensure_canvas(self, frame_height: int, frame_width: int):
        if self.canvas is None:
            self.canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            return

        if self.canvas.shape[0] != frame_height or self.canvas.shape[1] != frame_width:
            self.canvas = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
            self.last_draw_point = None

    def get_canvas(self):
        return self.canvas

    def clear(self):
        if self.canvas is not None:
            self.canvas[:] = 0
        self.last_draw_point = None

    def pause(self):
        self.last_draw_point = None

    def draw_point_path(self, x: int, y: int, color: tuple[int, int, int]):
        current_point = (x, y)

        if self.last_draw_point is not None and self.canvas is not None:
            cv2.line(
                self.canvas, self.last_draw_point, current_point, color, self.thickness
            )

        self.last_draw_point = current_point
