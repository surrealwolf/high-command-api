import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from src.database import Database
from src.scraper import HellDivers2Scraper
from src.collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database and scraper
db = Database()
scraper = HellDivers2Scraper()
collector = DataCollector(db, interval=300)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Hell Divers 2 API")
    if not collector.is_running:
        collector.start()
    yield
    # Shutdown
    logger.info("Shutting down Hell Divers 2 API")
    collector.stop()
    scraper.close()


# Initialize FastAPI app
app = FastAPI(
    title="Hell Divers 2 API",
    description="Real-time scraper for Hell Divers 2 game data",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# War Status Endpoints
# ========================


@app.get("/api/war/status", tags=["War"])
async def get_war_status():
    """Get current war status"""
    data = db.get_latest_war_status()
    if data:
        return data
    raise HTTPException(status_code=404, detail="No war status data available")


@app.post("/api/war/status/refresh", tags=["War"])
async def refresh_war_status():
    """Manually refresh war status"""
    data = scraper.get_war_status()
    if data:
        db.save_war_status(data)
        return {"success": True, "data": data}
    raise HTTPException(status_code=500, detail="Failed to fetch war status")


# ========================
# Campaign Endpoints
# ========================


@app.get("/api/campaigns", tags=["Campaigns"])
async def get_campaigns():
    """Get campaign information (with cache fallback)"""
    # Try live API first
    data = scraper.get_campaign_info()
    
    # Fallback to cache if live API fails
    if data is None:
        data = db.get_latest_campaigns_snapshot()
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail="No campaign data available (live fetch failed and no cached data)")


@app.get("/api/campaigns/active", tags=["Campaigns"])
async def get_active_campaigns():
    """Get active campaigns"""
    data = db.get_active_campaigns()
    if data:
        return data
    raise HTTPException(status_code=404, detail="No active campaigns")


# ========================
# Assignments Endpoints (Major Orders)
# ========================


@app.get("/api/assignments", tags=["Assignments"])
async def get_assignments(limit: int = Query(10, ge=1, le=100)):
    """Get current and recent assignments (Major Orders)"""
    data = db.get_latest_assignments(limit)
    if data:
        return data
    raise HTTPException(status_code=404, detail="No assignments available")


@app.post("/api/assignments/refresh", tags=["Assignments"])
async def refresh_assignments():
    """Manually refresh assignments"""
    data = scraper.get_assignments()
    if data:
        db.save_assignments(data)
        return {"success": True, "data": data}
    raise HTTPException(status_code=500, detail="Failed to fetch assignments")


# ========================
# Dispatches Endpoints (News/Announcements)
# ========================


@app.get("/api/dispatches", tags=["Dispatches"])
async def get_dispatches(limit: int = Query(10, ge=1, le=100)):
    """Get current and recent dispatches (news and announcements)"""
    data = db.get_latest_dispatches(limit)
    if data:
        return data
    raise HTTPException(status_code=404, detail="No dispatches available")


@app.post("/api/dispatches/refresh", tags=["Dispatches"])
async def refresh_dispatches():
    """Manually refresh dispatches"""
    data = scraper.get_dispatches()
    if data:
        db.save_dispatches(data)
        return {"success": True, "data": data}
    raise HTTPException(status_code=500, detail="Failed to fetch dispatches")


# ========================
# Planet Events Endpoints
# ========================


@app.get("/api/planet-events", tags=["Planets"])
async def get_planet_events(limit: int = Query(10, ge=1, le=100)):
    """Get current and recent planet events"""
    data = db.get_latest_planet_events(limit)
    if data:
        return data
    raise HTTPException(status_code=404, detail="No planet events available")


@app.post("/api/planet-events/refresh", tags=["Planets"])
async def refresh_planet_events():
    """Manually refresh planet events"""
    data = scraper.get_planet_events()
    if data:
        db.save_planet_events(data)
        return {"success": True, "data": data}
    raise HTTPException(status_code=500, detail="Failed to fetch planet events")


# ========================
# Planet Endpoints
# ========================


@app.get("/api/planets", tags=["Planets"])
async def get_planets():
    """Get all planets (with cache fallback)"""
    # Try live API first
    data = scraper.get_planets()
    
    # Fallback to cache if live API fails
    if data is None:
        data = db.get_latest_planets_snapshot()
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail="Failed to fetch planets and no cached data available")


@app.get("/api/planets/{planet_index}", tags=["Planets"])
async def get_planet_status(planet_index: int):
    """Get status of a specific planet (with cache fallback)"""
    # Try live API first
    data = collector.collect_planet_data(planet_index)
    
    # Fallback to cache if live API fails
    if data is None:
        history = db.get_planet_status_history(planet_index, limit=1)
        if history and isinstance(history[0], dict) and "data" in history[0]:
            data = history[0]["data"]
        elif history:
            data = history[0]
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail=f"Failed to fetch planet {planet_index} and no cached data available")


@app.get("/api/planets/{planet_index}/history", tags=["Planets"])
async def get_planet_history(planet_index: int, limit: int = Query(10, ge=1, le=100)):
    """Get status history for a planet"""
    data = db.get_planet_status_history(planet_index, limit)
    if data:
        return data
    raise HTTPException(status_code=404, detail=f"No history for planet {planet_index}")


# ========================
# Statistics Endpoints
# ========================


@app.get("/api/statistics", tags=["Statistics"])
async def get_statistics():
    """Get latest global statistics"""
    data = db.get_latest_statistics()
    if data:
        return data
    raise HTTPException(status_code=404, detail="No statistics available")


@app.get("/api/statistics/history", tags=["Statistics"])
async def get_statistics_history(limit: int = Query(100, ge=1, le=1000)):
    """Get statistics history"""
    data = db.get_statistics_history(limit)
    if data:
        return data
    raise HTTPException(status_code=404, detail="No statistics history available")


@app.post("/api/statistics/refresh", tags=["Statistics"])
async def refresh_statistics():
    """Manually refresh statistics"""
    data = scraper.get_statistics()
    if data:
        db.save_statistics(data)
        return {"success": True, "data": data}
    raise HTTPException(status_code=500, detail="Failed to fetch statistics")


# ========================
# Faction Endpoints
# ========================


@app.get("/api/factions", tags=["Factions"])
async def get_factions():
    """Get all factions (with cache fallback)"""
    # Try live API first
    data = scraper.get_factions()
    
    # Fallback to cache if live API fails
    if data is None:
        data = db.get_latest_factions_snapshot()
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail="Failed to fetch factions and no cached data available")


# ========================
# Biome Endpoints
# ========================


@app.get("/api/biomes", tags=["Biomes"])
async def get_biomes():
    """Get all biomes (with cache fallback)"""
    # Try live API first
    data = scraper.get_biomes()
    
    # Fallback to cache if live API fails
    if data is None:
        data = db.get_latest_biomes_snapshot()
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail="Failed to fetch biomes and no cached data available")


# ========================
# Health Check
# ========================


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    # Returns local service status and upstream API status
    # No external API calls made here to avoid blocking event loop or consuming rate limits
    upstream_status = db.get_upstream_status()
    return {
        "status": "healthy",
        "collector_running": collector.is_running,
        "upstream_api": "online" if upstream_status else "offline"
    }


# ========================
# Root Endpoint
# ========================


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Hell Divers 2 API",
        "version": "1.0.0",
        "description": "Real-time scraper for Hell Divers 2 game data",
        "docs": "/docs",
        "redoc": "/redoc",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
