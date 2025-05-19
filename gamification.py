# gamification.py
import json
from datetime import datetime, timedelta
import random
from pathlib import Path


class YogaGamification:
    def __init__(self, user_id):
        self.user_id = user_id
        self.data_path = Path(f"data/gamification/{user_id}.json")
        self.default_data = {
            "points": 0,
            "level": 1,
            "streak": 0,
            "achievements": {},
            "active_powerups": [],
            "daily_challenges": {},
            "cosmetic_inventory": [],
            "leaderboard_position": 0,
            "last_session_date": None
        }
        self.load_data()

        # Configure challenges and achievements
        self.ACHIEVEMENTS = {
            "zen_master": {"name": "Zen Master", "threshold": 1000, "points": 100},
            "pose_collector": {"name": "Pose Collector", "threshold": 5, "points": 50},
            "daily_streaker": {"name": "Daily Streaker", "threshold": 7, "points": 75}
        }

        self.DAILY_CHALLENGES = [
            {"id": "morning_yogi", "name": "Morning Practice", "condition": lambda s: s["start_time"].hour < 9},
            {"id": "weekend_warrior", "name": "Weekend Warrior",
             "condition": lambda s: s["start_time"].weekday() >= 5},
            {"id": "precision_pro", "name": "Precision Pro",
             "condition": lambda s: s["avg_accuracy"] > 85}
        ]

    def load_data(self):
        try:
            with open(self.data_path, "r") as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = self.default_data.copy()

    def save_data(self):
        self.data_path.parent.mkdir(exist_ok=True, parents=True)
        with open(self.data_path, "w") as f:
            json.dump(self.data, f)

    def update_streak(self, session_date):
        if self.data["last_session_date"]:
            last_date = datetime.fromisoformat(self.data["last_session_date"])
            if session_date - last_date == timedelta(days=1):
                self.data["streak"] += 1
            elif session_date - last_date > timedelta(days=1):
                self.data["streak"] = 1
        else:
            self.data["streak"] = 1
        self.data["last_session_date"] = session_date.isoformat()

    def award_points(self, session_data):
        base_points = session_data["duration"] // 5  # 1 point per 5 seconds
        accuracy_bonus = int(session_data["avg_accuracy"] // 10)
        streak_bonus = self.data["streak"] * 2
        total = base_points + accuracy_bonus + streak_bonus
        self.data["points"] += total
        return total

    def check_achievements(self, session_data):
        new_achievements = []

        # Pose-based achievements
        pose_count = len(self.data["achievements"].get("poses_collected", []))
        if pose_count >= self.ACHIEVEMENTS["pose_collector"]["threshold"]:
            if not self.data["achievements"].get("pose_collector"):
                new_achievements.append("pose_collector")

        # Daily streak achievement
        if self.data["streak"] >= self.ACHIEVEMENTS["daily_streaker"]["threshold"]:
            if not self.data["achievements"].get("daily_streaker"):
                new_achievements.append("daily_streaker")

        # Award new achievements
        for achievement in new_achievements:
            self.data["achievements"][achievement] = datetime.now().isoformat()
            self.data["points"] += self.ACHIEVEMENTS[achievement]["points"]

        return new_achievements

    def generate_daily_challenge(self):
        today = datetime.now().date().isoformat()
        if today not in self.data["daily_challenges"]:
            challenge = random.choice(self.DAILY_CHALLENGES)
            self.data["daily_challenges"][today] = {
                "challenge": challenge,
                "completed": False,
                "rewarded": False
            }
        return self.data["daily_challenges"][today]

    def check_challenges(self, session_data):
        completed = []
        for date, challenge_data in self.data["daily_challenges"].items():
            if not challenge_data["completed"]:
                if challenge_data["challenge"]["condition"](session_data):
                    challenge_data["completed"] = True
                    completed.append(challenge_data["challenge"]["name"])
        return completed

    def level_up(self):
        xp_needed = self.data["level"] * 100
        if self.data["points"] >= xp_needed:
            self.data["level"] += 1
            self.data["points"] -= xp_needed
            return True
        return False

    def get_random_powerup(self):
        powerups = [
            {"name": "Double Points", "effect": "double_points", "duration": 3600},
            {"name": "Accuracy Boost", "effect": "accuracy_boost", "duration": 1800},
            {"name": "Streak Shield", "effect": "streak_shield", "duration": 86400}
        ]
        return random.choice(powerups)

    def unlock_cosmetic(self):
        cosmetics = [
            "Golden Warrior Skin",
            "Animated Pose Effects",
            "Exclusive Meditation Music",
            "Avatar Customization Pack"
        ]
        unlocked = random.choice(cosmetics)
        if unlocked not in self.data["cosmetic_inventory"]:
            self.data["cosmetic_inventory"].append(unlocked)
            return unlocked
        return None

    def update_leaderboard(self, global_leaderboard):
        # This would interface with a database in production
        global_leaderboard.append({
            "user": self.user_id,
            "level": self.data["level"],
            "points": self.data["points"]
        })
        sorted_leaderboard = sorted(global_leaderboard,
                                    key=lambda x: (-x["level"], -x["points"]))
        self.data["leaderboard_position"] = sorted_leaderboard.index(
            next(u for u in sorted_leaderboard if u["user"] == self.user_id)) + 1
        return sorted_leaderboard[:10]