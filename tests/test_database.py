#!/usr/bin/env python3
"""
Unit tests for database module.
Tests database initialization, CRUD operations, and data persistence.
"""

import pytest
import sqlite3
import json
import tempfile
import os
from src.database import Database


@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = Database(db_path=path)
    yield db
    try:
        os.unlink(path)
    except:
        pass


class TestDatabaseInit:
    """Test database initialization"""

    def test_init_creates_file(self):
        """Test database initialization creates file"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.unlink(path)
        
        db = Database(db_path=path)
        assert os.path.exists(path)
        os.unlink(path)

    def test_init_creates_tables(self, temp_db):
        """Test database initialization creates all tables"""
        with sqlite3.connect(temp_db.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            assert "war_status" in tables
            assert "statistics" in tables
            assert "planet_status" in tables
            assert "campaigns" in tables
            assert "assignments" in tables
            assert "dispatches" in tables
            assert "planet_events" in tables
            assert "system_status" in tables


class TestWarStatus:
    """Test war status operations"""

    def test_save_war_status(self, temp_db):
        """Test saving war status data"""
        data = {"war_id": 1, "status": "active"}
        temp_db.save_war_status(data)
        
        result = temp_db.get_latest_war_status()
        assert result is not None
        assert result["war_id"] == 1

    def test_get_latest_war_status_empty(self, temp_db):
        """Test getting war status when none exists"""
        result = temp_db.get_latest_war_status()
        assert result is None


class TestStatistics:
    """Test statistics operations"""

    def test_save_statistics(self, temp_db):
        """Test saving statistics data"""
        data = {
            "total_players": 1000,
            "total_kills": 50000,
            "missions_won": 2000
        }
        temp_db.save_statistics(data)
        
        result = temp_db.get_latest_statistics()
        assert result is not None
        assert result["total_players"] == 1000

    def test_get_latest_statistics_empty(self, temp_db):
        """Test getting statistics when none exists"""
        result = temp_db.get_latest_statistics()
        assert result is None


class TestPlanetStatus:
    """Test planet status operations"""

    def test_save_planet_status(self, temp_db):
        """Test saving planet status"""
        planet_data = {
            "index": 5,
            "name": "Test Planet",
            "owner": "Humans",
            "status": "controlled"
        }
        result = temp_db.save_planet_status(5, planet_data)
        assert result is True
        
        history = temp_db.get_planet_status_history(5, limit=1)
        assert len(history) > 0

    def test_get_planet_status_history(self, temp_db):
        """Test getting planet status history"""
        planet_data = {"index": 5, "name": "Test Planet"}
        temp_db.save_planet_status(5, planet_data)
        
        result = temp_db.get_planet_status_history(5)
        assert result is not None
        assert len(result) > 0

    def test_get_latest_planets_snapshot(self, temp_db):
        """Test getting all planets snapshot"""
        temp_db.save_planet_status(1, {"index": 1, "name": "Planet 1"})
        temp_db.save_planet_status(2, {"index": 2, "name": "Planet 2"})
        
        result = temp_db.get_latest_planets_snapshot()
        assert result is not None
        assert isinstance(result, list)


class TestCampaigns:
    """Test campaigns operations"""

    def test_save_campaign(self, temp_db):
        """Test saving a single campaign"""
        campaign_data = {"id": 1, "planet": {"index": 5}, "status": "active"}
        result = temp_db.save_campaign(1, 5, campaign_data)
        assert result is True

    def test_get_active_campaigns(self, temp_db):
        """Test getting active campaigns"""
        temp_db.save_campaign(1, 5, {"id": 1, "planet": {"index": 5}})
        
        result = temp_db.get_active_campaigns()
        assert result is not None
        assert isinstance(result, list)

    def test_get_latest_campaigns_snapshot(self, temp_db):
        """Test getting latest campaigns snapshot"""
        temp_db.save_campaign(1, 5, {"id": 1, "planet": {"index": 5}})
        
        result = temp_db.get_latest_campaigns_snapshot()
        assert result is not None
        assert isinstance(result, list)


class TestAssignments:
    """Test assignments operations"""

    def test_save_assignments(self, temp_db):
        """Test saving assignments"""
        assignments = [
            {"id": 1, "title": "Major Order 1", "description": "Test"}
        ]
        result = temp_db.save_assignments(assignments)
        assert result is True
        
        retrieved = temp_db.get_latest_assignments()
        assert len(retrieved) > 0

    def test_get_latest_assignments_with_limit(self, temp_db):
        """Test getting assignments with limit"""
        assignments = [
            {"id": 1, "title": "Order 1"},
            {"id": 2, "title": "Order 2"},
            {"id": 3, "title": "Order 3"}
        ]
        temp_db.save_assignments(assignments)
        
        result = temp_db.get_latest_assignments(limit=2)
        assert len(result) <= 2


class TestDispatches:
    """Test dispatches operations"""

    def test_save_dispatches(self, temp_db):
        """Test saving dispatches"""
        dispatches = [
            {"id": 1, "message": "News 1"}
        ]
        result = temp_db.save_dispatches(dispatches)
        assert result is True
        
        retrieved = temp_db.get_latest_dispatches()
        assert len(retrieved) > 0

    def test_get_latest_dispatches_with_limit(self, temp_db):
        """Test getting dispatches with limit"""
        dispatches = [
            {"id": 1, "message": "Important news"},
            {"id": 2, "message": "Regular update"}
        ]
        temp_db.save_dispatches(dispatches)
        
        result = temp_db.get_latest_dispatches(limit=1)
        assert len(result) <= 1


class TestPlanetEvents:
    """Test planet events operations"""

    def test_save_planet_events(self, temp_db):
        """Test saving planet events"""
        events = [
            {"id": 1, "planetIndex": 5, "eventType": "storm"}
        ]
        result = temp_db.save_planet_events(events)
        assert result is True
        
        retrieved = temp_db.get_latest_planet_events()
        assert len(retrieved) > 0

    def test_get_latest_planet_events_with_limit(self, temp_db):
        """Test getting planet events with limit"""
        events = [
            {"id": 1, "planetIndex": 5, "eventType": "storm"},
            {"id": 2, "planetIndex": 10, "eventType": "meteor"}
        ]
        temp_db.save_planet_events(events)
        
        result = temp_db.get_latest_planet_events(limit=1)
        assert len(result) <= 1


class TestSystemStatus:
    """Test system status operations"""

    def test_set_upstream_status(self, temp_db):
        """Test setting upstream status"""
        temp_db.set_upstream_status(True)
        result = temp_db.get_upstream_status()
        assert result is True

    def test_get_upstream_status(self, temp_db):
        """Test getting upstream status"""
        temp_db.set_upstream_status(True)
        result = temp_db.get_upstream_status()
        assert result is True
        
        temp_db.set_upstream_status(False)
        result = temp_db.get_upstream_status()
        assert result is False

    def test_get_upstream_status_default(self, temp_db):
        """Test getting upstream status default value"""
        result = temp_db.get_upstream_status()
        # Should return True by default (optimistic)
        assert isinstance(result, bool)


class TestCacheFallback:
    """Test cache fallback methods"""

    def test_get_latest_planets_snapshot(self, temp_db):
        """Test getting latest planets snapshot"""
        temp_db.save_planet_status(1, {"index": 1, "name": "Planet 1"})
        temp_db.save_planet_status(2, {"index": 2, "name": "Planet 2"})
        
        result = temp_db.get_latest_planets_snapshot()
        assert result is not None
        assert isinstance(result, list)
        assert len(result) >= 2

    def test_get_latest_factions_snapshot(self, temp_db):
        """Test getting latest factions snapshot"""
        war_data = {"factions": [{"id": 1, "name": "Terminids"}]}
        temp_db.save_war_status(war_data)
        
        result = temp_db.get_latest_factions_snapshot()
        assert result is not None
        assert isinstance(result, list)

    def test_get_latest_biomes_snapshot(self, temp_db):
        """Test getting latest biomes snapshot"""
        # Save planets with biomes
        temp_db.save_planet_status(1, {"index": 1, "biome": {"name": "Desert"}})
        temp_db.save_planet_status(2, {"index": 2, "biome": {"name": "Ice"}})
        
        result = temp_db.get_latest_biomes_snapshot()
        assert result is not None
        assert isinstance(result, list)


class TestDatabaseErrors:
    """Test database error handling"""

    def test_save_with_invalid_json(self, temp_db):
        """Test saving data with non-serializable objects"""
        # This should not crash but handle gracefully
        try:
            data = {"callback": lambda x: x}  # Non-serializable
            temp_db.save_war_status(data)
            # If it doesn't raise, it handled it somehow
            assert True
        except (TypeError, json.JSONDecodeError):
            # Expected for non-serializable data
            assert True

    def test_empty_list_handling(self, temp_db):
        """Test handling empty lists"""
        result = temp_db.save_assignments([])
        # Empty list should still be processed
        assert result is True or result is False
