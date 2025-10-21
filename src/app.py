import streamlit as st
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "videos"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

VIOLATIONS_CSV_PATH = DATA_DIR / "violations_detected.csv"
DETECTED_IDS_CSV_PATH = DATA_DIR / "detected_ids.csv"
ATTENDANCE_CSV_PATH = DATA_DIR / "attendance_detected.csv"
SESSION_FILE = DATA_DIR / "sessions.csv"
PAYMENTS_FILE = DATA_DIR / "payments.csv"

st.set_page_config(page_title="Gym Trainer Activity Monitor", layout="wide")
st.title("🏋 Gym Trainer Policy Violation Detector Dashboard")

tab1, tab2 = st.tabs(["🎥 YOLO + Face Recognition", "⏱ Session & Interaction Violations"])

def check_file(path: Path):
    st.write(f"Checking file: {path.resolve()}")
    return path.exists()

with tab1:
    st.markdown("""
    Upload a gym CCTV *video (.mp4)* to automatically detect and flag  
    unauthorized trainer activities using the trained **YOLO + Face Recognition** model.
    """)

    uploaded_file = st.file_uploader("📹 Choose a video file (.mp4)", type=["mp4"])

    if uploaded_file:
        file_path = UPLOAD_DIR / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.success(f"✅ Video uploaded successfully: {uploaded_file.name}")
        st.video(str(file_path))

        if st.button("🚀 Run YOLO + Face Recognition Detection"):
            with st.spinner("Processing video... ⏳"):
                try:
                    from violation_detector import main as detect_video

                    detected_ids = detect_video(video_path=str(file_path), return_ids=True)

                    if not detected_ids:
                        st.warning("⚠ No valid IDs detected in this video.")
                    else:
                        st.success(f"✅ Detection completed! Total IDs in this video: {len(detected_ids)}")

                        if check_file(ATTENDANCE_CSV_PATH):
                            df_attendance = pd.read_csv(ATTENDANCE_CSV_PATH)
                            df_current = df_attendance[df_attendance.person_id.isin(detected_ids)]
                            df_current = df_current.drop_duplicates(subset=["person_id"])
                            if not df_current.empty:
                                st.info("📝 Attendance records for this video:")
                                st.dataframe(df_current)
                                st.metric("👨‍🏫 Trainers detected", df_current[df_current.role=="trainer"].person_id.nunique())
                                st.metric("🧑‍🤝‍🧑 Members detected", df_current[df_current.role=="member"].person_id.nunique())
                            else:
                                st.warning("⚠ No attendance records found for this video.")
                        else:
                            st.warning("⚠ attendance_detected.csv not found.")

                        if check_file(VIOLATIONS_CSV_PATH):
                            df_violations = pd.read_csv(VIOLATIONS_CSV_PATH)
                            df_current_violations = df_violations[
                                df_violations.trainer_id.isin(detected_ids) |
                                df_violations.member_id.isin(detected_ids)
                            ]
                            df_current_violations = df_current_violations.drop_duplicates(
                                subset=["trainer_id", "member_id", "violation_type", "timestamp"]
                            )
                            if not df_current_violations.empty:
                                st.warning(f"⚠ Detected {len(df_current_violations)} violation(s) in this video!")
                                st.dataframe(df_current_violations)
                            else:
                                st.success("✅ No violations detected in this video.")
                        else:
                            st.warning("⚠ violations_detected.csv not found.")

                except Exception as e:
                    st.error(f"❌ Error during detection: {e}")

with tab2:
    st.markdown("""
    Detect trainer violations based on static **CSV data**:
    - Extended session times  
    - Unauthorized extra services  
    - Unauthorized interactions  
    - Direct payments  
    """)

    missing_files = [f.name for f in [ATTENDANCE_CSV_PATH] if not check_file(f)]
    if missing_files:
        st.error(f"❌ Missing files: {', '.join(missing_files)}")
        st.info("Please ensure these files exist in the `/data` directory with correct names.")
    else:
        st.success("✅ All required CSV files found!")

        with st.expander("📋 View Attendance Data"):
            st.dataframe(pd.read_csv(ATTENDANCE_CSV_PATH))
        
        if st.button("🕒 Run Full Violation Detection"):
            with st.spinner("Analyzing all violations... ⏳"):
                try:
                    from detect_extended_sessions import main as detect_main
                    detect_main()
                    st.success("✅ Violation analysis completed!")

                    if check_file(VIOLATIONS_CSV_PATH):
                        df = pd.read_csv(VIOLATIONS_CSV_PATH)
                        df = df.drop_duplicates(subset=["trainer_id", "member_id", "violation_type", "timestamp"])
                        if not df.empty:
                            st.warning(f"⚠ Detected {len(df)} unique violation(s)!")
                            st.dataframe(df)
                        else:
                            st.success("✅ No violations detected.")
                    else:
                        st.warning("⚠ violations.csv not generated.")
                except Exception as e:
                    st.error(f"❌ Error running detection: {e}")

        if st.button("🔄 Refresh Existing Violations CSV"):
            if check_file(VIOLATIONS_CSV_PATH):
                try:
                    df = pd.read_csv(VIOLATIONS_CSV_PATH)
                    df = df.drop_duplicates(subset=["trainer_id", "member_id", "violation_type", "timestamp"])
                    if not df.empty:
                        st.warning(f"⚠ Detected {len(df)} unique violation(s)!")
                        st.dataframe(df)
                    else:
                        st.success("✅ No violations detected.")
                except pd.errors.EmptyDataError:
                    st.warning("⚠ violations.csv is empty — no data found.")
                except Exception as e:
                    st.error(f"❌ Error reading violations.csv: {e}")
            else:
                st.warning("⚠ violations.csv not found.")
