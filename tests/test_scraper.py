#!/usr/bin/env python3
"""
Unit tests for scraper module.
Tests HTTP client, rate limiting, error handling, and data fetching.
"""

import pytest
import time
from unittest.mock import patch, MagicMock, Mock
import requests
from src.scraper import HellDivers2Scraper


class TestScraperInit:
    """Test scraper initialization"""

    def test_init_with_defaults(self):
        """Test scraper initialization with defaults"""
        scraper = HellDivers2Scraper()
        assert scraper.timeout == 30
        assert scraper.request_delay == 2.0
        assert scraper.base_url is not None

    def test_init_with_custom_timeout(self):
        """Test scraper initialization with custom timeout"""
        scraper = HellDivers2Scraper(timeout=60)
        assert scraper.timeout == 60

    def test_init_with_custom_base_url(self):
        """Test scraper initialization with custom base URL"""
        scraper = HellDivers2Scraper(base_url="https://custom.api.com")
        assert scraper.base_url == "https://custom.api.com"

    def test_init_session_headers(self):
        """Test session headers are set correctly"""
        scraper = HellDivers2Scraper()
        assert "User-Agent" in scraper.session.headers
        assert "X-Super-Client" in scraper.session.headers
        assert "X-Super-Contact" in scraper.session.headers


class TestRateLimiting:
    """Test rate limiting functionality"""

    def test_rate_limit_delay(self):
        """Test rate limiting enforces delay"""
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time()
        
        start = time.time()
        scraper._rate_limit()
        elapsed = time.time() - start
        
        # Should have delayed approximately request_delay seconds
        assert elapsed >= scraper.request_delay - 0.1

    def test_rate_limit_no_delay_first_request(self):
        """Test no delay on first request after initialization"""
        scraper = HellDivers2Scraper()
        # Set last_request_time to far past
        scraper.last_request_time = time.time() - 10
        
        start = time.time()
        scraper._rate_limit()
        elapsed = time.time() - start
        
        # Should not delay significantly
        assert elapsed < 0.1


class TestFetchWithBackoff:
    """Test fetch with exponential backoff"""

    @patch("requests.Session.get")
    def test_fetch_success(self, mock_get):
        """Test successful fetch returns data"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test"}
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time() - 10  # Avoid rate limit delay
        result = scraper._fetch_with_backoff("https://example.com/api")
        
        assert result == {"data": "test"}
        mock_get.assert_called_once()

    @patch("requests.Session.get")
    def test_fetch_429_retry(self, mock_get):
        """Test 429 error triggers retry with backoff"""
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        mock_response_429.raise_for_status.side_effect = requests.HTTPError(response=mock_response_429)
        
        mock_response_success = MagicMock()
        mock_response_success.json.return_value = {"data": "test"}
        mock_response_success.status_code = 200
        
        mock_get.side_effect = [
            requests.HTTPError(response=mock_response_429),
            mock_response_success
        ]
        
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time() - 10
        result = scraper._fetch_with_backoff("https://example.com/api", max_retries=2)
        
        assert result == {"data": "test"}
        assert mock_get.call_count == 2

    @patch("requests.Session.get")
    def test_fetch_max_retries_exceeded(self, mock_get):
        """Test fetch returns None after max retries"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_get.side_effect = requests.HTTPError(response=mock_response)
        
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time() - 10
        result = scraper._fetch_with_backoff("https://example.com/api", max_retries=2)
        
        assert result is None

    @patch("requests.Session.get")
    def test_fetch_timeout(self, mock_get):
        """Test fetch returns None on timeout"""
        mock_get.side_effect = requests.Timeout()
        
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time() - 10
        result = scraper._fetch_with_backoff("https://example.com/api")
        
        assert result is None

    @patch("requests.Session.get")
    def test_fetch_connection_error(self, mock_get):
        """Test fetch returns None on connection error"""
        mock_get.side_effect = requests.ConnectionError()
        
        scraper = HellDivers2Scraper()
        scraper.last_request_time = time.time() - 10
        result = scraper._fetch_with_backoff("https://example.com/api")
        
        assert result is None


