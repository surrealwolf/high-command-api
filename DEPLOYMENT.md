# Hell Divers 2 API - Deployment Guide

## Development Setup

### Local Development

1. **Clone and setup**:
```bash
cd high-command-api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Run the API**:
```bash
python app.py
```

3. **Access the API**:
- API: http://localhost:5000
- Swagger UI: http://localhost:5000/docs
- ReDoc: http://localhost:5000/redoc

4. **Run tests**:
```bash
python demo.py
```

## Production Deployment

### Docker Deployment

**Build and run with Docker**:
```bash
# Build the image
docker build -t hell-divers-2-api .

# Run the container
docker run -d -p 5000:5000 \
  -v $(pwd)/helldivers2.db:/app/helldivers2.db \
  --name hell-divers-api \
  hell-divers-2-api
```

**Using Docker Compose**:
```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Manual Server Deployment

**On Ubuntu/Debian**:

1. **Install Python and dependencies**:
```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-pip
```

2. **Clone the repository**:
```bash
git clone <repository-url> /opt/hell-divers-api
cd /opt/hell-divers-api
```

3. **Setup virtual environment**:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Create systemd service**:
```bash
sudo nano /etc/systemd/system/hell-divers-api.service
```

Add the following content:
```ini
[Unit]
Description=Hell Divers 2 API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/hell-divers-api
Environment="PATH=/opt/hell-divers-api/venv/bin"
ExecStart=/opt/hell-divers-api/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Enable and start the service**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable hell-divers-api
sudo systemctl start hell-divers-api
```

6. **Check service status**:
```bash
sudo systemctl status hell-divers-api
sudo journalctl -u hell-divers-api -f
```

### Nginx Reverse Proxy Configuration

Add this to your Nginx configuration:

```nginx
server {
    listen 80;
    server_name api.helldive.rs;

    location / {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### Environment Configuration

Create a `.env` file for production:
```env
FLASK_ENV=production
API_PORT=5000
DATABASE_URL=sqlite:////data/helldivers2.db
LOG_LEVEL=INFO
SCRAPE_INTERVAL=300
```

## Monitoring

### Health Check

Monitor the API status:
```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "healthy",
  "collector_running": true
}
```

### Logs

View application logs:
```bash
# Local development
tail -f logs/app.log

# Docker
docker-compose logs -f api

# Systemd
journalctl -u hell-divers-api -f
```

## Performance Tuning

### Uvicorn Configuration

Edit `app.py` to adjust workers:
```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        workers=4,  # Increase for more concurrent requests
        loop="uvloop"  # Optional: faster event loop
    )
```

### Database Optimization

The SQLite database includes indexes for faster queries. For high-volume scenarios, consider:
1. Increasing the database file size
2. Implementing retention policies (delete old data)
3. Migrating to PostgreSQL

## Troubleshooting

### API Connection Issues

1. Check if the API is running:
```bash
curl -v http://localhost:5000/api/health
```

2. Check logs for errors:
```bash
grep "ERROR" logs/app.log
```

3. Verify network connectivity to Hell Divers 2 API:
```bash
curl -v https://api.live.prod.theadultswim.com/helldivers2/status
```

### Database Issues

1. Reset the database:
```bash
rm helldivers2.db
# Restart the API - it will recreate the schema
```

2. Check database integrity:
```bash
sqlite3 helldivers2.db ".tables"
sqlite3 helldivers2.db ".schema"
```

### Memory Issues

Monitor memory usage:
```bash
# Check process memory
ps aux | grep "python app.py"

# Monitor with top
top -p <PID>
```

## Backup and Maintenance

### Database Backups

```bash
# Backup the database
cp helldivers2.db helldivers2.db.backup.$(date +%Y%m%d_%H%M%S)

# Backup to a specific location
cp helldivers2.db /backups/helldivers2_$(date +%Y%m%d_%H%M%S).db
```

### Cleanup

Remove old data:
```sql
-- Example: Delete war status older than 30 days
DELETE FROM war_status 
WHERE timestamp < datetime('now', '-30 days');

-- Vacuum to reclaim space
VACUUM;
```

## Scaling Considerations

1. **Load Balancing**: Use multiple API instances behind a load balancer
2. **Caching**: Implement Redis for frequently accessed data
3. **Database**: Migrate to PostgreSQL for better concurrency
4. **Async Operations**: Use Celery for long-running tasks
5. **CDN**: Cache static documentation with CloudFlare

## Security

1. **HTTPS**: Always use HTTPS in production with SSL certificates
2. **Rate Limiting**: Implement request rate limiting
3. **Authentication**: Add API key authentication if needed
4. **CORS**: Configure CORS properly for your frontend domains
5. **Input Validation**: All inputs are validated via Pydantic

## Support

For issues or questions:
1. Check the README.md for basic setup
2. Review the demo.py for API usage examples
3. Check API logs for error messages
4. Verify network connectivity to the Hell Divers 2 API
