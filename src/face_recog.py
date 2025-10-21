from datetime import datetime
from .db import insert_attendance

def process_clips():
    """
    Simulate detections from pre-labelled clips.
    Each clip contains a trainer-member pair.
    """
    detections = [
        {"trainer_id": "T001", "member_id": "M101", "zone": "Weight Zone"},
        {"trainer_id": "T002", "member_id": "M102", "zone": "Cardio Zone"},
        {"trainer_id": "T002", "member_id": "M101", "zone": "Cardio Zone"},  # unauthorized example
    ]
    for d in detections:
        ts = datetime.now().isoformat(timespec="seconds")
        insert_attendance(d["trainer_id"], "trainer", d["zone"], ts)
        insert_attendance(d["member_id"], "member", d["zone"], ts)
        print(f"[CAMERA] {d['trainer_id']} with {d['member_id']} in {d['zone']} at {ts}")
