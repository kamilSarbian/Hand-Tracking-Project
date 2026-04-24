from config import PINCH_THRESHOLD, OPEN_THRESHOLD
from models.hand_data import HandData


class GestureRecognizer:
    """
    Converts finger states and thumb-index distance into named gestures.

    The order matters: pose gestures such as FIST are checked before PINCH so
    a closed hand is not accidentally classified as a pinch.
    """

    def __init__(self, pinch_sensitivity: float = 0.68):
        self.pinch_threshold = max(12, int(PINCH_THRESHOLD * pinch_sensitivity))

    def _is_fist(self, hand_data: HandData) -> bool:
        fingers = hand_data.fingers
        return (
            not fingers.index and
            not fingers.middle and
            not fingers.ring and
            not fingers.pinky
        )

    def _is_pinch(self, hand_data: HandData) -> bool:
        return hand_data.metrics.distance_thumb_index <= self.pinch_threshold

    def recognize(self, hand_data: HandData) -> str:
        fingers = hand_data.fingers
        distance = hand_data.metrics.distance_thumb_index

        if (
            fingers.thumb and
            not fingers.index and
            not fingers.middle and
            not fingers.ring and
            not fingers.pinky
            and distance >= OPEN_THRESHOLD
        ):
            return "THUMBS_UP"

        if self._is_fist(hand_data):
            return "FIST"

        if self._is_pinch(hand_data):
            return "PINCH"

        if (
            fingers.index and
            not fingers.middle and
            not fingers.ring and
            not fingers.pinky
        ):
            return "POINT"

        if (
            fingers.index and
            fingers.middle and
            not fingers.ring and
            not fingers.pinky
        ):
            return "PEACE"

        if (
            fingers.index and
            fingers.middle and
            fingers.ring and
            not fingers.pinky
        ):
            return "THREE"

        if (
            fingers.index and
            not fingers.middle and
            not fingers.ring and
            fingers.pinky
        ):
            return "ROCK"

        if distance >= OPEN_THRESHOLD and (
            fingers.index and fingers.middle and fingers.ring and fingers.pinky
        ):
            return "OPEN_HAND"

        return "UNKNOWN"
