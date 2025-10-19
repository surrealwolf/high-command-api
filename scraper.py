import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class HellDivers2Scraper:
    """Scraper for Hell Divers 2 game data"""
    
    BASE_URL = "https://api.live.prod.theadultswim.com/helldivers2"
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'High-Command API/1.0'
        })
    
    def get_war_status(self) -> Optional[Dict]:
        """Fetch current war status"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/status",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch war status: {e}")
            return None
    
    def get_campaign_info(self) -> Optional[Dict]:
        """Fetch campaign information"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/campaigns",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch campaign info: {e}")
            return None
    
    def get_planets(self) -> Optional[List[Dict]]:
        """Fetch all planets information"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/planets",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planets: {e}")
            return None
    
    def get_planet_status(self, planet_index: int) -> Optional[Dict]:
        """Fetch status of a specific planet"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/planets/{planet_index}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch planet status for {planet_index}: {e}")
            return None
    
    def get_statistics(self) -> Optional[Dict]:
        """Fetch global game statistics"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/statistics",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch statistics: {e}")
            return None
    
    def get_factions(self) -> Optional[List[Dict]]:
        """Fetch all factions"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/factions",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch factions: {e}")
            return None
    
    def get_biomes(self) -> Optional[List[Dict]]:
        """Fetch all biomes"""
        try:
            response = self.session.get(
                f"{self.BASE_URL}/biomes",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch biomes: {e}")
            return None
    
    def close(self):
        """Close the session"""
        self.session.close()
