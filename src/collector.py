import logging
from apscheduler.schedulers.background import BackgroundScheduler
from src.scraper import HellDivers2Scraper
from src.database import Database

logger = logging.getLogger(__name__)


class DataCollector:
    """Manages background data collection from Hell Divers 2 API"""

    def __init__(self, db: Database, interval: int = 300):
        self.db = db
        self.scraper = HellDivers2Scraper()
        self.scheduler = BackgroundScheduler()
        self.interval = interval
        self.is_running = False

    def start(self):
        """Start the data collection scheduler"""
        if self.is_running:
            logger.warning("Data collector is already running")
            return

        self.scheduler.add_job(
            self.collect_all_data, "interval", seconds=self.interval, id="collect_data"
        )
        self.scheduler.start()
        self.is_running = True
        logger.info(f"Data collector started with {self.interval}s interval")

    def stop(self):
        """Stop the data collection scheduler"""
        if not self.is_running:
            return

        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Data collector stopped")

    def collect_all_data(self):
        """Collect all available data"""
        logger.info("Starting data collection cycle")

        try:
            # Collect war status (this includes statistics)
            war_data = self.scraper.get_war_status()
            if war_data:
                self.db.save_war_status(war_data)
                logger.info("War status collected")
                
                # Extract and save statistics from war_data (no extra API call needed)
                stats_data = war_data.get("statistics")
                if stats_data:
                    self.db.save_statistics(stats_data)
                    logger.info("Statistics collected")
            else:
                logger.info("Failed to collect war status and statistics")

            # Collect planets
            planets = self.scraper.get_planets()
            if planets:
                for planet in planets:
                    planet_index = planet.get("index")
                    if planet_index:
                        self.db.save_planet_status(planet_index, planet)
                logger.info(f"Collected data for {len(planets)} planets")

            # Collect campaigns
            campaigns = self.scraper.get_campaign_info()
            if campaigns:
                for campaign in campaigns:
                    campaign_id = campaign.get("id")
                    if campaign_id and campaign.get("planet") and "index" in campaign["planet"]:
                        planet_index = campaign["planet"].get("index")
                        self.db.save_campaign(campaign_id, planet_index, campaign)
                logger.info(f"Collected {len(campaigns)} campaigns")

            # Collect assignments (Major Orders)
            assignments = self.scraper.get_assignments()
            if assignments:
                self.db.save_assignments(assignments)
                logger.info(f"Collected {len(assignments)} assignments")

            # Collect dispatches (news)
            dispatches = self.scraper.get_dispatches()
            if dispatches:
                self.db.save_dispatches(dispatches)
                logger.info(f"Collected {len(dispatches)} dispatches")

            # Collect planet events
            events = self.scraper.get_planet_events()
            if events is not None:
                self.db.save_planet_events(events)
                logger.info(f"Collected {len(events)} planet events")

            logger.info("Data collection cycle completed successfully")

        except Exception as e:
            logger.error(f"Error during data collection: {e}")

    def collect_planet_data(self, planet_index: int):
        """Collect data for a specific planet"""
        try:
            planet_data = self.scraper.get_planet_status(planet_index)
            if planet_data:
                self.db.save_planet_status(planet_index, planet_data)
                logger.info(f"Planet {planet_index} data collected")
                return planet_data
        except Exception as e:
            logger.error(f"Error collecting planet data: {e}")

        return None
