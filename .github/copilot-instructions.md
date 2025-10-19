# High Command API - AI Coding Agent Instructions

## Project Overview
**Hell Divers 2 API**: Production-ready FastAPI application for real-time scraping and tracking of Hell Divers 2 game data. The system continuously collects war status, planet information, campaigns, statistics, and faction data via background tasks and serves them through a comprehensive REST API.

## Environment & Build Setup

### Python Version
- **Target**: Python 3.14.0 (see `.python-version`)
- **Minimum**: Python 3.9
- **Development**: Use `pyenv` or `asdf` to match `.python-version`
- **Tools**: ruff (linting/formatting), mypy (type checking), pytest (testing with asyncio support)

### Makefile Workflow (Bash shell required)
- **`make venv`** - Create virtual environment
- **`make install`** - Install production dependencies via `pip install -e .`
- **`make dev`** - Install dev dependencies and run with auto-reload on port 5000
- **`make test`** - Run pytest with coverage (generates coverage.xml and HTML report)
- **`make test-fast`** - Run pytest without coverage
- **`make lint`** - Run ruff check and mypy on src/ and tests/
- **`make format`** - Format code with black and ruff --fix
- **`make check`** - Lint and test (pre-commit gate)
- **`make check-all`** - Format, lint, test (complete quality gate for PRs)

### Core Components
1. **app.py** (`src/app.py` - 205 lines): FastAPI application with 30+ endpoints organized by tags (War, Planets, Statistics, Campaigns, Factions, Biomes, System)
2. **scraper.py** (`src/scraper.py` - 115 lines): HTTP client wrapping Hell Divers 2 API (`https://api.live.prod.theadultswim.com/helldivers2`) with methods like `get_war_status()`, `get_planets()`, `get_statistics()`
3. **database.py** (`src/database.py` - 228 lines): SQLite manager with 4 main tables (war_status, statistics, planet_status, campaigns) + indexes for fast historical queries
4. **collector.py** (`src/collector.py` - 97 lines): APScheduler-based background task runner that calls `collect_all_data()` every 5 minutes (300s) during app lifecycle
5. **config.py** (`src/config.py` - 41 lines): Environment-based configuration with DevelopmentConfig (1-minute intervals) vs ProductionConfig (5-minute intervals)

### Lifecycle & Integration
- **Startup**: `lifespan()` context manager in app.py starts `collector.start()`, which launches APScheduler
- **Data Flow**: Collector → Scraper → (HTTP to Hell Divers 2 API) → Parser → Database → API endpoints
- **Error Handling**: Scraper returns `None` on failures with logged exceptions; endpoints raise `HTTPException(404/500)` when data unavailable
- **JSON Storage**: Complex nested objects stored as TEXT in database with `json.dumps()` for retrieval

## Key Patterns & Conventions

### Endpoint Patterns
- **Route Organization**: Grouped by resource tags (`@app.get("/api/{resource}/{action}", tags=["ResourceName"])`)
- **Response Format**: Raw JSON objects (no envelope); errors use FastAPI's `{"detail": "message"}` format
- **Refresh Pattern**: Most resources have `/api/{resource}/refresh` POST endpoints for manual data collection
- **Query Parameters**: Used with `Query()` for filtering (example: `@app.get("/api/planets", tags=["Planets"])`)

### Database Conventions
- **Auto-incrementing IDs**: `id INTEGER PRIMARY KEY AUTOINCREMENT` on all tables
- **Timestamps**: Every row gets `timestamp DATETIME DEFAULT CURRENT_TIMESTAMP`
- **Indexes**: Created on frequently queried columns (timestamp, planet_index)
- **JSON Storage**: Complex nested data stored in `data TEXT` column for flexibility
- **Retrieval**: Use `json.loads()` when returning from database to API

### Error Handling
- **Scraper Level**: Catch `requests.RequestException`, log error, return `None`
- **Database Level**: Use try/except with sqlite3.connect(), rollback on failure
- **API Level**: Raise `HTTPException(status_code, detail="message")` for client errors
- **Logging**: Use configured logger with module-specific `logger = logging.getLogger(__name__)`

### Dependencies & Tools Evolution
- **Linter Shift**: Replaced `flake8` with `ruff` (faster, more rules, auto-fix support)
- **Code Formatting**: Uses `black` (100 char line length) with `ruff format`
- **Type Checking**: `mypy` (Python 3.9+ compatible) with `ignore_missing_imports` enabled
- **Testing**: `pytest` with `pytest-asyncio` for async test support and `pytest-cov` for coverage
- **Test Output**: Generates `coverage.xml` (for CI upload) and HTML reports
- **Coverage Tracking**: Codecov integration via GitHub Actions (non-blocking failures)

## Specific Implementation Rules

