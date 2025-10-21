from collections import defaultdict
import datetime
from .config import MIN_SESSION_SECONDS, MAX_SESSION_GAP_SECONDS


class SessionBuilder:
    def __init__(self):
        # track_id -> {last_seen_ts, last_bbox, face_uuid, history: [(ts, zone, uuid)]}
        self.tracks = {}
        self.active_sessions = [] 

    def update_tracks(self, tracked_objs, timestamp, camera_zone):
        """
        Update tracking info from each processed frame or detection batch.
        Args:
            tracked_objs: [{'track_id', 'bbox', 'face_uuid'}]
            timestamp: datetime.datetime object
            camera_zone: str, e.g. 'GYM_FLOOR', 'ENTRY', 'EXIT'
        """
        for t in tracked_objs:
            tid = t['track_id']
            self.tracks.setdefault(tid, {'history': []})
            self.tracks[tid]['last_seen'] = timestamp
            self.tracks[tid]['bbox'] = t['bbox']
            if 'face_uuid' in t:
                self.tracks[tid]['face_uuid'] = t['face_uuid']
            self.tracks[tid]['history'].append((timestamp, camera_zone, t.get('face_uuid')))

    def build_sessions(self, trainer_profiles, member_profiles):
        """
        Build sessions based on co-presence of trainer and member within a time window.

        trainer_profiles: dict {uuid -> {...}}
        member_profiles: dict {uuid -> {...}}

        Returns:
            list of session dicts with timestamps, duration, trainer_uuid, member_uuid
        """
        sessions = []

        uuid_histories = defaultdict(list)
        for track_id, tinfo in self.tracks.items():
            for (ts, zone, uuid) in tinfo['history']:
                if uuid:
                    uuid_histories[uuid].append((ts, zone))

        for uuid in uuid_histories:
            uuid_histories[uuid].sort(key=lambda x: x[0])

        trainer_uuids = set(trainer_profiles.keys())
        member_uuids = set(member_profiles.keys())

        for trainer_uuid in trainer_uuids:
            for member_uuid in member_uuids:
                t_hist = uuid_histories.get(trainer_uuid, [])
                m_hist = uuid_histories.get(member_uuid, [])
                if not t_hist or not m_hist:
                    continue

                i, j = 0, 0
                start_ts, end_ts = None, None
                while i < len(t_hist) and j < len(m_hist):
                    t_ts, _ = t_hist[i]
                    m_ts, _ = m_hist[j]
                    diff = abs((t_ts - m_ts).total_seconds())

                    if diff <= MAX_SESSION_GAP_SECONDS:
                        if start_ts is None:
                            start_ts = min(t_ts, m_ts)
                        end_ts = max(t_ts, m_ts)
                    elif start_ts:
                        duration = (end_ts - start_ts).total_seconds()
                        if duration >= MIN_SESSION_SECONDS:
                            sessions.append({
                                'trainer_uuid': trainer_uuid,
                                'member_uuid': member_uuid,
                                'start_ts': start_ts,
                                'end_ts': end_ts,
                                'duration_sec': duration,
                            })
                        start_ts = end_ts = None

                    if t_ts < m_ts:
                        i += 1
                    else:
                        j += 1

                if start_ts:
                    duration = (end_ts - start_ts).total_seconds()
                    if duration >= MIN_SESSION_SECONDS:
                        sessions.append({
                            'trainer_uuid': trainer_uuid,
                            'member_uuid': member_uuid,
                            'start_ts': start_ts,
                            'end_ts': end_ts,
                            'duration_sec': duration,
                        })

        self.active_sessions = sessions
        return sessions
