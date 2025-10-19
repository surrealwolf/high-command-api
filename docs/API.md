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

### Get Planet Status
```http
GET /api/planets/{planet_index}
```
Get status of a specific planet.

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

## Biome Endpoints

### Get Biomes
```http
GET /api/biomes
```
Get information about all available biomes.

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
```json
{
  "detail": "No war status data available"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to fetch war status"
}
```

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
