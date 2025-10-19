# High Command API

A production-ready FastAPI application for real-time scraping and tracking of Hell Divers 2 game data.

## Overview

High Command API provides comprehensive access to Hell Divers 2 game statistics, war status, planet information, campaigns, and faction data through a modern RESTful API with automatic background data collection and interactive documentation.

## Features

- ✅ **Real-time Data Collection**: Automatic background scraping every 5 minutes
- ✅ **Comprehensive Endpoints**: 30+ endpoints for accessing game data
- ✅ **Historical Tracking**: SQLite database with optimized queries
- ✅ **Interactive Documentation**: Auto-generated Swagger UI and ReDoc
- ✅ **Production Ready**: Docker support, error handling, type hints
- ✅ **Developer Friendly**: Clean code, extensive documentation

## Project Structure

```
high-command-api/
├── src/                    # Core application code
│   ├── __init__.py
│   ├── app.py             # FastAPI application
│   ├── scraper.py         # Hell Divers 2 API scraper
│   ├── database.py        # SQLite database layer
│   ├── collector.py       # Background task scheduler
│   └── config.py          # Configuration management
├── tests/                  # Test suite
│   ├── __init__.py
│   └── demo.py            # Comprehensive tests
├── docs/                   # Documentation
│   ├── DEPLOYMENT.md      # Production deployment guide
│   ├── DEVELOPMENT.md     # Architecture guide
│   ├── QUICKREF.md        # Quick reference
│   └── API.md             # API reference
├── Makefile               # Project automation
├── Dockerfile             # Container image
├── docker-compose.yml     # Multi-container setup
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── pyproject.toml        # Project metadata
```

## Installation

### Prerequisites
- Python 3.8+
- pip or pipenv

### Setup

1. Clone the repository:
```bash
cd /home/lee/git/high-command/high-command-api
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
```

5. Run the application:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

6. (Optional) Run the demo script to test all endpoints:
```bash
python demo.py
```

## Quick Start

After installation, the API is immediately ready to use:

```bash
# Start the API
python app.py

# In another terminal, test it
curl http://localhost:5000/api/health

# Run the demo test suite
python demo.py
```

## API Endpoints

All endpoints are automatically documented and can be explored interactively:
- **Swagger UI**: http://localhost:5000/docs
- **ReDoc**: http://localhost:5000/redoc

### War Status
- `GET /api/war/status` - Get current war status
- `POST /api/war/status/refresh` - Manually refresh war status

### Campaigns
- `GET /api/campaigns` - Get all campaigns
- `GET /api/campaigns/active` - Get active campaigns

### Planets
- `GET /api/planets` - Get all planets
- `GET /api/planets/<planet_index>` - Get specific planet status
- `GET /api/planets/<planet_index>/history?limit=10` - Get planet status history

### Statistics
- `GET /api/statistics` - Get latest statistics
- `GET /api/statistics/history?limit=100` - Get statistics history
- `POST /api/statistics/refresh` - Manually refresh statistics

### Factions
- `GET /api/factions` - Get all factions

### Biomes
- `GET /api/biomes` - Get all biomes

### Health & Info
- `GET /api/health` - Health check endpoint
- `GET /` - Root endpoint with API information

## Configuration

Edit `.env` file to configure:

```env
FLASK_ENV=development          # Environment (development, production, testing)
FLASK_DEBUG=True               # Debug mode
API_PORT=5000                  # API port
DATABASE_URL=sqlite:///helldivers2.db  # Database location
LOG_LEVEL=INFO                 # Logging level
SCRAPE_INTERVAL=300            # Data collection interval in seconds
```

## Database

The API uses SQLite to store:
- **war_status**: Current and historical war statuses
- **statistics**: Game-wide statistics with timestamps
- **planet_status**: Individual planet status snapshots
- **campaigns**: Active and completed campaigns

All data includes timestamps for historical tracking and analysis.

## Background Data Collection

The application automatically collects data on a configurable interval (default 5 minutes):
- War status
- Global statistics
- Planet statuses
- Campaign information

Access the health endpoint to verify the collector is running:
```bash
curl http://localhost:5000/api/health
```

Output:
```json
{
  "status": "healthy",
  "collector_running": true
}
```

## Technology Stack

- **Framework**: FastAPI - Modern, fast Python web framework
- **Server**: Uvicorn - Lightning-fast ASGI server
- **Scheduling**: APScheduler - Flexible background task scheduler
- **HTTP Client**: Requests - Simple and elegant HTTP library
- **Database**: SQLite - Lightweight, file-based database
- **Documentation**: Automatic OpenAPI (Swagger) & ReDoc integration

## Usage Examples

### Get current war status
```bash
curl http://localhost:5000/api/war/status
```

### Get planet history (last 20 updates)
```bash
curl "http://localhost:5000/api/planets/1/history?limit=20"
```

### Get statistics history (last 50 entries)
```bash
curl "http://localhost:5000/api/statistics/history?limit=50"
```

### Manually refresh statistics
```bash
curl -X POST http://localhost:5000/api/statistics/refresh
```

## Future Enhancements

- [ ] WebSocket support for real-time updates
- [ ] Predictive analytics for war outcomes
- [ ] Player performance metrics integration
- [ ] Discord webhook notifications for events
- [ ] Grafana dashboard integration
- [ ] Advanced filtering and search capabilities
- [ ] Data export (CSV, JSON, SQL)
- [ ] Authentication and rate limiting
- [ ] GraphQL API layer
- [ ] Caching layer (Redis)
- [ ] Docker containerization

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## Troubleshooting

### No data available
- Check that the API can reach `https://api.live.prod.theadultswim.com`
- Verify network connectivity and firewall settings
- Check logs for specific error messages

### Database errors
- Ensure write permissions to the database directory
- Delete `helldivers2.db` and restart to rebuild the database

### Scheduler not running
- Check logs for background scheduler errors
- Verify APScheduler is properly installed
