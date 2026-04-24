from services.hand_service import HandService
from models.hand_data import Point2D


class FakeLandmark:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class FakeCategory:
    def __init__(self, category_name):
        self.category_name = category_name


class FakeResult:
    def __init__(self, hand_landmarks, handedness):
        self.hand_landmarks = hand_landmarks
        self.handedness = handedness


def build_fake_hand():
    points = [FakeLandmark(0.1, 0.1) for _ in range(21)]
    points[4] = FakeLandmark(0.2, 0.2)
    points[8] = FakeLandmark(0.4, 0.2)
    return points


def test_extract_hands_returns_single_hand():
    service = HandService(mirrored_view=False, pinch_threshold=60)

    fake_hand = build_fake_hand()
    result = FakeResult(
        hand_landmarks=[fake_hand],
        handedness=[[FakeCategory("Left")]]
    )

    hands = service.extract_hands(result, frame_width=1000, frame_height=500)

    assert len(hands) == 1
    assert hands[0].label == "Left"
    assert hands[0].thumb_tip == Point2D(x=200, y=100)
    assert hands[0].index_tip == Point2D(x=400, y=100)


def test_extract_hands_mirrored_label_swaps_left_to_right():
    service = HandService(mirrored_view=True, pinch_threshold=60)

    fake_hand = build_fake_hand()
    result = FakeResult(
        hand_landmarks=[fake_hand],
        handedness=[[FakeCategory("Left")]]
    )

    hands = service.extract_hands(result, frame_width=1000, frame_height=500)

    assert len(hands) == 1
    assert hands[0].label == "Right"


def test_extract_hands_detects_pinch_as_false_for_large_distance():
    service = HandService(mirrored_view=False, pinch_threshold=60)

    fake_hand = build_fake_hand()
    result = FakeResult(
        hand_landmarks=[fake_hand],
        handedness=[[FakeCategory("Left")]]
    )

    hands = service.extract_hands(result, frame_width=1000, frame_height=500)

    assert hands[0].metrics.distance_thumb_index > 60
    assert hands[0].metrics.pinch_active is False