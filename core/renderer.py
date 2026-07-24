from typing import List

import cv2

from models.hand_data import HandData


class HandRenderer:
    """
    Renders the clean camera view with hands and an optional drawing canvas.
    """

    def draw(
        self,
        frame,
        hands_data: List[HandData],
        canvas,
    ):
        return self._blend_canvas(frame, canvas)

    def _blend_canvas(self, frame, canvas):
        if canvas is None:
            return frame

        return cv2.addWeighted(frame, 1.0, canvas, 1.0, 0)
