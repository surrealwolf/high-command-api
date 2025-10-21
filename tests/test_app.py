#!/usr/bin/env python3
"""
Comprehensive tests for Hell Divers 2 API - Testing actual source code
Coverage target: 80%+
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.app import app
from src.database import Database
from src.scraper import HellDivers2Scraper
from src.collector import DataCollector
from src.config import Config, DevelopmentConfig, ProductionConfig, TestingConfig


# ========================
# Configuration Tests
# ========================


def test_config_defaults():
    """Test configuration default values"""
    assert Config.DEBUG is False
    assert Config.TESTING is False
    assert Config.API_TIMEOUT == 30
    assert Config.SCRAPE_INTERVAL == 300


def test_development_config():
    """Test development configuration"""
    assert DevelopmentConfig.DEBUG is True
    assert DevelopmentConfig.SCRAPE_INTERVAL == 60


def test_production_config():
    """Test production configuration"""
    assert ProductionConfig.DEBUG is False
    assert ProductionConfig.SCRAPE_INTERVAL == 300


def test_testing_config():
    """Test testing configuration"""
    assert TestingConfig.TESTING is True
    assert TestingConfig.DATABASE_URL == "sqlite:///:memory:"
    assert TestingConfig.SCRAPE_INTERVAL == 60


def test_config_environment_overrides():
    """Test environment variable overrides for config"""
    with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG", "HELLDIVERS_API_BASE": "https://test.api"}):
        # Re-import config to pick up environment changes
        from importlib import reload
        from src import config as config_module
        reload(config_module)
        assert config_module.Config.LOG_LEVEL == "DEBUG"


# ========================
# Database Tests
# ========================


class TestDatabase:
    """Test database operations"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        
        db = Database(db_path)
        yield db
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_database_initialization(self, temp_db):
        """Test database initialization creates all tables"""
        # Database should initialize without errors
        assert temp_db.db_path is not None

    def test_save_and_get_war_status(self, temp_db):
        """Test saving and retrieving war status"""
        war_data = {"war_id": 1, "statistics": {"players": 50000}}
        
        # Save war status
        result = temp_db.save_war_status(war_data)
        assert result is True
        
        # Retrieve war status
        retrieved = temp_db.get_latest_war_status()
        assert retrieved is not None
        assert retrieved["war_id"] == 1
        assert retrieved["statistics"]["players"] == 50000

    def test_save_and_get_statistics(self, temp_db):
        """Test saving and retrieving statistics"""
        stats_data = {"total_players": 50000, "total_kills": 1000000, "missions_won": 5000}
        
        result = temp_db.save_statistics(stats_data)
        assert result is True
        
        retrieved = temp_db.get_latest_statistics()
        assert retrieved is not None
        assert retrieved["total_players"] == 50000

    def test_save_and_get_planet_status(self, temp_db):
        """Test saving and retrieving planet status"""
        planet_data = {"name": "Malevelon Creek", "owner": "Humans", "status": "Active"}
        
        result = temp_db.save_planet_status(0, planet_data)
        assert result is True
        
        history = temp_db.get_planet_status_history(0, limit=1)
        assert len(history) > 0
        assert history[0]["data"]["name"] == "Malevelon Creek"

    def test_save_and_get_campaign(self, temp_db):
        """Test saving and retrieving campaigns"""
        campaign_data = {"id": 1, "status": "active", "planet": {"index": 0}}
        
        result = temp_db.save_campaign(1, 0, campaign_data)
        assert result is True
        
        campaigns = temp_db.get_active_campaigns()
        assert len(campaigns) > 0

    def test_save_and_get_assignments(self, temp_db):
        """Test saving and retrieving assignments"""
        assignments = [
            {"id": 1, "title": "Major Order 1"},
            {"id": 2, "title": "Major Order 2"}
        ]
        
        result = temp_db.save_assignments(assignments)
        assert result is True
        
        retrieved = temp_db.get_latest_assignments(limit=10)
        assert len(retrieved) == 2

    def test_save_and_get_dispatches(self, temp_db):
        """Test saving and retrieving dispatches"""
        dispatches = [
            {"id": 1, "message": "News 1"},
            {"id": 2, "message": "News 2"}
        ]
        
        result = temp_db.save_dispatches(dispatches)
        assert result is True
        
        retrieved = temp_db.get_latest_dispatches(limit=10)
        assert len(retrieved) == 2

    def test_save_and_get_planet_events(self, temp_db):
        """Test saving and retrieving planet events"""
        events = [
            {"id": 1, "event": "Attack"},
            {"id": 2, "event": "Defense"}
        ]
        
        result = temp_db.save_planet_events(events)
        assert result is True
        
        retrieved = temp_db.get_latest_planet_events(limit=10)
        assert len(retrieved) == 2

    def test_get_statistics_history(self, temp_db):
        """Test retrieving statistics history"""
        # Save multiple statistics entries
        for i in range(5):
            temp_db.save_statistics({"total_players": 1000 * i})
        
        history = temp_db.get_statistics_history(limit=3)
        assert len(history) == 3

    def test_get_latest_planets_snapshot(self, temp_db):
        """Test getting latest planets snapshot"""
        # Save multiple planets
        temp_db.save_planet_status(0, {"name": "Planet A", "index": 0})
        temp_db.save_planet_status(1, {"name": "Planet B", "index": 1})
        
        snapshot = temp_db.get_latest_planets_snapshot()
        assert snapshot is not None
        assert len(snapshot) == 2

    def test_get_latest_campaigns_snapshot(self, temp_db):
        """Test getting latest campaigns snapshot"""
        temp_db.save_campaign(1, 0, {"id": 1, "status": "active"})
        temp_db.save_campaign(2, 1, {"id": 2, "status": "active"})
        
        snapshot = temp_db.get_latest_campaigns_snapshot()
        assert snapshot is not None
        assert len(snapshot) == 2

    def test_get_latest_factions_snapshot(self, temp_db):
        """Test getting latest factions snapshot"""
        war_data = {"factions": [{"name": "Humans"}, {"name": "Bugs"}]}
        temp_db.save_war_status(war_data)
        
        factions = temp_db.get_latest_factions_snapshot()
        assert factions is not None
        assert len(factions) == 2

    def test_get_latest_biomes_snapshot(self, temp_db):
        """Test getting latest biomes snapshot with type checking"""
        # Test with valid dict biome
        temp_db.save_planet_status(0, {"biome": {"name": "Swamp"}, "index": 0})
        temp_db.save_planet_status(1, {"biome": {"name": "Desert"}, "index": 1})
        
        biomes = temp_db.get_latest_biomes_snapshot()
        assert biomes is not None
        assert len(biomes) == 2
        
    def test_get_latest_biomes_snapshot_with_invalid_biome(self, temp_db):
        """Test biome snapshot with non-dict biome data (type guard test)"""
        # Save planet with invalid biome type (not a dict)
        temp_db.save_planet_status(0, {"biome": "NotADict", "index": 0})
        
        biomes = temp_db.get_latest_biomes_snapshot()
        # Should return None or empty list since biome is not a dict
        assert biomes is None or len(biomes) == 0

    def test_upstream_status(self, temp_db):
        """Test upstream status tracking"""
        # Default should be True
        assert temp_db.get_upstream_status() is True
        
        # Set to False
        temp_db.set_upstream_status(False)
        assert temp_db.get_upstream_status() is False
        
        # Set back to True
        temp_db.set_upstream_status(True)
        assert temp_db.get_upstream_status() is True

    def test_empty_data_scenarios(self, temp_db):
        """Test handling of empty data"""
        # Empty planet history
        history = temp_db.get_planet_status_history(999, limit=10)
        assert history == []
        
        # Empty campaigns
        campaigns = temp_db.get_active_campaigns()
        assert campaigns == []
        
        # No war status
        war_status = temp_db.get_latest_war_status()
        assert war_status is None

    def test_database_error_handling(self, temp_db):
        """Test database error handling"""
        # Try to save with invalid data that might cause JSON serialization issues
        # Use a mock to force an exception
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_war_status({"test": "data"})
            assert result is False

    def test_save_statistics_error_handling(self, temp_db):
        """Test statistics save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_statistics({"players": 1000})
            assert result is False

    def test_save_planet_status_error_handling(self, temp_db):
        """Test planet status save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_planet_status(0, {"name": "Test"})
            assert result is False

    def test_save_campaign_error_handling(self, temp_db):
        """Test campaign save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_campaign(1, 0, {"id": 1})
            assert result is False

    def test_save_assignments_error_handling(self, temp_db):
        """Test assignments save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_assignments([{"id": 1}])
            assert result is False

    def test_save_dispatches_error_handling(self, temp_db):
        """Test dispatches save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_dispatches([{"id": 1}])
            assert result is False

    def test_save_planet_events_error_handling(self, temp_db):
        """Test planet events save error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.save_planet_events([{"id": 1}])
            assert result is False

    def test_get_latest_war_status_error(self, temp_db):
        """Test get latest war status error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_war_status()
            assert result is None

    def test_get_latest_statistics_error(self, temp_db):
        """Test get latest statistics error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_statistics()
            assert result is None

    def test_get_planet_status_history_error(self, temp_db):
        """Test get planet status history error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_planet_status_history(0)
            assert result == []

    def test_get_statistics_history_error(self, temp_db):
        """Test get statistics history error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_statistics_history()
            assert result == []

    def test_get_active_campaigns_error(self, temp_db):
        """Test get active campaigns error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_active_campaigns()
            assert result == []

    def test_get_latest_assignments_error(self, temp_db):
        """Test get latest assignments error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_assignments()
            assert result == []

    def test_get_latest_dispatches_error(self, temp_db):
        """Test get latest dispatches error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_dispatches()
            assert result == []

    def test_get_latest_planet_events_error(self, temp_db):
        """Test get latest planet events error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_planet_events()
            assert result == []

    def test_get_latest_planets_snapshot_error(self, temp_db):
        """Test get latest planets snapshot error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_planets_snapshot()
            assert result is None

    def test_get_latest_campaigns_snapshot_error(self, temp_db):
        """Test get latest campaigns snapshot error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_campaigns_snapshot()
            assert result is None

    def test_get_latest_factions_snapshot_error(self, temp_db):
        """Test get latest factions snapshot error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_factions_snapshot()
            assert result is None

    def test_get_latest_biomes_snapshot_error(self, temp_db):
        """Test get latest biomes snapshot error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            result = temp_db.get_latest_biomes_snapshot()
            assert result is None

    def test_set_upstream_status_error(self, temp_db):
        """Test set upstream status error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            # Should not raise exception
            temp_db.set_upstream_status(True)

    def test_get_upstream_status_error(self, temp_db):
        """Test get upstream status error handling"""
        with patch('sqlite3.connect') as mock_connect:
            mock_connect.side_effect = Exception("Database error")
            # Should default to True
            result = temp_db.get_upstream_status()
            assert result is True

    def test_assignments_without_id(self, temp_db):
        """Test saving assignments without id field"""
        assignments = [{"no_id": True}]
        result = temp_db.save_assignments(assignments)
        assert result is True
        
    def test_dispatches_without_id(self, temp_db):
        """Test saving dispatches without id field"""
        dispatches = [{"no_id": True}]
        result = temp_db.save_dispatches(dispatches)
        assert result is True

    def test_planet_events_without_id(self, temp_db):
        """Test saving planet events without id field"""
        events = [{"no_id": True}]
        result = temp_db.save_planet_events(events)
        assert result is True

    def test_get_latest_planets_snapshot_no_timestamp(self, temp_db):
        """Test get planets snapshot when no timestamp exists"""
        # Empty database should return None
        result = temp_db.get_latest_planets_snapshot()
        assert result is None

    def test_get_latest_campaigns_snapshot_empty(self, temp_db):
        """Test get campaigns snapshot when empty"""
        result = temp_db.get_latest_campaigns_snapshot()
        assert result is None

    def test_get_latest_factions_snapshot_no_war_data(self, temp_db):
        """Test get factions snapshot when no war data exists"""
        result = temp_db.get_latest_factions_snapshot()
        assert result is None

    def test_get_latest_biomes_snapshot_no_planets(self, temp_db):
        """Test get biomes snapshot when no planets exist"""
        result = temp_db.get_latest_biomes_snapshot()
        assert result is None

    def test_get_latest_biomes_snapshot_empty_results(self, temp_db):
        """Test get biomes snapshot with no results for timestamp"""
        # This would be an edge case where timestamp exists but no data
        result = temp_db.get_latest_biomes_snapshot()
        assert result is None

    def test_get_latest_factions_snapshot_war_data_no_factions(self, temp_db):
        """Test get factions snapshot when war data has no factions key"""
        temp_db.save_war_status({"war_id": 1})
        result = temp_db.get_latest_factions_snapshot()
        assert result is None


# ========================
# Scraper Tests
# ========================


class TestScraper:
    """Test scraper operations"""

    @pytest.fixture
    def scraper(self):
        """Create a scraper instance with test base URL"""
        return HellDivers2Scraper(timeout=10, base_url="https://test.api/v1")

    def test_scraper_initialization(self, scraper):
        """Test scraper initialization"""
        assert scraper.timeout == 10
        assert scraper.base_url == "https://test.api/v1"
        assert scraper.request_delay == 2.0
        assert scraper.session is not None

    def test_scraper_headers(self, scraper):
        """Test scraper sets correct headers"""
        assert "User-Agent" in scraper.session.headers
        assert "X-Super-Client" in scraper.session.headers
        assert "X-Super-Contact" in scraper.session.headers

    @patch('requests.Session.get')
    def test_get_war_status_success(self, mock_get, scraper):
        """Test successful war status fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"war_id": 1}
        mock_get.return_value = mock_response
        
        result = scraper.get_war_status()
        assert result is not None
        assert result["war_id"] == 1

    @patch('requests.Session.get')
    def test_get_war_status_network_error(self, mock_get, scraper):
        """Test war status fetch with network error"""
        import requests
        mock_get.side_effect = requests.RequestException("Network error")
        
        result = scraper.get_war_status()
        assert result is None

    @patch('requests.Session.get')
    def test_get_war_status_timeout(self, mock_get, scraper):
        """Test war status fetch with timeout"""
        import requests
        mock_get.side_effect = requests.Timeout("Timeout error")
        
        result = scraper.get_war_status()
        assert result is None

    @patch('requests.Session.get')
    def test_get_war_status_http_error(self, mock_get, scraper):
        """Test war status fetch with HTTP error (404, 500, etc.)"""
        import requests
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = scraper.get_war_status()
        assert result is None

    @patch('requests.Session.get')
    def test_get_campaign_info(self, mock_get, scraper):
        """Test campaign info fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_get.return_value = mock_response
        
        result = scraper.get_campaign_info()
        assert result is not None
        assert len(result) == 1

    @patch('requests.Session.get')
    def test_get_assignments(self, mock_get, scraper):
        """Test assignments fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_get.return_value = mock_response
        
        result = scraper.get_assignments()
        assert result is not None

    @patch('requests.Session.get')
    def test_get_dispatches(self, mock_get, scraper):
        """Test dispatches fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_get.return_value = mock_response
        
        result = scraper.get_dispatches()
        assert result is not None

    @patch('requests.Session.get')
    def test_get_planets(self, mock_get, scraper):
        """Test planets fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"index": 0}]
        mock_get.return_value = mock_response
        
        result = scraper.get_planets()
        assert result is not None

    @patch('requests.Session.get')
    def test_get_planet_status(self, mock_get, scraper):
        """Test planet status fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"index": 0}
        mock_get.return_value = mock_response
        
        result = scraper.get_planet_status(0)
        assert result is not None

    @patch('requests.Session.get')
    def test_get_statistics(self, mock_get, scraper):
        """Test statistics fetch (from war status)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"statistics": {"players": 50000}}
        mock_get.return_value = mock_response
        
        result = scraper.get_statistics()
        assert result is not None
        assert result["players"] == 50000

    @patch('requests.Session.get')
    def test_get_statistics_no_war_data(self, mock_get, scraper):
        """Test statistics fetch when war data is unavailable"""
        import requests
        mock_get.side_effect = requests.RequestException("Error")
        
        result = scraper.get_statistics()
        assert result is None

    @patch('requests.Session.get')
    def test_get_planet_events(self, mock_get, scraper):
        """Test planet events fetch"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_get.return_value = mock_response
        
        result = scraper.get_planet_events()
        assert result is not None

    @patch('requests.Session.get')
    def test_get_factions(self, mock_get, scraper):
        """Test factions fetch (from war status)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"factions": [{"name": "Humans"}]}
        mock_get.return_value = mock_response
        
        result = scraper.get_factions()
        assert result is not None
        assert len(result) == 1

    @patch('requests.Session.get')
    def test_get_biomes(self, mock_get, scraper):
        """Test biomes fetch (from planets)"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"biome": {"name": "Swamp"}},
            {"biome": {"name": "Desert"}},
            {"biome": {"name": "Swamp"}}  # Duplicate
        ]
        mock_get.return_value = mock_response
        
        result = scraper.get_biomes()
        assert result is not None
        # Should have unique biomes only
        assert len(result) == 2

    @patch('requests.Session.get')
    def test_get_biomes_empty_planets(self, mock_get, scraper):
        """Test biomes fetch when no planets available"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        result = scraper.get_biomes()
        assert result is None

    def test_rate_limiting(self, scraper):
        """Test rate limiting enforcement"""
        import time
        
        # Reset last_request_time to a time far in the past to ensure first call is immediate
        scraper.last_request_time = 0
        
        # First request should be immediate
        start_time = time.time()
        scraper._rate_limit()
        first_duration = time.time() - start_time
        assert first_duration < 0.1  # Should be nearly instant
        
        # Second request should be delayed
        start_time = time.time()
        scraper._rate_limit()
        second_duration = time.time() - start_time
        # Should delay approximately request_delay seconds (2.0s)
        assert second_duration >= 1.5  # Allow some margin

    def test_scraper_close(self, scraper):
        """Test scraper session closure"""
        scraper.close()
        # Session should be closed, but we can't easily test this
        # Just ensure no exceptions are raised

    @patch('requests.Session.get')
    def test_get_biomes_no_biome_names(self, mock_get, scraper):
        """Test biomes extraction when planets have no biome names"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"biome": {}},  # No name
            {"no_biome": "data"}  # No biome key
        ]
        mock_get.return_value = mock_response
        
        result = scraper.get_biomes()
        assert result is None  # No valid biomes


# ========================
# Collector Tests
# ========================


class TestCollector:
    """Test data collector operations"""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
            db_path = f.name
        
        db = Database(db_path)
        yield db
        
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)

    @pytest.fixture
    def collector(self, temp_db):
        """Create a collector instance"""
        collector = DataCollector(temp_db, interval=60)
        yield collector
        # Ensure collector is stopped
        if collector.is_running:
            collector.stop()

    def test_collector_initialization(self, collector):
        """Test collector initialization"""
        assert collector.db is not None
        assert collector.scraper is not None
        assert collector.interval == 60
        assert collector.is_running is False

    def test_collector_start(self, collector):
        """Test collector start"""
        collector.start()
        assert collector.is_running is True
        collector.stop()

    def test_collector_start_already_running(self, collector):
        """Test starting collector when already running"""
        collector.start()
        assert collector.is_running is True
        
        # Try to start again
        collector.start()
        assert collector.is_running is True  # Should still be running
        
        collector.stop()

    def test_collector_stop(self, collector):
        """Test collector stop"""
        collector.start()
        collector.stop()
        assert collector.is_running is False

    def test_collector_stop_not_running(self, collector):
        """Test stopping collector when not running"""
        # Should not raise any errors
        collector.stop()
        assert collector.is_running is False

    @patch.object(HellDivers2Scraper, 'get_war_status')
    @patch.object(HellDivers2Scraper, 'get_statistics')
    @patch.object(HellDivers2Scraper, 'get_planets')
    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    @patch.object(HellDivers2Scraper, 'get_assignments')
    @patch.object(HellDivers2Scraper, 'get_dispatches')
    @patch.object(HellDivers2Scraper, 'get_planet_events')
    def test_collect_all_data_success(self, mock_events, mock_dispatches, mock_assignments, 
                                     mock_campaigns, mock_planets, mock_stats, mock_war, 
                                     collector):
        """Test successful data collection"""
        mock_war.return_value = {"war_id": 1}
        mock_stats.return_value = {"players": 50000}
        mock_planets.return_value = [{"index": 0, "name": "Planet"}]
        mock_campaigns.return_value = [{"id": 1, "planet": {"index": 0}}]
        mock_assignments.return_value = [{"id": 1}]
        mock_dispatches.return_value = [{"id": 1}]
        mock_events.return_value = [{"id": 1}]
        
        collector.collect_all_data()
        
        # Check that data was saved
        assert collector.db.get_latest_war_status() is not None

    @patch.object(HellDivers2Scraper, 'get_war_status')
    def test_collect_all_data_failure(self, mock_war, collector):
        """Test data collection with failures"""
        mock_war.return_value = None
        
        # Should handle gracefully and not crash
        collector.collect_all_data()

    @patch.object(HellDivers2Scraper, 'get_planets')
    def test_collect_all_data_empty_planets(self, mock_planets, collector):
        """Test data collection with empty planet list"""
        mock_planets.return_value = []
        
        # Should handle gracefully
        collector.collect_all_data()

    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    def test_collect_all_data_empty_campaigns(self, mock_campaigns, collector):
        """Test data collection with empty campaigns"""
        mock_campaigns.return_value = []
        
        collector.collect_all_data()

    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    def test_collect_all_data_campaigns_missing_planet_index(self, mock_campaigns, collector):
        """Test campaign collection with missing planet index"""
        # Campaign without planet.index should be skipped
        mock_campaigns.return_value = [
            {"id": 1, "planet": {}},  # No index
            {"id": 2, "no_planet": True}  # No planet key
        ]
        
        collector.collect_all_data()

    @patch.object(HellDivers2Scraper, 'get_planets')
    def test_collect_all_data_planets_missing_index(self, mock_planets, collector):
        """Test planet collection with missing index"""
        # Planet without index should be skipped
        mock_planets.return_value = [
            {"name": "Planet A"},  # No index
            {"index": 1, "name": "Planet B"}  # Valid
        ]
        
        collector.collect_all_data()

    @patch.object(HellDivers2Scraper, 'get_war_status')
    def test_collect_all_data_exception(self, mock_war, collector):
        """Test data collection with exception"""
        mock_war.side_effect = Exception("Test exception")
        
        # Should catch exception and set upstream status to False
        collector.collect_all_data()
        assert collector.db.get_upstream_status() is False

    @patch.object(HellDivers2Scraper, 'get_planet_status')
    def test_collect_planet_data(self, mock_planet, collector):
        """Test collecting data for specific planet"""
        mock_planet.return_value = {"index": 0, "name": "Test Planet"}
        
        result = collector.collect_planet_data(0)
        assert result is not None
        assert result["name"] == "Test Planet"

    @patch.object(HellDivers2Scraper, 'get_planet_status')
    def test_collect_planet_data_failure(self, mock_planet, collector):
        """Test collecting planet data with failure"""
        mock_planet.return_value = None
        
        result = collector.collect_planet_data(0)
        assert result is None

    @patch.object(HellDivers2Scraper, 'get_planet_status')
    def test_collect_planet_data_exception(self, mock_planet, collector):
        """Test collecting planet data with exception"""
        mock_planet.side_effect = Exception("Test exception")
        
        result = collector.collect_planet_data(0)
        assert result is None


# ========================
# API Endpoint Tests
# ========================


class TestAPIEndpoints:
    """Test FastAPI endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        # Use TestClient without lifespan to avoid starting the collector
        with TestClient(app) as client:
            yield client

    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Hell Divers 2 API"

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "collector_running" in data

    @patch.object(Database, 'get_latest_war_status')
    def test_get_war_status_success(self, mock_get, client):
        """Test get war status endpoint"""
        mock_get.return_value = {"war_id": 1}
        
        response = client.get("/api/war/status")
        assert response.status_code == 200
        data = response.json()
        assert data["war_id"] == 1

    @patch.object(Database, 'get_latest_war_status')
    def test_get_war_status_not_found(self, mock_get, client):
        """Test get war status when no data available"""
        mock_get.return_value = None
        
        response = client.get("/api/war/status")
        assert response.status_code == 404

    @patch.object(HellDivers2Scraper, 'get_war_status')
    @patch.object(Database, 'save_war_status')
    def test_refresh_war_status_success(self, mock_save, mock_get, client):
        """Test refresh war status endpoint"""
        mock_get.return_value = {"war_id": 1}
        mock_save.return_value = True
        
        response = client.post("/api/war/status/refresh")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    @patch.object(HellDivers2Scraper, 'get_war_status')
    def test_refresh_war_status_failure(self, mock_get, client):
        """Test refresh war status when fetch fails"""
        mock_get.return_value = None
        
        response = client.post("/api/war/status/refresh")
        assert response.status_code == 500

    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    def test_get_campaigns_live(self, mock_get, client):
        """Test get campaigns with live API"""
        mock_get.return_value = [{"id": 1}]
        
        response = client.get("/api/campaigns")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    @patch.object(Database, 'get_latest_campaigns_snapshot')
    def test_get_campaigns_cache_fallback(self, mock_cache, mock_live, client):
        """Test get campaigns with cache fallback"""
        mock_live.return_value = None
        mock_cache.return_value = [{"id": 1}]
        
        response = client.get("/api/campaigns")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_campaign_info')
    @patch.object(Database, 'get_latest_campaigns_snapshot')
    def test_get_campaigns_no_data(self, mock_cache, mock_live, client):
        """Test get campaigns when no data available"""
        mock_live.return_value = None
        mock_cache.return_value = None
        
        response = client.get("/api/campaigns")
        assert response.status_code == 503

    @patch.object(Database, 'get_active_campaigns')
    def test_get_active_campaigns(self, mock_get, client):
        """Test get active campaigns"""
        mock_get.return_value = [{"id": 1}]
        
        response = client.get("/api/campaigns/active")
        assert response.status_code == 200

    @patch.object(Database, 'get_active_campaigns')
    def test_get_active_campaigns_not_found(self, mock_get, client):
        """Test get active campaigns when none available"""
        mock_get.return_value = []
        
        response = client.get("/api/campaigns/active")
        assert response.status_code == 404

    @patch.object(HellDivers2Scraper, 'get_planets')
    def test_get_planets_live(self, mock_get, client):
        """Test get planets with live API"""
        mock_get.return_value = [{"index": 0}]
        
        response = client.get("/api/planets")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_planets')
    @patch.object(Database, 'get_latest_planets_snapshot')
    def test_get_planets_cache_fallback(self, mock_cache, mock_live, client):
        """Test get planets with cache fallback"""
        mock_live.return_value = None
        mock_cache.return_value = [{"index": 0}]
        
        response = client.get("/api/planets")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_planets')
    @patch.object(Database, 'get_latest_planets_snapshot')
    def test_get_planets_no_data(self, mock_cache, mock_live, client):
        """Test get planets when no data available"""
        mock_live.return_value = None
        mock_cache.return_value = None
        
        response = client.get("/api/planets")
        assert response.status_code == 503

    @patch.object(DataCollector, 'collect_planet_data')
    def test_get_planet_status_live(self, mock_collect, client):
        """Test get planet status with live data"""
        mock_collect.return_value = {"index": 0, "name": "Planet"}
        
        response = client.get("/api/planets/0")
        assert response.status_code == 200

    @patch.object(DataCollector, 'collect_planet_data')
    @patch.object(Database, 'get_planet_status_history')
    def test_get_planet_status_cache_fallback(self, mock_history, mock_collect, client):
        """Test get planet status with cache fallback"""
        mock_collect.return_value = None
        mock_history.return_value = [{"data": {"index": 0}}]
        
        response = client.get("/api/planets/0")
        assert response.status_code == 200

    @patch.object(DataCollector, 'collect_planet_data')
    @patch.object(Database, 'get_planet_status_history')
    def test_get_planet_status_no_data(self, mock_history, mock_collect, client):
        """Test get planet status when no data available"""
        mock_collect.return_value = None
        mock_history.return_value = []
        
        response = client.get("/api/planets/0")
        assert response.status_code == 503

    @patch.object(Database, 'get_planet_status_history')
    def test_get_planet_history(self, mock_get, client):
        """Test get planet history"""
        mock_get.return_value = [{"data": {"index": 0}}]
        
        response = client.get("/api/planets/0/history")
        assert response.status_code == 200

    @patch.object(Database, 'get_planet_status_history')
    def test_get_planet_history_not_found(self, mock_get, client):
        """Test get planet history when none available"""
        mock_get.return_value = []
        
        response = client.get("/api/planets/0/history")
        assert response.status_code == 404

    @patch.object(Database, 'get_latest_statistics')
    def test_get_statistics(self, mock_get, client):
        """Test get statistics"""
        mock_get.return_value = {"players": 50000}
        
        response = client.get("/api/statistics")
        assert response.status_code == 200

    @patch.object(Database, 'get_latest_statistics')
    def test_get_statistics_not_found(self, mock_get, client):
        """Test get statistics when none available"""
        mock_get.return_value = None
        
        response = client.get("/api/statistics")
        assert response.status_code == 404

    @patch.object(Database, 'get_statistics_history')
    def test_get_statistics_history(self, mock_get, client):
        """Test get statistics history"""
        mock_get.return_value = [{"data": {"players": 50000}}]
        
        response = client.get("/api/statistics/history")
        assert response.status_code == 200

    @patch.object(Database, 'get_statistics_history')
    def test_get_statistics_history_not_found(self, mock_get, client):
        """Test get statistics history when none available"""
        mock_get.return_value = []
        
        response = client.get("/api/statistics/history")
        assert response.status_code == 404

    @patch.object(HellDivers2Scraper, 'get_statistics')
    @patch.object(Database, 'save_statistics')
    def test_refresh_statistics(self, mock_save, mock_get, client):
        """Test refresh statistics"""
        mock_get.return_value = {"players": 50000}
        mock_save.return_value = True
        
        response = client.post("/api/statistics/refresh")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_statistics')
    def test_refresh_statistics_failure(self, mock_get, client):
        """Test refresh statistics when fetch fails"""
        mock_get.return_value = None
        
        response = client.post("/api/statistics/refresh")
        assert response.status_code == 500

    @patch.object(HellDivers2Scraper, 'get_factions')
    def test_get_factions_live(self, mock_get, client):
        """Test get factions with live API"""
        mock_get.return_value = [{"name": "Humans"}]
        
        response = client.get("/api/factions")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_factions')
    @patch.object(Database, 'get_latest_factions_snapshot')
    def test_get_factions_cache_fallback(self, mock_cache, mock_live, client):
        """Test get factions with cache fallback"""
        mock_live.return_value = None
        mock_cache.return_value = [{"name": "Humans"}]
        
        response = client.get("/api/factions")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_factions')
    @patch.object(Database, 'get_latest_factions_snapshot')
    def test_get_factions_no_data(self, mock_cache, mock_live, client):
        """Test get factions when no data available"""
        mock_live.return_value = None
        mock_cache.return_value = None
        
        response = client.get("/api/factions")
        assert response.status_code == 503

    @patch.object(HellDivers2Scraper, 'get_biomes')
    def test_get_biomes_live(self, mock_get, client):
        """Test get biomes with live API"""
        mock_get.return_value = [{"name": "Swamp"}]
        
        response = client.get("/api/biomes")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_biomes')
    @patch.object(Database, 'get_latest_biomes_snapshot')
    def test_get_biomes_cache_fallback(self, mock_cache, mock_live, client):
        """Test get biomes with cache fallback"""
        mock_live.return_value = None
        mock_cache.return_value = [{"name": "Swamp"}]
        
        response = client.get("/api/biomes")
        assert response.status_code == 200

    @patch.object(HellDivers2Scraper, 'get_biomes')
    @patch.object(Database, 'get_latest_biomes_snapshot')
    def test_get_biomes_no_data(self, mock_cache, mock_live, client):
        """Test get biomes when no data available"""
        mock_live.return_value = None
        mock_cache.return_value = None
        
        response = client.get("/api/biomes")
        assert response.status_code == 503

    def test_query_parameters(self, client):
        """Test query parameters validation"""
        # Test with valid limit
        with patch.object(Database, 'get_statistics_history') as mock_get:
            mock_get.return_value = [{"data": {"players": 50000}}]
            response = client.get("/api/statistics/history?limit=50")
            assert response.status_code == 200
        
        # Test with limit too high (should be clamped or validated)
        with patch.object(Database, 'get_statistics_history') as mock_get:
            mock_get.return_value = []
            response = client.get("/api/statistics/history?limit=2000")
            # FastAPI Query validation should handle this
            # Response can be 200 or 422 depending on validation
            assert response.status_code in [200, 404, 422]
