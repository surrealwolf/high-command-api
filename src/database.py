import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for Hell Divers 2 API data"""

    def __init__(self, db_path: str = "helldivers2.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # War Status Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS war_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Statistics Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Planet Status Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS planet_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    planet_index INTEGER UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Campaigns Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS campaigns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id INTEGER UNIQUE NOT NULL,
                    planet_index INTEGER,
                    status TEXT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Assignments Table (Major Orders)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS assignments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assignment_id INTEGER UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Dispatches Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS dispatches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dispatch_id INTEGER UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Planet Events Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS planet_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER UNIQUE NOT NULL,
                    planet_index INTEGER,
                    event_type TEXT,
                    data TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # System Status Table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS system_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            # Create indexes for frequently queried columns
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_war_status_timestamp ON war_status(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_statistics_timestamp ON statistics(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_planet_status_index ON planet_status(planet_index)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_campaigns_timestamp ON campaigns(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_assignments_timestamp ON assignments(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_dispatches_timestamp ON dispatches(timestamp)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_planet_events_index ON planet_events(planet_index)"
            )

            conn.commit()

    def save_war_status(self, data: Dict) -> bool:
        """Save war status to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO war_status (data) VALUES (?)", (json.dumps(data),)
                )
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
                cursor.execute(
                    "INSERT INTO statistics (data) VALUES (?)", (json.dumps(data),)
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
            return False

    def save_planet_status(self, planet_index: int, data: Dict) -> bool:
        """Save or update planet status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO planet_status (planet_index, data) VALUES (?, ?)",
                    (planet_index, json.dumps(data)),
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
                # Campaigns from the API are active by definition
                status = "active"

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
            logger.error(f"Failed to get war status: {e}")
            return None

    def get_latest_statistics(self) -> Optional[Dict]:
        """Get the latest statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM statistics ORDER BY timestamp DESC LIMIT 1"
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return None

    def get_planet_status(self, planet_index: int) -> Optional[Dict]:
        """Get planet status by index"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT data FROM planet_status WHERE planet_index = ?",
                    (planet_index,),
                )
                result = cursor.fetchone()
                return json.loads(result[0]) if result else None
        except Exception as e:
            logger.error(f"Failed to get planet status: {e}")
            return None

    def get_latest_campaigns_snapshot(self) -> Optional[List[Dict]]:
        """Get latest campaigns snapshot from cache"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT data FROM campaigns ORDER BY timestamp DESC LIMIT 50"
                )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results] if results else None
        except Exception as e:
            logger.error(f"Failed to get campaigns snapshot: {e}")
            return None

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

    def get_assignment(self, limit: int = 10) -> List[Dict]:
        """Get assignments with optional limit"""
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
            logger.error(f"Failed to get assignments: {e}")
            return []

    def save_assignment(self, assignment_id: int, data: Dict) -> bool:
        """Save assignment to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO assignments (assignment_id, data) VALUES (?, ?)",
                    (assignment_id, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save assignment: {e}")
            return False

    def save_dispatch(self, dispatch_id: int, data: Dict) -> bool:
        """Save dispatch to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO dispatches (dispatch_id, data) VALUES (?, ?)",
                    (dispatch_id, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save dispatch: {e}")
            return False

    def get_dispatches(self, limit: int = 10) -> List[Dict]:
        """Get dispatches with optional limit"""
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
            logger.error(f"Failed to get dispatches: {e}")
            return []

    def save_planet_event(self, event_id: int, planet_index: int, event_type: str, data: Dict) -> bool:
        """Save planet event to database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO planet_events (event_id, planet_index, event_type, data) VALUES (?, ?, ?, ?)",
                    (event_id, planet_index, event_type, json.dumps(data)),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to save planet event: {e}")
            return False

    def get_planet_events(
        self, planet_index: Optional[int] = None, limit: int = 10
    ) -> List[Dict]:
        """Get planet events with optional filtering"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if planet_index:
                    cursor.execute(
                        "SELECT data FROM planet_events WHERE planet_index = ? ORDER BY timestamp DESC LIMIT ?",
                        (planet_index, limit),
                    )
                else:
                    cursor.execute(
                        "SELECT data FROM planet_events ORDER BY timestamp DESC LIMIT ?",
                        (limit,),
                    )
                results = cursor.fetchall()
                return [json.loads(row[0]) for row in results]
        except Exception as e:
            logger.error(f"Failed to get planet events: {e}")
            return []

    def update_system_status(self, key: str, value: str) -> bool:
        """Update system status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT OR REPLACE INTO system_status (key, value) VALUES (?, ?)",
                    (key, value),
                )
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update system status: {e}")
            return False

    def get_system_status(self, key: str) -> Optional[str]:
        """Get system status value"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT value FROM system_status WHERE key = ?", (key,))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return None
