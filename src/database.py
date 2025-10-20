import sqlite3
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for Hell Divers 2 data"""

    def __init__(self, db_path: str = "helldivers2.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # War status table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS war_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """
            )

            # Statistics table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_players INTEGER,
                    total_kills INTEGER,
                    missions_won INTEGER,
                    data TEXT NOT NULL
                )
            """
            )

            # Planet status table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS planet_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    planet_index INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    planet_name TEXT,
                    owner TEXT,
                    status TEXT,
                    data TEXT NOT NULL
                )
            """
            )

            # Campaigns table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    planet_index INTEGER,
                    status TEXT,
                    data TEXT NOT NULL
                )
            """
            )

            # Assignments table (Major Orders)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """
            )

            # Dispatches table (News/Announcements)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dispatches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dispatch_id INTEGER UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """
            )

            # Planet events table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS planet_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER UNIQUE,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    data TEXT NOT NULL
                )
            """
            )

            # Index for faster queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_war_timestamp ON war_status(timestamp)")
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_stats_timestamp ON statistics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_planet_index ON planet_status(planet_index)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignment_timestamp ON assignments(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_dispatch_timestamp ON dispatches(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_event_timestamp ON planet_events(timestamp)")

            conn.commit()

    def save_war_status(self, data: Dict) -> bool:
        """Save war status to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO war_status (data) VALUES (?)", (json.dumps(data),))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save war status: {e}")
            return False

    def save_statistics(self, data: Dict) -> bool:
        """Save statistics to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                total_players = data.get("total_players", 0)
                total_kills = data.get("total_kills", 0)
                missions_won = data.get("missions_won", 0)

                cursor.execute(
                    "INSERT INTO statistics (total_players, total_kills, missions_won, data) VALUES (?, ?, ?, ?)",
                    (total_players, total_kills, missions_won, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
            return False

    def save_planet_status(self, planet_index: int, data: Dict) -> bool:
        """Save planet status to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                planet_name = data.get("name", "Unknown")
                owner = data.get("owner", "Unknown")
                status = data.get("status", "Unknown")

                cursor.execute(
                    "INSERT INTO planet_status (planet_index, planet_name, owner, status, data) VALUES (?, ?, ?, ?, ?)",
                    (planet_index, planet_name, owner, status, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save planet status: {e}")
            return False

    def save_campaign(self, campaign_id: int, planet_index: int, data: Dict) -> bool:
        """Save campaign to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                status = data.get("status", "Unknown")

                cursor.execute(
                    "INSERT OR REPLACE INTO campaigns (campaign_id, planet_index, status, data) VALUES (?, ?, ?, ?)",
                    (campaign_id, planet_index, status, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save campaign: {e}")
            return False

    def get_latest_war_status(self) -> Optional[Dict]:
        """Get the latest war status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM war_status ORDER BY timestamp DESC LIMIT 1")
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logger.error(f"Failed to get latest war status: {e}")
            return None

    def get_latest_statistics(self) -> Optional[Dict]:
        """Get the latest statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM statistics ORDER BY timestamp DESC LIMIT 1")
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logger.error(f"Failed to get latest statistics: {e}")
            return None

    def get_planet_status_history(self, planet_index: int, limit: int = 10) -> List[Dict]:
        """Get status history for a planet"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data, timestamp FROM planet_status WHERE planet_index = ? ORDER BY timestamp DESC LIMIT ?",
                    (planet_index, limit),
                )
                results = cursor.fetchall()
                return [{"data": json.loads(row[0]), "timestamp": row[1]} for row in results]
        except Exception as e:
            logger.error(f"Failed to get planet status history: {e}")
            return []

    def get_statistics_history(self, limit: int = 100) -> List[Dict]:
        """Get statistics history"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data, timestamp FROM statistics ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                results = cursor.fetchall()
                return [{"data": json.loads(row[0]), "timestamp": row[1]} for row in results]
        except Exception as e:
            logger.error(f"Failed to get statistics history: {e}")
            return []

    def get_active_campaigns(self) -> List[Dict]:
        """Get all active campaigns"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM campaigns WHERE status = ? ORDER BY timestamp DESC",
                    ("active",),
                )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Failed to get active campaigns: {e}")
            return []

    def save_assignments(self, data: List[Dict]) -> bool:
        """Save assignments (Major Orders) to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for assignment in data:
                    assignment_id = assignment.get("id")
                    if assignment_id:
                        cursor.execute(
                            "INSERT OR REPLACE INTO assignments (assignment_id, data) VALUES (?, ?)",
                            (assignment_id, json.dumps(assignment)),
                        )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save assignments: {e}")
            return False

    def save_dispatches(self, data: List[Dict]) -> bool:
        """Save dispatches (news/announcements) to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for dispatch in data:
                    dispatch_id = dispatch.get("id")
                    if dispatch_id:
                        cursor.execute(
                            "INSERT OR REPLACE INTO dispatches (dispatch_id, data) VALUES (?, ?)",
                            (dispatch_id, json.dumps(dispatch)),
                        )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save dispatches: {e}")
            return False

    def save_planet_events(self, data: List[Dict]) -> bool:
        """Save planet events to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for event in data:
                    event_id = event.get("id")
                    if event_id:
                        cursor.execute(
                            "INSERT OR REPLACE INTO planet_events (event_id, data) VALUES (?, ?)",
                            (event_id, json.dumps(event)),
                        )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save planet events: {e}")
            return False

    def get_latest_assignments(self, limit: int = 10) -> List[Dict]:
        """Get latest assignments"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM assignments ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Failed to get latest assignments: {e}")
            return []

    def get_latest_dispatches(self, limit: int = 10) -> List[Dict]:
        """Get latest dispatches"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM dispatches ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Failed to get latest dispatches: {e}")
            return []

    def get_latest_planet_events(self, limit: int = 10) -> List[Dict]:
        """Get latest planet events"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM planet_events ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Failed to get latest planet events: {e}")
            return []
