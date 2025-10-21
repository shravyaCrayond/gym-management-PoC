# from src.face_recog import process_clips
from src.violation_detector import detect_unauthorized_sessions, detect_extended_sessions

def main():
    print(" Starting Trainer Activity Detection PoC")
    # process_clips()
    detect_unauthorized_sessions()
    detect_extended_sessions()

    print(" Detection cycle complete.")

if __name__ == "__main__":
    main()
