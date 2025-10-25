#!/usr/bin/env python3
"""
Unit tests for collector module.
Tests data collection scheduling, error handling, and lifecycle.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.collector import DataCollector
from src.database import Database
from src.scraper import HellDivers2Scraper


@pytest.fixture
def mock_db():
    """Create a mock database"""
    return MagicMock(spec=Database)


@pytest.fixture
def mock_scraper():
    """Create a mock scraper"""
    return MagicMock(spec=HellDivers2Scraper)


class TestCollectorInit:
    """Test collector initialization"""

    def test_init_default_interval(self, mock_db):
        """Test collector initialization with default interval"""
        collector = DataCollector(mock_db)
        assert collector.interval == 300
        assert collector.is_running is False
        assert collector.db == mock_db

    def test_init_custom_interval(self, mock_db):
        """Test collector initialization with custom interval"""
        collector = DataCollector(mock_db, interval=60)
        assert collector.interval == 60


class TestCollectorLifecycle:
    """Test collector start/stop"""

    def test_start_collector(self, mock_db):
        """Test starting collector"""
        collector = DataCollector(mock_db, interval=300)
        collector.start()
        
        assert collector.is_running is True
        collector.stop()

    def test_start_already_running(self, mock_db):
        """Test starting collector when already running"""
        collector = DataCollector(mock_db, interval=300)
        collector.start()
        
        # Try starting again - should not error
        collector.start()
        assert collector.is_running is True
        collector.stop()

    def test_stop_collector(self, mock_db):
        """Test stopping collector"""
        collector = DataCollector(mock_db, interval=300)
        collector.start()
        collector.stop()
        
        assert collector.is_running is False

    def test_stop_not_running(self, mock_db):
        """Test stopping collector when not running"""
        collector = DataCollector(mock_db, interval=300)
        # Should not error
        collector.stop()
        assert collector.is_running is False


class TestDataCollection:
    """Test data collection methods"""

    @patch.object(HellDivers2Scraper, "get_war_status")
    @patch.object(HellDivers2Scraper, "get_statistics")
    @patch.object(HellDivers2Scraper, "get_planets")
    def test_collect_all_data_success(self, mock_planets, mock_stats, mock_war, mock_db):
        """Test successful data collection"""
        mock_war.return_value = {"war_id": 1}
        mock_stats.return_value = {"total_players": 1000}
        mock_planets.return_value = [{"index": 1, "name": "Planet 1"}]
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Verify database save methods were called
        mock_db.save_war_status.assert_called_once()
        mock_db.save_statistics.assert_called_once()

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_collect_war_status_failure(self, mock_war, mock_db):
        """Test collection continues when war status fails"""
        mock_war.return_value = None
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Should not call save_war_status if data is None
        mock_db.save_war_status.assert_not_called()

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_collect_empty_planets(self, mock_planets, mock_db):
        """Test collection with empty planet list"""
        mock_planets.return_value = []
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Should handle empty list gracefully
        assert True

    @patch.object(HellDivers2Scraper, "get_campaign_info")
    def test_collect_campaigns(self, mock_campaigns, mock_db):
        """Test campaign collection"""
        mock_campaigns.return_value = [
            {"id": 1, "planet": {"index": 5}}
        ]
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Verify campaign was saved
        mock_db.save_campaign.assert_called()

    @patch.object(HellDivers2Scraper, "get_assignments")
    def test_collect_assignments(self, mock_assignments, mock_db):
        """Test assignments collection"""
        mock_assignments.return_value = [{"id": 1, "title": "Major Order"}]
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        mock_db.save_assignments.assert_called_once()

    @patch.object(HellDivers2Scraper, "get_dispatches")
    def test_collect_dispatches(self, mock_dispatches, mock_db):
        """Test dispatches collection"""
        mock_dispatches.return_value = [{"id": 1, "message": "News"}]
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        mock_db.save_dispatches.assert_called_once()

    @patch.object(HellDivers2Scraper, "get_planet_events")
    def test_collect_planet_events(self, mock_events, mock_db):
        """Test planet events collection"""
        mock_events.return_value = [{"id": 1, "planetIndex": 5}]
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        mock_db.save_planet_events.assert_called_once()


class TestErrorHandling:
    """Test error handling in data collection"""

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_collection_with_exception(self, mock_war, mock_db):
        """Test collection handles exceptions gracefully"""
        mock_war.side_effect = Exception("API Error")
        
        collector = DataCollector(mock_db, interval=300)
        # Should not raise exception
        collector.collect_all_data()
        assert True

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_collection_with_database_error(self, mock_planets, mock_db):
        """Test collection handles database errors"""
        mock_planets.return_value = [{"index": 1}]
        mock_db.save_planet_status.side_effect = Exception("DB Error")
        
        collector = DataCollector(mock_db, interval=300)
        # Should handle error and continue
        collector.collect_all_data()
        assert True


class TestUpstreamStatusTracking:
    """Test upstream API status tracking"""

    @patch.object(HellDivers2Scraper, "get_war_status")
    @patch.object(HellDivers2Scraper, "get_statistics")
    @patch.object(HellDivers2Scraper, "get_planets")
    @patch.object(HellDivers2Scraper, "get_campaign_info")
    @patch.object(HellDivers2Scraper, "get_assignments")
    @patch.object(HellDivers2Scraper, "get_dispatches")
    @patch.object(HellDivers2Scraper, "get_planet_events")
    def test_upstream_status_success(self, mock_events, mock_dispatches, mock_assign, 
                                     mock_camp, mock_planets, mock_stats, mock_war, mock_db):
        """Test upstream status is set to True on successful collection"""
        # Return valid data for all endpoints
        mock_war.return_value = {"war_id": 1}
        mock_stats.return_value = {"total_players": 1000}
        mock_planets.return_value = [{"index": 1}]
        mock_camp.return_value = []
        mock_assign.return_value = []
        mock_dispatches.return_value = []
        mock_events.return_value = []
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Verify upstream status was set to True
        mock_db.set_upstream_status.assert_called_with(True)

    @patch.object(HellDivers2Scraper, "get_war_status")
    @patch.object(HellDivers2Scraper, "get_statistics")
    @patch.object(HellDivers2Scraper, "get_planets")
    @patch.object(HellDivers2Scraper, "get_campaign_info")
    @patch.object(HellDivers2Scraper, "get_assignments")
    @patch.object(HellDivers2Scraper, "get_dispatches")
    @patch.object(HellDivers2Scraper, "get_planet_events")
    def test_upstream_status_failure(self, mock_events, mock_dispatches, mock_assign,
                                     mock_camp, mock_planets, mock_stats, mock_war, mock_db):
        """Test upstream status is set to False on exception"""
        # Cause an exception during collection
        mock_war.side_effect = Exception("API Error")
        
        collector = DataCollector(mock_db, interval=300)
        collector.collect_all_data()
        
        # Verify upstream status was set to False due to exception
        mock_db.set_upstream_status.assert_called_with(False)
