import math
from typing import List

from models.hand_data import Point2D, HandMetrics, HandData, FingerState


class HandService:
    def __init__(self, mirrored_view: bool = True, pinch_threshold: int = 60):
        self.mirrored_view = mirrored_view
        self.pinch_threshold = pinch_threshold

    def _normalize_hand_label(self, raw_label: str) -> str:
        if not self.mirrored_view:
            return raw_label
        return "Right" if raw_label == "Left" else "Left"

    def _to_pixel_coords(self, landmark, width: int, height: int) -> Point2D:
        return Point2D(
            x=int(landmark.x * width),
            y=int(landmark.y * height)
        )

    def _calc_distance(self, p1: Point2D, p2: Point2D) -> int:
        return int(math.hypot(p2.x - p1.x, p2.y - p1.y))

    def _calc_radius(self, distance: int) -> int:
        return max(10, min(distance // 2, 120))

    def _is_finger_up(self, tip, pip) -> bool:
        return tip.y < pip.y

    def _is_thumb_up(self, hand_landmarks, raw_label: str) -> bool:
        thumb_tip = hand_landmarks[4]
        thumb_ip = hand_landmarks[3]

        if raw_label == "Right":
            return thumb_tip.x < thumb_ip.x
        return thumb_tip.x > thumb_ip.x

    def _build_finger_state(self, hand_landmarks, raw_label: str) -> FingerState:
        index_tip = hand_landmarks[8]
        index_pip = hand_landmarks[6]

        middle_tip = hand_landmarks[12]
        middle_pip = hand_landmarks[10]

        ring_tip = hand_landmarks[16]
        ring_pip = hand_landmarks[14]

        pinky_tip = hand_landmarks[20]
        pinky_pip = hand_landmarks[18]

        return FingerState(
            thumb=self._is_thumb_up(hand_landmarks, raw_label),
            index=self._is_finger_up(index_tip, index_pip),
            middle=self._is_finger_up(middle_tip, middle_pip),
            ring=self._is_finger_up(ring_tip, ring_pip),
            pinky=self._is_finger_up(pinky_tip, pinky_pip),
        )

    def extract_hands(self, result, frame_width: int, frame_height: int) -> List[HandData]:
        hands_data: List[HandData] = []

        if not result.hand_landmarks or not result.handedness:
            return hands_data

        for hand_landmarks, handedness_list in zip(result.hand_landmarks, result.handedness):
            raw_label = handedness_list[0].category_name
            label = self._normalize_hand_label(raw_label)

            landmarks_px = [
                self._to_pixel_coords(lm, frame_width, frame_height)
                for lm in hand_landmarks
            ]

            thumb_tip = self._to_pixel_coords(hand_landmarks[4], frame_width, frame_height)
            index_tip = self._to_pixel_coords(hand_landmarks[8], frame_width, frame_height)

            distance_thumb_index = self._calc_distance(thumb_tip, index_tip)
            radius = self._calc_radius(distance_thumb_index)

            center_point = Point2D(
                x=(thumb_tip.x + index_tip.x) // 2,
                y=(thumb_tip.y + index_tip.y) // 2
            )

            metrics = HandMetrics(
                distance_thumb_index=distance_thumb_index,
                pinch_active=distance_thumb_index <= self.pinch_threshold,
                radius=radius
            )

            fingers = self._build_finger_state(hand_landmarks, raw_label)

            hand_data = HandData(
                label=label,
                landmarks_px=landmarks_px,
                thumb_tip=thumb_tip,
                index_tip=index_tip,
                center_point=center_point,
                metrics=metrics,
                fingers=fingers
            )

            hands_data.append(hand_data)

        return hands_data