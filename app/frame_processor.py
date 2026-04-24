class FrameProcessor:
    """
    Processes a single frame:
    - hand detection
    - conversion into app data models
    - gesture recognition
    """

    def __init__(self, detector, hand_service, recognizer):
        self.detector = detector
        self.hand_service = hand_service
        self.recognizer = recognizer

    def process(self, frame):
        h, w, _ = frame.shape

        result = self.detector.detect(frame)
        hands_data = self.hand_service.extract_hands(result, w, h)

        for hand_data in hands_data:
            hand_data.gesture_name = self.recognizer.recognize(hand_data)

        return hands_data
