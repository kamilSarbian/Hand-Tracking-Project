from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Point2D:
    x: int
    y: int


@dataclass
class FingerState:
    thumb: bool
    index: bool
    middle: bool
    ring: bool
    pinky: bool


@dataclass
class HandMetrics:
    distance_thumb_index: int
    pinch_active: bool
    radius: int


@dataclass
class HandData:
    label: str
    landmarks_px: List[Point2D]
    thumb_tip: Point2D
    index_tip: Point2D
    center_point: Point2D
    metrics: HandMetrics
    fingers: FingerState
    gesture_name: Optional[str] = None