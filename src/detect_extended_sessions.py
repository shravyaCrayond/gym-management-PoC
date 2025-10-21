import pandas as pd
from pathlib import Path

DATA_DIR = Path("./data")
TOLERANCE_MINUTES = 10

SESSIONS_FILE = DATA_DIR / "sessions.csv"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"
PAYMENTS_FILE = DATA_DIR / "payments.csv" 
OUTPUT_FILE = DATA_DIR / "violations.csv" 

OUTPUT_COLUMNS = [
    "trainer_id",
    "member_id",
    "zone",
    "violation_type",
    "official_start_time",
    "official_end_time",
    "timestamp",
    "overtime_minutes",
    "details"
]


def read_csv_clean(file_path, datetime_cols=None, str_cols=None):
    """Read CSV, strip column names, clean strings, convert datetimes"""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        if str_cols:
            for col in str_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
        if datetime_cols:
            for col in datetime_cols:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
        return df
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return pd.DataFrame()

def detect_extended_sessions(sessions, attendance):
    violations = []

    for _, session in sessions.iterrows():
        trainer = session["trainer_id"]
        member = session["member_id"]
        zone = session["zone"]
        start_time = session["start_time"]
        end_time = session["end_time"]

        if pd.isna(end_time):
            continue

        mask = (
            (attendance["trainer_id"] == trainer) &
            (attendance["member_id"] == member) &
            (attendance["zone"] == zone)
        )
        filtered_att = attendance[mask]

        if not filtered_att.empty:
            actual_last = filtered_att["timestamp"].max()
            if pd.isna(actual_last):
                continue

            diff_min = (actual_last - end_time).total_seconds() / 60
            if diff_min >= TOLERANCE_MINUTES:
                violations.append({
                    "trainer_id": trainer,
                    "member_id": member,
                    "zone": zone,
                    "violation_type": "Extended Session",
                    "official_start_time": start_time,
                    "official_end_time": end_time,
                    "timestamp": actual_last,
                    "overtime_minutes": round(diff_min, 2),
                    "details": "Trainer extended session beyond official end time"
                })
        else:
            print(f"⚠ No attendance found for session: {trainer}, {member}, {zone}")
    return violations

def detect_unauthorized_services(sessions, attendance):
    violations = []

    for _, att in attendance.iterrows():
        trainer = att["trainer_id"]
        member = att["member_id"]
        zone = att["zone"]
        ts = att["timestamp"]

        mask = (
            (sessions["trainer_id"] == trainer) &
            (sessions["member_id"] == member) &
            (sessions["zone"] == zone) &
            (sessions["start_time"] <= ts) &
            (sessions["end_time"] + pd.Timedelta(minutes=TOLERANCE_MINUTES) >= ts)
        )

        if mask.sum() == 0:
            violations.append({
                "trainer_id": trainer,
                "member_id": member,
                "zone": zone,
                "violation_type": "Unauthorized Extra Service",
                "official_start_time": None,
                "official_end_time": None,
                "timestamp": ts,
                "overtime_minutes": None,
                "details": "Zone not booked or outside official session time"
            })
    return violations

def detect_direct_payments(payments):
    violations = []

    for _, row in payments.iterrows():
        if str(row.get("approved_by_gym", "No")).lower() != "yes":
            violations.append({
                "trainer_id": row.get("trainer_id"),
                "member_id": row.get("member_id"),
                "zone": None,
                "violation_type": "Direct Payment",
                "official_start_time": None,
                "official_end_time": None,
                "timestamp": row.get("timestamp"),
                "overtime_minutes": None,
                "details": f"Trainer received direct payment of {row.get('amount')} not approved by gym"
            })
    return violations

def detect_unauthorized_interactions(sessions, attendance):
    violations = []

    for _, att in attendance.iterrows():
        trainer = att["trainer_id"]
        member = att["member_id"]
        zone = att["zone"]
        ts = att["timestamp"]

        mask = (
            (sessions["trainer_id"] == trainer) &
            (sessions["member_id"] == member) &
            (sessions["start_time"] <= ts) &
            (sessions["end_time"] + pd.Timedelta(minutes=TOLERANCE_MINUTES) >= ts)
        )

        if mask.sum() == 0:
            violations.append({
                "trainer_id": trainer,
                "member_id": member,
                "zone": zone,
                "violation_type": "Unauthorized Interaction",
                "official_start_time": None,
                "official_end_time": None,
                "timestamp": ts,
                "overtime_minutes": None,
                "details": "Trainer interacted with member outside any official session"
            })
    return violations

def main():
    sessions = read_csv_clean(SESSIONS_FILE, datetime_cols=["start_time","end_time"],
                              str_cols=["trainer_id","member_id","zone"])
    attendance = read_csv_clean(ATTENDANCE_FILE, datetime_cols=["timestamp"],
                                str_cols=["trainer_id","member_id","zone"])
    payments = read_csv_clean(PAYMENTS_FILE, datetime_cols=["timestamp"],
                              str_cols=["trainer_id","member_id"])

    if sessions.empty and attendance.empty and payments.empty:
        print("❌ No data available.")
        return

    violations = []
    violations += detect_extended_sessions(sessions, attendance)
    violations += detect_unauthorized_services(sessions, attendance)
    violations += detect_unauthorized_interactions(sessions, attendance)
    violations += detect_direct_payments(payments)

    df = pd.DataFrame(violations, columns=OUTPUT_COLUMNS)
    df.to_csv(OUTPUT_FILE, index=False)

    if not df.empty:
        print(f"⚠ Detected {len(df)} violation(s):")
        print(df)
    else:
        print("✅ No violations detected.")

if __name__ == "__main__":
    main()