class TestScraperMethods:
    """Test scraper data fetching methods"""

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_war_status(self, mock_fetch):
        """Test get_war_status method"""
        mock_fetch.return_value = {"war_id": 1, "status": "active"}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_war_status()
        
        assert result == {"war_id": 1, "status": "active"}
        mock_fetch.assert_called_once()

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_war_status_failure(self, mock_fetch):
        """Test get_war_status returns None on failure"""
        mock_fetch.return_value = None
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_war_status()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_planets(self, mock_fetch):
        """Test get_planets method"""
        mock_fetch.return_value = [{"index": 0, "name": "Super Earth"}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_planets()
        
        assert result == [{"index": 0, "name": "Super Earth"}]

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_get_statistics(self, mock_war_status):
        """Test get_statistics method"""
        mock_war_status.return_value = {"statistics": {"missions": 1000, "deaths": 5000}}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_statistics()
        
        assert result == {"missions": 1000, "deaths": 5000}

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_get_factions(self, mock_war_status):
        """Test get_factions method"""
        mock_war_status.return_value = {"factions": [{"id": 1, "name": "Terminids"}]}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_factions()
        
        assert result == [{"id": 1, "name": "Terminids"}]

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_get_biomes(self, mock_planets):
        """Test get_biomes method"""
        mock_planets.return_value = [
            {"biome": {"name": "Desert", "type": "arid"}},
            {"biome": {"name": "Ice", "type": "frozen"}}
        ]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_biomes()
        
        assert len(result) == 2
        assert {"name": "Desert", "type": "arid"} in result

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_campaign_info(self, mock_fetch):
        """Test get_campaign_info method"""
        mock_fetch.return_value = [{"id": 1, "planet": {"index": 5}}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_campaign_info()
        
        assert result == [{"id": 1, "planet": {"index": 5}}]

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_assignments(self, mock_fetch):
        """Test get_assignments method"""
        mock_fetch.return_value = [{"id": 1, "title": "Major Order"}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_assignments()
        
        assert result == [{"id": 1, "title": "Major Order"}]

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_dispatches(self, mock_fetch):
        """Test get_dispatches method"""
        mock_fetch.return_value = [{"id": 1, "message": "News"}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_dispatches()
        
        assert result == [{"id": 1, "message": "News"}]

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_planet_events(self, mock_fetch):
        """Test get_planet_events method"""
        mock_fetch.return_value = [{"planet_index": 5, "event": "storm"}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_planet_events()
        
        assert result == [{"planet_index": 5, "event": "storm"}]

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_planet_status(self, mock_fetch):
        """Test get_planet_status method"""
        mock_fetch.return_value = {"index": 5, "liberation": 50.0}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_planet_status(5)
        
        assert result == {"index": 5, "liberation": 50.0}


class TestScraperCleanup:
    """Test scraper cleanup"""

    def test_close_session(self):
        """Test close method closes session"""
        with patch("requests.Session.close") as mock_close:
            scraper = HellDivers2Scraper()
            scraper.close()
            mock_close.assert_called_once()


class TestScraperEdgeCases:
    """Test scraper edge cases"""

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_war_status_wrong_type(self, mock_fetch):
        """Test get_war_status with wrong return type"""
        mock_fetch.return_value = ["not", "a", "dict"]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_war_status()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_planets_wrong_type(self, mock_fetch):
        """Test get_planets with wrong return type"""
        mock_fetch.return_value = {"not": "a list"}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_planets()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "_fetch_with_backoff")
    def test_get_campaign_info_wrong_type(self, mock_fetch):
        """Test get_campaign_info with wrong return type"""
        mock_fetch.return_value = "not a list"
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_campaign_info()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_get_statistics_no_stats(self, mock_war):
        """Test get_statistics when war status has no statistics"""
        mock_war.return_value = {"war_id": 1}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_statistics()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "get_war_status")
    def test_get_factions_no_factions(self, mock_war):
        """Test get_factions when war status has no factions"""
        mock_war.return_value = {"war_id": 1}
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_factions()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_get_biomes_no_planets(self, mock_planets):
        """Test get_biomes when no planets returned"""
        mock_planets.return_value = None
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_biomes()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_get_biomes_empty_list(self, mock_planets):
        """Test get_biomes with empty planet list"""
        mock_planets.return_value = []
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_biomes()
        
        assert result is None

    @patch.object(HellDivers2Scraper, "get_planets")
    def test_get_biomes_no_biome_data(self, mock_planets):
        """Test get_biomes when planets have no biome data"""
        mock_planets.return_value = [{"index": 1, "name": "Planet"}]
        
        scraper = HellDivers2Scraper(base_url="https://api.example.com")
        result = scraper.get_biomes()
        
        assert result is None
