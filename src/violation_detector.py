import cv2
import numpy as np
import tensorflow as tf
import pickle
from ultralytics import YOLO
import keras
import time
from datetime import datetime
from pathlib import Path
from db import insert_attendance, insert_violation, insert_detected_id
import pandas as pd
import sqlite3

keras.config.enable_unsafe_deserialization()
tf.get_logger().setLevel('ERROR')

BASE_DIR = Path(__file__).resolve().parent
FACE_MODEL_PATH = BASE_DIR / "face_model_c.keras"
LABEL_ENCODER_PATH = BASE_DIR / "face_label_e.pkl"
YOLO_MODEL_PATH = BASE_DIR / "best.pt"

FRAME_SKIP = 2
RESIZE_WIDTH = 640
OUTPUT_DIR = BASE_DIR.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

print(" Loading models...")
face_model = tf.keras.models.load_model(FACE_MODEL_PATH, safe_mode=False)
with open(LABEL_ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)
yolo_model = YOLO(str(YOLO_MODEL_PATH))
print("✅ Models loaded successfully!")

def export_csv(df, filename):
    path = OUTPUT_DIR / filename
    df.to_csv(path, index=False)
    print(f"✅ Exported CSV: {path}")
    return path

def main(video_path=None, return_ids=False):
    """
    Detect persons in a video using YOLO + Face Recognition.
    Logs attendance, violations, detected IDs, and exports CSVs.
    If return_ids=True, returns set of person_ids detected in this video.
    """
    if video_path is None:
        print("⚠ No video path provided to main()")
        return set() if return_ids else None

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print("❌ Error: Could not open video.")
        return set() if return_ids else None

    frame_count = 0
    detected_ids_set = set()

    print(f"🎥 Processing video: {video_path}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % FRAME_SKIP != 0:
            continue

        h, w = frame.shape[:2]
        if w > RESIZE_WIDTH:
            scale = RESIZE_WIDTH / w
            frame = cv2.resize(frame, (RESIZE_WIDTH, int(h * scale)))

        start_time = time.time()
        device = 'cuda' if tf.config.list_physical_devices('GPU') else 'cpu'
        results = yolo_model.predict(frame, imgsz=320, verbose=False, device=device)[0]

        detected_trainers = []
        detected_members = []

        for box in results.boxes:
            cls_id = int(box.cls[0])
            cls_name = yolo_model.model.names.get(cls_id, "unknown")
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            # --- Face Recognition ---
            face_crop = frame[y1:y2, x1:x2]
            if face_crop.size == 0:
                continue

            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, (160, 160))
            face_resized = face_resized.astype('float32') / 255.0
            face_input = np.expand_dims(face_resized, axis=0)

            preds = face_model.predict(face_input, verbose=False)
            pred_class = np.argmax(preds, axis=1)
            pred_label = label_encoder.inverse_transform(pred_class)[0]

            person_id = str(pred_label)
            ts = datetime.now().isoformat(timespec="seconds")

            role = "trainer" if person_id.startswith("T") else "member"
            insert_attendance(person_id, role, "Workout Zone", ts)

            insert_detected_id(person_id, ts)
            detected_ids_set.add(person_id)

            if role == "trainer":
                detected_trainers.append(person_id)
            else:
                detected_members.append(person_id)

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(frame, f"{person_id} ({cls_name}) {conf:.2f}", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        for trainer_id in detected_trainers:
            for member_id in detected_members:
                insert_violation(trainer_id, member_id, "Unauthorized Activity", "Workout Zone", ts)

        fps = 1 / (time.time() - start_time + 1e-6)
        print(f" Frame {frame_count} processed — FPS: {fps:.2f}")

    cap.release()

    conn = sqlite3.connect("gym_management.db")
    if detected_ids_set:
        ids_tuple = tuple(str(x) for x in detected_ids_set)
        if len(ids_tuple) == 1:
            ids_tuple = (ids_tuple[0],)

        attendance_df = pd.read_sql_query(
            f"SELECT * FROM attendance WHERE person_id IN {ids_tuple}", conn
        )
        violation_df = pd.read_sql_query(
            f"SELECT * FROM violations WHERE trainer_id IN {ids_tuple} OR member_id IN {ids_tuple}", conn
        )
        detected_df = pd.read_sql_query(
            f"SELECT * FROM detected_ids WHERE person_id IN {ids_tuple}", conn
        )

        export_csv(attendance_df, "attendance_detected.csv")
        export_csv(violation_df, "violations_detected.csv")
        export_csv(detected_df, "detected_ids.csv")
    else:
        print("⚠ No valid IDs detected — skipping CSV export.")

    conn.close()
    print("✅ Detection finished and all data logged.")

    if return_ids:
        return detected_ids_set