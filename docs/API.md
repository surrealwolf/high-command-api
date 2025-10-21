# API Reference

## Base URL
```
http://localhost:5000/api
```

## Health & Root Endpoints

### Health Check
```http
GET /api/health
```
Check API health and collector status.

**Response:**
```json
{
  "status": "healthy",
  "collector_running": true
}
```

### Root Information
```http
GET /
```
Get API information and documentation links.

**Response:**
```json
{
  "name": "Hell Divers 2 API",
  "version": "1.0.0",
  "description": "Real-time scraper for Hell Divers 2 game data",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

## War Endpoints

### Get War Status
```http
GET /api/war/status
```
Get the current war status.

**Response:**
```json
{
  "id": 1,
  "status": "active",
  "message": "The war is ongoing"
}
```

### Refresh War Status
```http
POST /api/war/status/refresh
```
Manually trigger a refresh of war status data.

**Response:**
```json
{
  "success": true,
  "data": { /* war status data */ }
}
```

## Campaign Endpoints

### Get Campaigns
```http
GET /api/campaigns
```
Get campaign information from the Hell Divers 2 API.

**Cache Fallback**: If upstream API is unavailable, returns most recent cached campaign data.

**Response:**
```json
{
  "campaigns": [
    {
      "id": 1,
      "planet_index": 0,
      "status": "active"
    }
  ]
}
```

**Error Responses:**
- `503 Service Unavailable`: Upstream API failed and no cached data available
```json
{
  "detail": "No campaign data available (live fetch failed and no cached data)"
}
```

### Get Active Campaigns
```http
GET /api/campaigns/active
```
Get only active campaigns from the database.

**Response:**
```json
[
  {
    "id": 1,
    "planet_index": 0,
    "status": "active"
  }
]
```

## Planet Endpoints

### Get All Planets
```http
GET /api/planets
```
Get information about all planets.

**Cache Fallback**: If upstream API is unavailable, returns most recent cached planet snapshot.

**Response:**
```json
[
  {
    "index": 0,
    "name": "Malevelon Creek",
    "owner": "Humans",
    "status": "contested"
  }
]
```

**Error Responses:**
- `503 Service Unavailable`: Upstream API failed and no cached data available
```json
{
  "detail": "Failed to fetch planets and no cached data available"
}
```

### Get Planet Status
```http
GET /api/planets/{planet_index}
```
Get status of a specific planet.

**Cache Fallback**: If upstream API is unavailable, returns most recent cached status for this planet.

**Parameters:**
- `planet_index` (integer): The planet index

**Response:**
```json
{
  "index": 0,
  "name": "Malevelon Creek",
  "owner": "Humans",
  "status": "contested",
  "biome": "Swamp"
}
```

**Error Responses:**
- `503 Service Unavailable`: Upstream API failed and no cached data for this planet
```json
{
  "detail": "Failed to fetch planet {planet_index} and no cached data available"
}
```

### Get Planet History
```http
GET /api/planets/{planet_index}/history?limit=10
```
Get historical status data for a planet.

**Parameters:**
- `planet_index` (integer): The planet index
- `limit` (integer, optional): Number of records (1-100, default: 10)

**Response:**
```json
[
  {
    "data": { /* planet data */ },
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

## Statistics Endpoints

### Get Latest Statistics
```http
GET /api/statistics
```
Get the latest global game statistics.

**Response:**
```json
{
  "total_players": 500000,
  "total_kills": 1000000,
  "missions_won": 50000,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Get Statistics History
```http
GET /api/statistics/history?limit=100
```
Get historical statistics data.

**Parameters:**
- `limit` (integer, optional): Number of records (1-1000, default: 100)

**Response:**
```json
[
  {
    "data": { /* statistics data */ },
    "timestamp": "2024-01-15T10:30:00"
  }
]
```

### Refresh Statistics
```http
POST /api/statistics/refresh
```
Manually trigger a refresh of statistics data.

**Response:**
```json
{
  "success": true,
  "data": { /* statistics data */ }
}
```

## Faction Endpoints

### Get Factions
```http
GET /api/factions
```
Get all faction information.

**Cache Fallback**: If upstream API is unavailable, returns factions from most recent cached war status.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Humans",
    "description": "The main player faction"
  },
  {
    "id": 2,
    "name": "Bugs",
    "description": "Terminid enemies"
  }
]
```

**Error Responses:**
- `503 Service Unavailable`: Upstream API failed and no cached faction data
```json
{
  "detail": "Failed to fetch factions and no cached data available"
}
```

## Biome Endpoints

### Get Biomes
```http
GET /api/biomes
```
Get information about all available biomes.

**Cache Fallback**: If upstream API is unavailable, returns biomes from most recent cached planet data.

**Response:**
```json
[
  {
    "id": 0,
    "name": "Swamp",
    "description": "Wet and muddy terrain"
  },
  {
    "id": 1,
    "name": "Desert",
    "description": "Arid and sandy environment"
  }
]
```

**Error Responses:**
- `503 Service Unavailable`: Upstream API failed and no cached biome data
```json
{
  "detail": "Failed to fetch biomes and no cached data available"
}
```

## Documentation Endpoints

### OpenAPI Schema
```http
GET /openapi.json
```
Get the OpenAPI (formerly Swagger) schema.

### Swagger UI
```
http://localhost:5000/docs
```
Interactive API documentation with "Try it out" functionality.

### ReDoc
```
http://localhost:5000/redoc
```
Alternative API documentation interface.

## Error Responses

### 404 Not Found
Returned when a resource doesn't exist or no data has been collected yet.

**Example scenarios**:
- Requesting history for a planet that has never been tracked
- Accessing active campaigns when none are currently active
- Querying data before the first collection cycle completes

```json
{
  "detail": "No war status data available"
}
```

### 500 Internal Server Error
Returned when an unexpected server error occurs.

**Example scenarios**:
- Failed to refresh data due to scraper error
- Database write failure
- Unexpected exception in request handler

```json
{
  "detail": "Failed to fetch war status"
}
```

### 503 Service Unavailable
**New in cache-fallback feature**: Returned by cache-enabled endpoints when BOTH conditions are true:
1. Upstream Hell Divers 2 API is unavailable or returns an error
2. No cached data exists in the database

**Endpoints that return 503**:
- `GET /api/campaigns`
- `GET /api/planets`
- `GET /api/planets/{planet_index}`
- `GET /api/factions`
- `GET /api/biomes`

**What this means for API consumers**:
- A 503 response indicates a genuine service degradation (upstream down + no cache)
- A 200 response on these endpoints may contain cached data from the last successful collection
- Consider implementing retry logic with exponential backoff for 503 responses
- Monitor for persistent 503s which may indicate prolonged upstream outage

```json
{
  "detail": "No campaign data available (live fetch failed and no cached data)"
}
```

### Understanding Cache Fallback
Cache-enabled endpoints follow this logic:
1. **Try live API** - Attempt to fetch fresh data from upstream
2. **Fallback to cache** - If live fetch fails, try to retrieve from database
3. **Return 200** - If either live or cached data is available
4. **Return 503** - Only if both live fetch AND cache retrieval fail

This ensures maximum availability and resilience against upstream API outages.

### 422 Unprocessable Entity
```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 1000",
      "type": "value_error.number.not_le"
    }
  ]
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions may include:
- Request throttling per IP
- Daily request limits
- Concurrent connection limits

## CORS

CORS is enabled for all origins. Requests from any origin are allowed:
- Origins: `*`
- Methods: `*`
- Headers: `*`

## Data Collection Interval

Background data collection runs every **5 minutes** by default.
This can be configured via environment variables or the `src/config.py` file.

## Authentication

Currently no authentication is required. Future versions may include:
- API key authentication
- JWT token support
- Rate limiting per key
