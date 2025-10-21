# Hell Divers 2 API - Development Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   FastAPI Application                   │
│                    (app.py)                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Endpoints  │  │   Middleware │  │   Handlers   │ │
│  │   /api/*     │  │   CORS, etc  │  │   Async     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                          ▲                              │
│                          │                              │
│         ┌────────────────┼────────────────┐            │
│         ▼                ▼                ▼            │
│   ┌──────────┐  ┌──────────────┐  ┌────────────┐      │
│   │ Scraper  │  │  Database    │  │ Collector  │      │
│   │(requests)│  │  (SQLite)    │  │(APScheduler)     │
│   └──────────┘  └──────────────┘  └────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
         │                                      │
         ▼                                      ▼
  Hell Divers 2 API              helldivers2.db (File)
```

## Module Structure

### `app.py` - Main Application
- **Purpose**: FastAPI application factory and route handlers
- **Key Components**:
  - `lifespan()`: Startup/shutdown lifecycle management
  - Route handlers for all endpoints
  - CORS middleware configuration
  - Error handling

### `scraper.py` - API Scraper
- **Purpose**: HTTP client for Hell Divers 2 API
- **Key Methods**:
  - `get_war_status()`: Fetch war information
  - `get_planets()`: Get all planets
  - `get_statistics()`: Get global stats
  - `get_campaigns()`: Get campaign info
  - `get_factions()`: Get faction info
  - `get_biomes()`: Get biome info

### `database.py` - Data Persistence
- **Purpose**: SQLite database operations
- **Tables**:
  - `war_status`: War information
  - `statistics`: Global game stats
  - `planet_status`: Individual planet data
  - `campaigns`: Campaign information
  - `assignments`: Major orders
  - `dispatches`: News and announcements
  - `planet_events`: Special planet events
  - `system_status`: Internal metadata (upstream API status)
- **Key Methods**:
  - `save_*()`: Insert data
  - `get_*()`: Retrieve data
  - `*_history()`: Get historical data
  - `get_latest_*_snapshot()`: Get cached data for fallback
  - `set_upstream_status()`: Track upstream API availability
  - `get_upstream_status()`: Check last known upstream status

### `collector.py` - Background Tasks
- **Purpose**: Schedule and manage data collection
- **Key Components**:
  - APScheduler background scheduler
  - Periodic data collection (default: 5 minutes)
  - Event-driven collection

### `config.py` - Configuration
- **Purpose**: Environment-based configuration
- **Classes**:
  - `Config`: Base configuration
  - `DevelopmentConfig`: Dev settings
  - `ProductionConfig`: Prod settings
  - `TestingConfig`: Test settings

## API Design

### Response Format

All responses follow a consistent JSON format:

**Success Response**:
```json
{
  "field": "value",
  "nested": {
    "data": "here"
  }
}
```

**Error Response**:
```json
{
  "detail": "Error message describing what went wrong"
}
```

### Cache Fallback Behavior

Certain endpoints implement cache fallback for resilience:
- **Endpoints with cache fallback**: `/api/campaigns`, `/api/planets`, `/api/planets/{planet_index}`, `/api/factions`, `/api/biomes`
- **Fallback logic**:
  1. Try to fetch from live upstream API
  2. If upstream fails, retrieve from database cache
  3. If cache exists, return 200 with cached data
  4. If no cache exists, return 503 Service Unavailable

**Status Codes**:
- `200 OK`: Success (may be live or cached data)
- `404 Not Found`: Resource doesn't exist or no data collected
- `503 Service Unavailable`: Upstream API down AND no cached data available
- `500 Internal Server Error`: Unexpected server error

### Endpoint Patterns

```
GET    /api/resource           - List/Get all
GET    /api/resource/{id}      - Get single
POST   /api/resource/action    - Custom action
```

## Adding New Endpoints

### 1. Add Scraper Method

In `scraper.py`:
```python
def get_new_data(self) -> Optional[Dict]:
    """Fetch new data from Hell Divers 2 API"""
    try:
        response = self.session.get(
            f"{self.BASE_URL}/new-endpoint",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to fetch new data: {e}")
        return None
```

### 2. Add Database Methods

In `database.py`:
```python
def save_new_data(self, data: Dict) -> bool:
    """Save new data to database"""
    try:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO new_data_table (data) VALUES (?)',
                (json.dumps(data),)
            )
            conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to save new data: {e}")
        return False
```

### 3. Add API Endpoint

In `app.py`:
```python
@app.get("/api/new-data", tags=["New Data"])
async def get_new_data():
    """Get new data"""
    data = db.get_latest_new_data()
    if data:
        return data
    raise HTTPException(status_code=404, detail="No data available")
```

### 4. (Optional) Add Cache Fallback

For critical endpoints that should continue serving during upstream outages:
```python
@app.get("/api/new-data", tags=["New Data"])
async def get_new_data():
    """Get new data (with cache fallback)"""
    # Try live API first
    data = scraper.get_new_data()
    
    # Fallback to cache if live API fails
    if data is None:
        data = db.get_latest_new_data_snapshot()
    
    if data is not None:
        return data
    raise HTTPException(status_code=503, detail="No new data available (live fetch failed and no cached data)")
```

### System Status Tracking

The `system_status` table tracks internal metadata:
- **Purpose**: Monitor upstream API health and other system metrics
- **Usage**: Collector updates upstream status after each collection cycle
- **Schema**:
  ```sql
  CREATE TABLE system_status (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      status_key TEXT UNIQUE,
      status_value BOOLEAN,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
  )
  ```
- **Current Keys**:
  - `upstream_api_available`: Boolean indicating if Hell Divers 2 API is reachable

## Testing

### Manual Testing

1. **Start the API**:
```bash
python app.py
```

2. **Run demo tests**:
```bash
python demo.py
```

3. **Manual curl tests**:
```bash
# Get war status
curl http://localhost:5000/api/war/status

# Refresh statistics
curl -X POST http://localhost:5000/api/statistics/refresh

# Get planets with limit
curl "http://localhost:5000/api/planets/1/history?limit=20"
```

### Interactive Testing

1. **Swagger UI**: http://localhost:5000/docs
2. **ReDoc**: http://localhost:5000/redoc
3. **Python client**:
```python
import requests

API = "http://localhost:5000/api"
response = requests.get(f"{API}/planets")
print(response.json())
```

## Debugging

### Enable Debug Logging

Update `app.py`:
```python
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitor Database

```bash
# Connect to database
sqlite3 helldivers2.db

# View tables
.tables

# View schema
.schema war_status

# Query data
SELECT * FROM war_status LIMIT 1;

# Count rows
SELECT COUNT(*) FROM war_status;
```

### Monitor Scheduler

The scheduler logs all job execution. Check logs for:
```
Added job "DataCollector.collect_all_data"
Scheduler started
Job executed successfully
```

## Performance Optimization

### Database Indexes

Already implemented for:
- `war_status.timestamp`
- `statistics.timestamp`
- `planet_status.planet_index`

Add new indexes:
```python
cursor.execute('CREATE INDEX idx_column ON table(column)')
```

### Query Optimization

Use `LIMIT` for large result sets:
```python
SELECT * FROM planet_status LIMIT 100;
```

### Caching

Implement response caching:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation():
    ...
```

## Common Issues & Solutions

### Issue: "API not responding"
**Solution**: Check if the API is running and listening on port 5000
```bash
lsof -i :5000
```

### Issue: "Database locked"
**Solution**: Close all database connections and restart the app

### Issue: "Scheduler not collecting data"
**Solution**: Check logs and verify network connectivity

### Issue: "Missing dependencies"
**Solution**: Reinstall requirements
```bash
pip install -r requirements.txt --force-reinstall
```

### Issue: "503 errors on cache-fallback endpoints"
**Solution**: 
- Check if upstream API is accessible: `curl https://api.helldivers2.dev/api/v1/war/info`
- Verify database has cached data: `sqlite3 helldivers2.db "SELECT COUNT(*) FROM planet_status"`
- Wait for collector to run and populate cache (runs every 5 minutes)

## Database Migration Notes

### Adding system_status Table (Cache Fallback Feature)

If upgrading from a version before the cache-fallback feature, the `system_status` table will be automatically created on next startup. No manual migration is required.

**What changed**:
- New table: `system_status` with columns `id`, `status_key`, `status_value`, `timestamp`
- New index: `idx_system_status_key` on `status_key` column
- New methods: `set_upstream_status()`, `get_upstream_status()` in `database.py`
- New snapshot methods: `get_latest_planets_snapshot()`, `get_latest_campaigns_snapshot()`, etc.

**To verify migration**:
```bash
sqlite3 helldivers2.db "SELECT name FROM sqlite_master WHERE type='table' AND name='system_status'"
```

Expected output: `system_status`

## Code Style

- Use type hints for all functions
- Document functions with docstrings
- Follow PEP 8 style guide
- Use meaningful variable names
- Handle errors gracefully

## Contributing

1. Create a feature branch
2. Make changes following the patterns in existing code
3. Test thoroughly with `demo.py`
4. Update documentation
5. Submit a pull request

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Requests Documentation](https://requests.readthedocs.io/)
