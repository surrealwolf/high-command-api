import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    DEBUG = False
    TESTING = False

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///helldivers2.db")

    # API Settings
    API_TIMEOUT = 30
    SCRAPE_INTERVAL = 300  # 5 minutes

    # Hell Divers 2 API Endpoints
    HELLDIVERS_API_BASE = os.getenv("HELLDIVERS_API_BASE", "NA")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SCRAPE_INTERVAL = 60  # 1 minute for testing


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SCRAPE_INTERVAL = 300  # 5 minutes


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    SCRAPE_INTERVAL = 60


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
