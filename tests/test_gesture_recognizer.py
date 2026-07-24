from gestures.recognizer import GestureRecognizer
from models.hand_data import FingerState, HandData, HandMetrics, Point2D


def build_hand(
    *,
    distance=100,
    thumb=False,
    index=False,
    middle=False,
    ring=False,
    pinky=False,
):
    point = Point2D(0, 0)
    return HandData(
        label="Right",
        landmarks_px=[],
        thumb_tip=point,
        index_tip=point,
        center_point=point,
        metrics=HandMetrics(
            distance_thumb_index=distance,
            pinch_active=False,
            radius=10,
        ),
        fingers=FingerState(
            thumb=thumb,
            index=index,
            middle=middle,
            ring=ring,
            pinky=pinky,
        ),
    )


def test_fist_ignores_thumb_state_and_wins_over_pinch_distance():
    recognizer = GestureRecognizer()
    hand = build_hand(distance=20, thumb=True)

    assert recognizer.recognize(hand) == "FIST"


def test_pinch_requires_stronger_close_distance():
    recognizer = GestureRecognizer()

    assert recognizer.recognize(build_hand(distance=50, index=True)) == "POINT"
    assert recognizer.recognize(build_hand(distance=35, index=True)) == "PINCH"


def test_extra_gestures_are_recognized():
    recognizer = GestureRecognizer()

    assert (
        recognizer.recognize(build_hand(index=True, middle=True, ring=True)) == "THREE"
    )
    assert recognizer.recognize(build_hand(index=True, pinky=True)) == "ROCK"
    assert recognizer.recognize(build_hand(distance=150, thumb=True)) == "THUMBS_UP"
