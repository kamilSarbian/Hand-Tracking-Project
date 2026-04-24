from utils.settings_loader import load_settings


SETTINGS = load_settings()

# MediaPipe model path.
MODEL_PATH = "models_assets/hand_landmarker.task"

# Camera and window.
CAMERA_INDEX = SETTINGS["camera_index"]
WINDOW_NAME = SETTINGS["window_name"]
MIRRORED_VIEW = SETTINGS["mirrored_view"]

# Hand detection configuration.
MAX_HANDS = SETTINGS["max_hands"]
MIN_HAND_DETECTION_CONFIDENCE = SETTINGS["min_hand_detection_confidence"]
MIN_HAND_PRESENCE_CONFIDENCE = SETTINGS["min_hand_presence_confidence"]
MIN_TRACKING_CONFIDENCE = SETTINGS["min_tracking_confidence"]

# Gesture thresholds.
PINCH_THRESHOLD = SETTINGS["pinch_threshold"]
OPEN_THRESHOLD = SETTINGS["open_threshold"]

# Gesture cooldown, for example screenshot triggering.
GESTURE_COOLDOWN_SECONDS = SETTINGS["gesture_cooldown_seconds"]

# Drawing settings.
DRAW_THICKNESS = SETTINGS["draw_thickness"]

# Output folders.
SCREENSHOT_DIR = "outputs/screenshots"
RECORDING_DIR = "outputs/recordings"

# Logical app canvas size.
APP_WIDTH = SETTINGS["app_width"]
APP_HEIGHT = SETTINGS["app_height"]
