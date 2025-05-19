# session_tracker.py
import pandas as pd


class SessionTracker:
    def __init__(self):
        self.sessions = []

    def add_session(self, duration, poses, avg_hr=None):
        session = {
            'date': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M"),
            'duration': round(float(duration), 1),
            'poses': ', '.join(poses),
            'avg_hr': avg_hr,
            'calories': self._estimate_calories(duration)
        }
        self.sessions.append(session)

    def get_stats(self):
        if not self.sessions:
            return {
                'total_sessions': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'fav_pose': 'N/A'
            }

        df = pd.DataFrame(self.sessions)
        return {
            'total_sessions': len(df),
            'total_duration': round(df['duration'].sum(), 1),
            'avg_duration': round(df['duration'].mean(), 1),
            'fav_pose': df['poses'].mode()[0] if not df['poses'].empty else 'N/A'
        }

    def _estimate_calories(self, duration):
        return round(float(duration) * 3, 1)  # 3 kcal/min estimation

    def get_history_df(self):
        return pd.DataFrame(self.sessions) if self.sessions else pd.DataFrame()