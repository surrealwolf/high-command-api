import requests
import logging
from typing import Dict, List, Optional
from src.config import Config

logger = logging.getLogger(__name__)


class HellDivers2Scraper:
    """Scraper for Hell Divers 2 game data"""

    DEFAULT_BASE_URL = "https://api.live.prod.theadultswim.com/helldivers2"

    def __init__(self, timeout: int = 30, base_url: Optional[str] = None):
        self.timeout = timeout
        # Use provided URL, config URL, or fallback to default
        config_url = Config.HELLDIVERS_API_BASE
        if config_url == "NA":
            self.base_url = base_url or self.DEFAULT_BASE_URL
        else:
            self.base_url = base_url or config_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "High-Command API/1.0"})

    def get_war_status(self) -> Optional[Dict]:
        """Fetch current war status"""
        try:
            response = self.session.get(f"{self.base_url}/status", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch war status: {e}")
            return None

    def get_campaign_info(self) -> Optional[Dict]:
        """Fetch campaign information"""
        try:
            response = self.session.get(f"{self.base_url}/campaigns", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch campaign info: {e}")
            return None

    def get_planets(self) -> Optional[List[Dict]]:
        """Fetch all planets information"""
        try:
            response = self.session.get(f"{self.base_url}/planets", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planets: {e}")
            return None

    def get_planet_status(self, planet_index: int) -> Optional[Dict]:
        """Fetch status of a specific planet"""
        try:
            response = self.session.get(
                f"{self.base_url}/planets/{planet_index}", timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planet status for {planet_index}: {e}")
            return None

    def get_statistics(self) -> Optional[Dict]:
        """Fetch global game statistics"""
        try:
            response = self.session.get(f"{self.base_url}/statistics", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch statistics: {e}")
            return None

    def get_factions(self) -> Optional[List[Dict]]:
        """Fetch all factions"""
        try:
            response = self.session.get(f"{self.base_url}/factions", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch factions: {e}")
            return None

    def get_biomes(self) -> Optional[List[Dict]]:
        """Fetch all biomes"""
        try:
            response = self.session.get(f"{self.base_url}/biomes", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch biomes: {e}")
            return None

    def close(self):
        """Close the session"""
        self.session.close()
