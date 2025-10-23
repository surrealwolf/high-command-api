# Backend Data Refresh Guide

## Issue Diagnosis ✅

The API is working correctly, but the backend database only contains test/stale data:

- ✅ Sorting logic: Working correctly (newest first)
- ✅ Timestamp parsing: Working correctly  
- ✅ API response format: Correct
- ❌ **Data freshness**: Only has ~10 dispatches from March 2024
- ❌ **No current data**: No October 2025 dispatches in database

## Root Causes

This could happen due to:

1. **Scraper not running** - Background collector/scraper task isn't active
2. **Upstream API unavailable** - Hell Divers 2 API down or rate-limited
3. **Test data only** - Development database with fixtures, not live data
4. **Initial state** - First time running, scraper hasn't collected data yet

## Solutions

### Solution 1: Manually Trigger Data Refresh (Quickest)

Use the refresh endpoints to force data collection:

```bash
# Refresh all dispatches
curl -X POST http://localhost:5000/api/dispatches/refresh

# Refresh assignments  
curl -X POST http://localhost:5000/api/assignments/refresh

# Refresh planet events
curl -X POST http://localhost:5000/api/planet-events/refresh

# Refresh all war data
curl -X POST http://localhost:5000/api/war/status/refresh
```

Expected response:
```json
{
  "success": true,
  "data": {
    "dispatches": [
      {
        "id": 1,
        "message": "...",
        "published": "2025-10-21T..."
      }
    ]
  }
}
```

### Solution 2: Start Background Collector (Automatic Updates)

Ensure the collector is running when API starts:

```bash
# Check collector status
curl http://localhost:5000/api/health

# Expected response includes:
# "collector_running": true
```

If collector is not running, the API is missing the background refresh loop.

### Solution 3: Verify Upstream API Connection

Test connectivity to Hell Divers 2 community API:

```bash
# Direct test to Hell Divers 2 API (no rate limiting)
curl -H "X-Super-Client: high-command-test" \
     -H "X-Super-Contact: dev@example.com" \
     https://api.helldivers2.dev/api/v1/dispatches
```

If this returns fresh data, the upstream is working.

### Solution 4: Reset and Reinitialize Database (Nuclear Option)

If all else fails, remove old database and force fresh collection:

```bash
# Stop the API first (Ctrl+C in terminal)

# Backup old database
cp helldivers2.db helldivers2.db.backup

# Remove old database  
rm helldivers2.db

# Restart API - will create fresh database and collect data
make dev
```

## Data Collection Flow

```
Hell Divers 2 Community API
    ↓
Scraper (src/scraper.py)
    ↓
Collector (src/collector.py) - runs every 5 minutes
    ↓
Database (helldivers2.db - SQLite)
    ↓
FastAPI Endpoints (src/app.py)
    ↓
Frontend/Client
```

## Configuration

### Check Collector Settings (src/config.py)

```python
# Development: collects every 60 seconds
class DevelopmentConfig:
    COLLECTION_INTERVAL = 60

# Production: collects every 300 seconds (5 minutes)  
class ProductionConfig:
    COLLECTION_INTERVAL = 300
```

### Enable Debug Logging

Check logs to see if collector is working:

```bash
# In development, watch for:
# "Collector started"
# "Collecting all game data..."
# "Collected X dispatches"
```

## Verification Checklist

- [ ] API starts without errors
- [ ] Health endpoint shows `collector_running: true`
- [ ] Manual refresh endpoints return data (200 status)
- [ ] Database file `helldivers2.db` exists and has size > 100KB
- [ ] New dispatches appear after running refresh
- [ ] Timestamps are recent (not March 2024)

## Expected Behavior After Fix

After ensuring fresh data collection:

```bash
# Should return current October 2025 dispatches
curl http://localhost:5000/api/dispatches?limit=10&sort=newest

# Response should have:
# - Multiple dispatches
# - Recent timestamps (October 2025)
# - Properly formatted JSON
```

## Frontend Validation

Once backend has fresh data:

```javascript
// In News.tsx, you should see:
// 1. Recent timestamps in console logs
// 2. Current dispatch content
// 3. Proper sorting (newest first)
// 4. No "No dispatches" fallback message
```

## Debugging Tips

### Check Database Contents

```bash
# Open SQLite CLI
sqlite3 helldivers2.db

# See table info
.tables
.schema dispatches

# See latest dispatches sorted by published date
SELECT * FROM dispatches ORDER BY json_extract(data, '$.published') DESC LIMIT 5;

# Count total dispatches
SELECT COUNT(*) FROM dispatches;
```

### Monitor Collector Logs

```bash
# In your terminal running `make dev`, watch for:
# [INFO] Collector: Collecting all game data
# [INFO] Collector: Collected X dispatches
# [ERROR] Collector: Failed to fetch...
```

### Check API Response

```bash
# Get raw API response with headers
curl -v http://localhost:5000/api/dispatches?limit=20

# Check timestamps in response
curl http://localhost:5000/api/dispatches | jq '.[0].published'
```

## Next Steps

1. **Immediate**: Run manual refresh endpoint
   ```bash
   curl -X POST http://localhost:5000/api/dispatches/refresh
   ```

2. **Verify**: Check database timestamps
   ```bash
   sqlite3 helldivers2.db "SELECT published FROM dispatches ORDER BY published DESC LIMIT 1;"
   ```

3. **Monitor**: Watch collector logs for auto-updates
   ```bash
   # Keep terminal open during `make dev`
   ```

4. **Frontend**: Refresh browser to see new data

## Support

If data still doesn't update:

- Check `.env` file for correct API headers (SUPER_CLIENT_HEADER, SUPER_CONTACT_HEADER)
- Verify network connectivity: `ping api.helldivers2.dev`
- Check rate limits haven't been exceeded (wait 10 minutes before retry)
- Review Hell Divers 2 API status: https://api.helldivers2.dev

---

**Remember**: The frontend and API logic are working correctly. This is purely a data freshness issue in the backend database. Once the scraper collects current data, everything will display properly.