### Adding New Endpoints
1. Create scraper method in `scraper.py` following pattern: try/except with `requests.RequestException`, return `None` on failure
2. Add database storage method in `database.py` using `INSERT INTO` or `UPDATE` with JSON serialization for complex data
3. Create API endpoint in `app.py` with proper tag, docstring, and error handling
4. Add to `collector.py`'s `collect_all_data()` if background collection needed (typical pattern)
5. Test with `demo.py` by adding test functions to the class

### Modifying Database Schema
- **Never break existing code**: Create new tables if schema change needed; old tables stay for backward compatibility
- **Always add indexes** on columns used in WHERE or ORDER BY clauses
- **Use JSON TEXT** for nested/variable data to avoid schema sprawl
- **Migration**: No migration system in place; manual database backup recommended before schema changes

### Adding New Collectors
- Add method to `scraper.py` following existing patterns (session timeout, User-Agent headers)
- Register in `collector.py`'s `collect_all_data()` with try/except and logging
- Ensure idempotent: safe to run every 5 minutes without side effects
- Include logging before and after: `logger.info(f"Collected data for X items")`

### Dependencies
- **Framework**: FastAPI 0.104.1, Uvicorn 0.24.0
- **Scheduler**: APScheduler 3.10.4 (no concurrent execution; uses background threads)
- **HTTP**: Requests 2.31.0 with session reuse and 30-second timeout
- **Database**: SQLite3 (built-in); no ORM used—raw SQL with sqlite3 module
- **Config**: python-dotenv 1.0.0 for environment variables

## Critical Workflows

### Local Development
```bash
# Setup virtual environment
python3 -m venv venv && source venv/bin/activate

# Install dependencies
make install

# Run API (auto-reloads with --reload)
make dev

# In another terminal, run tests
make test-fast     # Quick test without coverage
make test          # Full test with coverage report

# Or use Makefile shortcuts
make lint                # ruff + mypy checks
make format              # black + ruff formatting
make check-all           # Format + lint + test (complete gate)
```

### Production Deployment
```bash
# Using Docker (Python 3.14-slim base, non-root user)
docker build -t high-command-api:latest .
docker run -p 5000:5000 high-command-api:latest

# Using Makefile
make run                # Runs: python -m uvicorn src.app:app --host 0.0.0.0 --port 5000
```

### GitHub Actions CI/CD
- **tests.yml**: Runs on Python 3.13 & 3.14, Linux/macOS/Windows, includes security checks
- **docker.yml**: Builds Docker image with layer caching (type=gha)
- **auto-approve.yml**: Auto-approves PRs after successful Tests + Docker workflows (trusted authors only)

### Debugging Tips
- **Check collector status**: Call `/api/health` endpoint to verify `collector_running` flag
- **Database inspection**: Query SQLite directly with `sqlite3 helldivers2.db` for historical data
- **Logs**: Check terminal/Docker logs for scraper errors (logged at ERROR level with exception details)
- **API docs**: Navigate to http://localhost:5000/docs (Swagger UI) or http://localhost:5000/redoc

## Common Pitfalls to Avoid
- ❌ **Blocking operations in endpoints**: All endpoints are `async`, never use `time.sleep()`; use `await asyncio.sleep()`
- ❌ **Database connection leaks**: Always use context manager `with sqlite3.connect():`
- ❌ **Missing error context**: Log full exceptions with `logger.error(f"...: {e}")` for debugging
- ❌ **Hardcoded values**: Use config.py for timeouts (30s), intervals (300s), API URLs
- ❌ **Assuming data exists**: Always check `if data:` before processing; scraper methods return `None` on failure

## File Map for Quick Reference
| Component | File | Purpose |
|-----------|------|---------|
| Python Version | `.python-version` | Specifies Python 3.14.0 (pyenv/asdf support) |
| Project Config | `pyproject.toml` | Build system, dependencies, tool config (ruff, mypy, pytest) |
| Makefile | `Makefile` | Bash-based dev/prod/docker/lint targets (aligned with MCP) |
| API Routes | `src/app.py` | 30+ FastAPI endpoints with lifecycle management |
| Data Fetching | `src/scraper.py` | HTTP client for Hell Divers 2 API |
| Persistence | `src/database.py` | SQLite schema + CRUD operations |
| Scheduling | `src/collector.py` | APScheduler background tasks (5-minute cycle) |
| Settings | `src/config.py` | Environment-based configuration classes |
| Integration Tests | `tests/demo.py` | 350+ lines of colored endpoint tests |
| CI/CD Workflows | `.github/workflows/` | tests.yml, docker.yml, auto-approve.yml |
| AI Instructions | `.github/copilot-instructions.md` | This file (aligned with MCP project) |
| Documentation | `DEVELOPMENT.md` | Architecture & design decisions |
