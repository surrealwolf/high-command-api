# Architecture & Development

## Project Structure

```
high-command-api/
├── src/                    # Core application code
│   ├── __init__.py        # Package initialization
│   ├── app.py             # FastAPI application
│   ├── scraper.py         # Hell Divers 2 API scraper
│   ├── database.py        # SQLite database layer
│   ├── collector.py       # Background task scheduler
│   └── config.py          # Configuration management
├── tests/                  # Test suite
│   ├── __init__.py
│   └── demo.py            # Comprehensive integration tests
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md    # This file
│   ├── DEPLOYMENT.md      # Production deployment guide
│   ├── API.md             # API reference
│   └── QUICKREF.md        # Quick reference guide
├── main.py                # Application entry point
├── Makefile               # Project automation (40+ targets)
├── Dockerfile             # Production container image
├── docker-compose.yml     # Multi-container setup
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
├── .env.example           # Environment template
├── .gitignore             # Git patterns
└── README.md              # Project overview
```

## Core Modules

### `src/app.py` - FastAPI Application
- **Purpose**: Main FastAPI application with all endpoint handlers
- **Key Components**:
  - `lifespan()`: Async context manager for startup/shutdown
  - 30+ endpoint handlers organized by resource type
  - CORS middleware for cross-origin requests
  - Error handling with HTTPExceptions
  
- **Endpoints**: War status, planets, statistics, campaigns, factions, biomes
- **Documentation**: Auto-generated at `/docs` (Swagger) and `/redoc` (ReDoc)

### `src/scraper.py` - Hell Divers 2 API Client
- **Purpose**: Fetch external game data from Hell Divers 2 API
- **Class**: `HellDivers2Scraper`
- **Methods**:
  - `get_war_status()`: Current war status
  - `get_planets()`: All planets information
  - `get_statistics()`: Global game statistics
  - `get_campaigns()`: Active campaigns
  - `get_factions()`: Faction information
  - `get_biomes()`: Biome data
  
- **Error Handling**: Graceful error handling with logging

### `src/database.py` - SQLite Storage
- **Purpose**: Persistent data storage with optimized queries
- **Class**: `Database`
- **Tables**:
  - `war_status`: War data with timestamps
  - `statistics`: Player stats and metrics
  - `planet_status`: Individual planet data
  - `campaigns`: Campaign information
  
- **Indexes**: Optimized for timestamp and planet_index queries
- **Methods**: Save/retrieve data, history queries

### `src/collector.py` - Background Scheduler
- **Purpose**: Automatic periodic data collection
- **Class**: `DataCollector`
- **Features**:
  - APScheduler integration for background tasks
  - Configurable collection interval (default: 5 minutes)
  - Comprehensive error handling
  - Collects all data types automatically
  
- **Methods**: `start()`, `stop()`, `collect_all_data()`, `collect_planet_data()`

### `src/config.py` - Configuration Management
- **Purpose**: Environment-based settings and configuration
- **Classes**:
  - `Config`: Base configuration
  - `DevelopmentConfig`: Development overrides
  - `ProductionConfig`: Production settings
  - `TestingConfig`: Testing environment
  
- **Settings**: Database URL, API timeouts, collection intervals, log levels

## Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│                    Client Requests                            │
└─────────────────────────┬──────────────────────────────────────┘
                          │
                          ▼
                    ┌─────────────┐
                    │  FastAPI    │
                    │  (app.py)   │
                    └─────────────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
        Database     Scraper        Collector
       (database)   (scraper)     (collector)
           │              │              │
           ▼              ▼              ▼
        SQLite      External API   Background
        Storage    (Hell Divers 2)   Tasks
```

## API Lifecycle

### Startup
1. FastAPI app initializes
2. Lifespan context manager's startup code runs
3. DataCollector starts (schedules background tasks)
4. Application ready to receive requests

### Background Collection (every 5 minutes)
1. Collector runs `collect_all_data()`
2. Scraper fetches data from Hell Divers 2 API
3. Database stores the retrieved data
4. Logging records the operation

### Request Handling
1. Client sends HTTP request
2. FastAPI routes to appropriate handler
3. Handler queries database or scraper
4. Response returned to client

### Shutdown
1. Shutdown signal received
2. DataCollector stops scheduler
3. Scraper session closed
4. Application exits gracefully

## Database Schema

### war_status
```sql
CREATE TABLE war_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    data TEXT NOT NULL
);
```

### statistics
```sql
CREATE TABLE statistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_players INTEGER,
    total_kills INTEGER,
    missions_won INTEGER,
    data TEXT NOT NULL
);
```

### planet_status
```sql
CREATE TABLE planet_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    planet_index INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    planet_name TEXT,
    owner TEXT,
    status TEXT,
    data TEXT NOT NULL
);
```

### campaigns
```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER UNIQUE,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    planet_index INTEGER,
    status TEXT,
    data TEXT NOT NULL
);
```

## Design Patterns

### Async/Await
All FastAPI handlers use `async def` for non-blocking I/O

### Context Manager
Lifespan pattern manages application lifecycle

### Scheduler Pattern
APScheduler for background task management

### Repository Pattern
Database class abstracts data access

### Configuration Pattern
Environment-based configuration classes

## Development Workflow

### Setting Up Development Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Running Locally
```bash
python main.py
```

### Testing
```bash
python -m tests.demo
```

### Running with Live Reload
```bash
python main.py --reload
```

## Code Quality

### Type Hints
All functions include type hints for better IDE support and documentation

### Error Handling
Comprehensive error handling with logging throughout the codebase

### Documentation
- Docstrings for all classes and methods
- Inline comments for complex logic
- Comprehensive README and deployment guides

## Performance Considerations

1. **Database Indexing**: Timestamps and planet_index are indexed for fast queries
2. **Async Operations**: Non-blocking I/O for better concurrency
3. **Session Management**: Reused HTTP session for connection pooling
4. **Background Collection**: Off-loads heavy operations from request handlers
5. **JSON Serialization**: Efficient storage and retrieval of complex data

## Security Considerations

1. **CORS Middleware**: Configurable cross-origin requests
2. **Input Validation**: FastAPI's built-in validation
3. **Error Messages**: Generic error messages in production
4. **Logging**: Secure logging of operations and errors
5. **Environment Variables**: Sensitive config via .env files
