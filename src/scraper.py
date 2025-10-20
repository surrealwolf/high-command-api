import requests
import logging
import time
from typing import Dict, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class HellDivers2Scraper:
    """Scraper for Hell Divers 2 game data via community API (api.helldivers2.dev)
    
    Rate limiting: 5 requests per 10 seconds (2.0 seconds between requests enforced)
    """

    def __init__(self, timeout: int = 30, base_url: Optional[str] = None):
        self.timeout = timeout
        # Use provided URL or config URL
        self.base_url = base_url or Config.HELLDIVERS_API_BASE
        
        # Rate limiting: delay between requests (2 seconds for 5 requests in 10 seconds)
        self.request_delay = 2.0
        self.last_request_time = 0

        # Get headers from config, use "NA" if not configured
        client_name = (
            Config.HELLDIVERS_API_CLIENT_NAME
            if Config.HELLDIVERS_API_CLIENT_NAME != "NA"
            else "HighCommand"
        )
        contact = (
            Config.HELLDIVERS_API_CONTACT
            if Config.HELLDIVERS_API_CONTACT != "NA"
            else "admin@example.com"
        )

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "High-Command API/1.0",
                "X-Super-Client": client_name,
                "X-Super-Contact": contact,
            }
        )
        logger.info(f"HellDivers2Scraper initialized with base_url: {self.base_url}")
    
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.request_delay:
            delay = self.request_delay - elapsed
            logger.debug(f"Rate limiting: sleeping for {delay:.2f}s")
            time.sleep(delay)
        self.last_request_time = time.time()

    def get_war_status(self) -> Optional[Dict]:
        """Fetch current war status"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/war", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch war status: {e}")
            return None

    def get_campaign_info(self) -> Optional[List[Dict]]:
        """Fetch active campaigns information"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/campaigns", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch campaign info: {e}")
            return None

    def get_assignments(self) -> Optional[List[Dict]]:
        """Fetch current assignments (Major Orders)"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/assignments", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch assignments: {e}")
            return None

    def get_dispatches(self) -> Optional[List[Dict]]:
        """Fetch news dispatches and announcements"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/dispatches", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch dispatches: {e}")
            return None

    def get_planets(self) -> Optional[List[Dict]]:
        """Fetch all planets information"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/planets", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planets: {e}")
            return None

    def get_planet_status(self, planet_index: int) -> Optional[Dict]:
        """Fetch status of a specific planet"""
        try:
            self._rate_limit()
            response = self.session.get(
                f"{self.base_url}/planets/{planet_index}", timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planet status for {planet_index}: {e}")
            return None

    def get_statistics(self) -> Optional[Dict]:
        """Fetch global game statistics (part of war status)"""
        try:
            # Statistics are included in war status, return the statistics subset
            war_data = self.get_war_status()
            if war_data and "statistics" in war_data:
                return war_data["statistics"]
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to fetch statistics: {e}")
            return None

    def get_planet_events(self) -> Optional[List[Dict]]:
        """Fetch planet events"""
        try:
            self._rate_limit()
            response = self.session.get(f"{self.base_url}/planet-events", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planet events: {e}")
            return None

    def get_factions(self) -> Optional[List[Dict]]:
        """Fetch all factions (from war data)"""
        try:
            war_data = self.get_war_status()
            if war_data and "factions" in war_data:
                return war_data["factions"]
            return None
        except requests.RequestException as e:
            logger.error(f"Failed to fetch factions: {e}")
            return None

    def get_biomes(self) -> Optional[List[Dict]]:
        """Fetch all biomes from planets data"""
        try:
            planets = self.get_planets()
            if not planets:
                return None
            # Extract unique biomes from planets
            biomes = {}
            for planet in planets:
                if "biome" in planet:
                    biome_name = planet["biome"].get("name")
                    if biome_name and biome_name not in biomes:
                        biomes[biome_name] = planet["biome"]
            return list(biomes.values()) if biomes else None
        except requests.RequestException as e:
            logger.error(f"Failed to fetch biomes: {e}")
            return None

    def close(self):
        """Close the session"""
        self.session.close()
