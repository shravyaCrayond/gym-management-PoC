from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  
DATA_DIR = BASE_DIR / 'data'
VIDEO_FOLDER = BASE_DIR / 'sample_data' / 'videos'
TRAINER_DIR = BASE_DIR / 'sample_data' / 'trainers'
MEMBER_DIR = BASE_DIR / 'sample_data' / 'members'
CLIP_FOLDER = BASE_DIR / 'src' / 'static' / 'clips'
DB_PATH = DATA_DIR / 'gym_monitor.db'

CAMERA_ZONES = ['ENTRY', 'GYM_FLOOR', 'EXIT']
FRAME_INTERVAL_SEC = 2
TEST_VIDEO_PATH = VIDEO_FOLDER / 'test_video.mp4'

TRAINER_PROFILES = {
    'T001': {'name': 'Alex'},
    'T002': {'name': 'Ravi'},
}

MEMBER_PROFILES = {
    'M001': {'name': 'John'},
    'M002': {'name': 'Neha'},
}

MIN_SESSION_SECONDS = 300         # 5 minutes required for valid session
MAX_SESSION_GAP_SECONDS = 120     # max allowed gap between detections (2 min)
SESSION_TOLERANCE_MINUTES = 10    # tolerance for session duration check
EXTEND_TOLERANCE_SECONDS = 300    # 5 minutes extension allowed
UNSCHEDULED_WINDOW_SECONDS = 600  # 10 minutes early/late window for booking
FACE_MATCH_THRESHOLD = 0.45       # DeepFace cosine similarity threshold

VIOLATION_LOG_PATH = DATA_DIR / 'violations.log'

SQLITE_DB_URI = f"sqlite:///{DB_PATH}"

for path in [DATA_DIR, CLIP_FOLDER, VIDEO_FOLDER, TRAINER_DIR, MEMBER_DIR]:
    path.mkdir(parents=True, exist_ok=True)
