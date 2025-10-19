import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from database import Database
from scraper import HellDivers2Scraper
from collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
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
    lifespan=lifespan
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
    """Get campaign information"""
    data = scraper.get_campaign_info()
    if data:
        return data
    raise HTTPException(status_code=404, detail="Failed to fetch campaigns")

@app.get("/api/campaigns/active", tags=["Campaigns"])
async def get_active_campaigns():
    """Get active campaigns"""
    data = db.get_active_campaigns()
    if data:
        return data
    raise HTTPException(status_code=404, detail="No active campaigns")

# ========================
# Planet Endpoints
# ========================

@app.get("/api/planets", tags=["Planets"])
async def get_planets():
    """Get all planets"""
    data = scraper.get_planets()
    if data:
        return data
    raise HTTPException(status_code=404, detail="Failed to fetch planets")

@app.get("/api/planets/{planet_index}", tags=["Planets"])
async def get_planet_status(planet_index: int):
    """Get status of a specific planet"""
    data = collector.collect_planet_data(planet_index)
    if data:
        return data
    raise HTTPException(status_code=404, detail=f"Failed to fetch planet {planet_index}")

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
    """Get all factions"""
    data = scraper.get_factions()
    if data:
        return data
    raise HTTPException(status_code=404, detail="Failed to fetch factions")

# ========================
# Biome Endpoints
# ========================

@app.get("/api/biomes", tags=["Biomes"])
async def get_biomes():
    """Get all biomes"""
    data = scraper.get_biomes()
    if data:
        return data
    raise HTTPException(status_code=404, detail="Failed to fetch biomes")

# ========================
# Health Check
# ========================

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "collector_running": collector.is_running
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
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
