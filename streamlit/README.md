# 🅿️ Free Parking Bot - Streamlit Deployment

This is the Streamlit web interface deployment for the Free Parking Bot, providing a web-based dashboard for finding and managing parking spots.

## Features

- **🔍 Interactive Parking Search**: Find parking spots by location or address
- **🗺️ Interactive Maps**: Visualize parking spots on maps with color-coded status
- **📊 Real-time Statistics**: View database statistics and trends
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🌐 Web-based Interface**: Accessible from any web browser

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_streamlit.txt
```

### 2. Initialize Database
```bash
# Fetch OSM data for parking spots
python osm_fetcher.py

# Initialize database tables
python -c "from database import init_db; init_db()"
```

### 3. Run Streamlit App
```bash
# Local development
streamlit run app.py

# With specific port
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

### 4. Access the Application
Open your browser and go to `http://localhost:8501`

## Deployment Options

### Local Development
```bash
# Run with auto-reload
streamlit run app.py --server.headless true --server.fileWatcherType "all"
```

### Cloud Deployment (Streamlit Community Cloud)

1. **Prepare your app**:
   ```bash
   # Install dependencies
   pip install -r requirements_streamlit.txt
   
   # Test locally
   streamlit run app.py
   ```

2. **Deploy to Streamlit Community Cloud**:
   - Push your code to GitHub
   - Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Set environment variables (if needed)
   - Deploy

### Docker Deployment

```bash
# Build Docker image
docker build -t parking-bot-streamlit .

# Run container
docker run -p 8501:8501 -v $(pwd)/data:/app/data parking-bot-streamlit
```

### Heroku Deployment

1. **Create `Procfile`**:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DB_PATH` | Database file path | No | `parking.db` |
| `STREAMLIT_SERVER_PORT` | Streamlit server port | No | `8501` |
| `STREAMLIT_SERVER_ADDRESS` | Streamlit server address | No | `localhost` |
| `BOT_TOKEN` | Telegram bot token (optional) | No | - |

## Database Setup

### First Time Setup
```bash
# Fetch parking data from OpenStreetMap
python osm_fetcher.py minsk    # Minsk only
python osm_fetcher.py moscow   # Moscow only
python osm_fetcher.py          # Both cities

# Initialize database structure
python -c "from database import init_db; init_db()"
```

### Database Maintenance
```bash
# Check database status
sqlite3 parking.db "SELECT COUNT(*) FROM spots; SELECT COUNT(*) FROM reports;"

# Clean old reports (older than 30 days)
sqlite3 parking.db "DELETE FROM reports WHERE datetime(reported_at) < datetime('now', '-30 days');"
```

## App Features

### Pages

1. **🏠 Home**: Overview and statistics
2. **🔍 Find Parking**: Search for parking spots by location
3. **📊 Statistics**: Detailed analytics and charts
4. **🗺️ Map View**: Interactive map of all parking spots
5. **⚙️ Settings**: Configuration and database management

### Key Components

- **Search Engine**: Find nearest parking spots using spatial algorithms
- **Status System**: Real-time parking status from crowd-sourced reports
- **Interactive Maps**: Folium integration for geographic visualization
- **Statistics**: Plotly charts for data visualization
- **Responsive UI**: Streamlit components for modern web interface

## Customization

### Adding New Cities
1. Update `CITIES` in `config.py`:
   ```python
   CITIES = {
       "minsk": (53.80, 27.40, 53.95, 27.70),
       "moscow": (55.55, 37.32, 55.92, 37.85),
       "your_city": (south, west, north, east),
   }
   ```

2. Fetch new data:
   ```bash
   python osm_fetcher.py your_city
   ```

### Styling
- Modify CSS in `app.py` for custom styling
- Update Streamlit theme in `st.set_page_config()`
- Customize colors and layout in components

### Adding Features
- Integrate external APIs (Google Maps, HERE maps)
- Add user authentication
- Implement real-time updates with WebSockets
- Add payment integration for premium features

## Performance Optimization

### Caching
```python
# In Streamlit app
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_parking_data():
    return fetch_parking_data()
```

### Database Optimization
- Add indexes for frequent queries
- Implement connection pooling
- Use SQLite WAL mode for better concurrency

### Map Optimization
- Limit map markers to 1000 points max
- Implement clustering for dense areas
- Use tile layers for better performance

## Troubleshooting

### Common Issues

1. **Database not found**:
   ```bash
   # Initialize database
   python -c "from database import init_db; init_db()"
   ```

2. **Missing dependencies**:
   ```bash
   # Install requirements
   pip install -r requirements_streamlit.txt
   ```

3. **Map not loading**:
   - Check Folium installation
   - Verify JavaScript is enabled in browser
   - Check network connectivity

### Debug Commands
```bash
# Test database connection
python -c "import sqlite3; print(sqlite3.connect('parking.db'))"

# Test Streamlit app
streamlit run app.py --server.headless true --server.loggerLevel info

# Check Streamlit logs
streamlit run app.py --server.fileWatcherType "all"
```

## Security Considerations

1. **Database Security**:
   - Keep database file in secure location
   - Use proper file permissions
   - Backup regularly

2. **API Keys**:
   - Never hardcode API keys
   - Use environment variables
   - Implement proper key rotation

3. **Web Security**:
   - Use HTTPS in production
   - Implement proper CORS policies
   - Validate user input

## Support and Maintenance

### Regular Tasks
- Update dependencies regularly
- Monitor database performance
- Update OSM data weekly
- Review user feedback and suggestions

### Backup Strategy
```bash
# Daily backup
sqlite3 parking.db ".backup backup_$(date +%Y%m%d).db"

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
mkdir -p $BACKUP_DIR
sqlite3 parking.db ".backup $BACKUP_DIR/parking_$(date +%Y%m%d_%H%M%S).db"
```

### Monitoring
- Check application logs
- Monitor database performance
- Track user engagement metrics
- Review error reports