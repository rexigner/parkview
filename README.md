# 🅿️ Free Parking Bot - Deployment Configurations

This project provides three different deployment configurations for the Free Parking Bot:

1. **PythonAnywhere** - Simple deployment for PythonAnywhere hosting platform
2. **Cloud Deploy** - Generic cloud deployment with Docker support
3. **Streamlit** - Web-based interface using Streamlit

## 📁 Project Structure

```
parking_bot_deploy/
├── README.md                           # This main file
├── pythonanywhere/                     # PythonAnywhere deployment
│   ├── README.md                      # PythonAnywhere-specific setup
│   ├── config.py                      # Config for PythonAnywhere
│   ├── main.py                        # Main bot file
│   ├── database.py                    # Database management
│   ├── engine.py                      # Core engine
│   ├── osm_fetcher.py                # OSM data fetcher
│   ├── pythonanywhere_onefile_runner.py # PythonAnywhere runner
│   └── requirements_pythonanywhere.txt # Dependencies
├── cloud_deploy/                      # Generic cloud deployment
│   ├── README.md                      # Cloud deployment guide
│   ├── config.py                      # Config for cloud deployment
│   ├── database.py                    # Database management
│   ├── engine.py                      # Core engine
│   ├── main.py                        # Main bot file
│   ├── osm_fetcher.py                # OSM data fetcher
│   ├── Dockerfile                     # Docker configuration
│   ├── docker-compose.yml             # Docker Compose setup
│   └── requirements_normal_deploy.txt # Dependencies
└── streamlit/                         # Streamlit web interface
    ├── README.md                      # Streamlit deployment guide
    ├── app.py                         # Main Streamlit application
    ├── config.py                      # Config for Streamlit
    ├── database.py                    # Database management
    ├── engine.py                      # Core engine
    ├── osm_fetcher.py                # OSM data fetcher
    ├── Dockerfile                     # Docker configuration
    ├── docker-compose.yml             # Docker Compose setup
    └── requirements_streamlit.txt    # Dependencies
```

## 🚀 Quick Start

### Choose Your Deployment Method

#### 1. PythonAnywhere (Recommended for beginners)
- **Best for**: Simple, hassle-free deployment
- **Setup**: Follow instructions in `pythonanywhere/README.md`
- **Features**: Telegram bot only

#### 2. Cloud Deploy (Best for production)
- **Best for**: AWS, GCP, Heroku, or any cloud platform
- **Setup**: Follow instructions in `cloud_deploy/README.md`
- **Features**: Docker containerization, scalable

#### 3. Streamlit (Best for web interface)
- **Best for**: Web-based dashboard and admin interface
- **Setup**: Follow instructions in `streamlit/README.md`
- **Features**: Interactive maps, statistics, web interface

## 📋 Prerequisites for All Deployments

1. **Python 3.11+**
2. **Bot Token**: Get from [@BotFather](https://t.me/BotFather) in Telegram
3. **Database**: SQLite database will be created automatically
4. **OSM Data**: Run `python osm_fetcher.py` to populate database

## 🔧 Common Setup Steps

### 1. Install Dependencies
```bash
# For each deployment folder
cd pythonanywhere
pip install -r requirements_pythonanywhere.txt

# Or
cd cloud_deploy
pip install -r requirements_normal_deploy.txt

# Or
cd streamlit
pip install -r requirements_streamlit.txt
```

### 2. Initialize Database
```bash
# Run OSM data fetcher (choose cities as needed)
python osm_fetcher.py          # All cities
python osm_fetcher.py minsk     # Minsk only
python osm_fetcher.py moscow    # Moscow only
```

### 3. Set Environment Variables
```bash
export BOT_TOKEN="your_bot_token_here"
export DB_PATH="/path/to/parking.db"
```

## 🏗️ Architecture Overview

### Core Components
- **main.py**: Telegram bot using aiogram v3
- **database.py**: SQLite database management
- **engine.py**: Spatial search and occupancy scoring
- **config.py**: Configuration management
- **osm_fetcher.py**: OpenStreetMap data integration

### Features
- **Telegram Bot**: Interactive parking spot finder
- **Crowd-sourced Reports**: Real-time parking status
- **Spatial Search**: Find nearest parking spots
- **Multi-language**: English and Russian support
- **Status System**: Free, likely full, full status indicators

## 🌐 Supported Cities

Currently supports:
- **Minsk, Belarus**
- **Moscow, Russia**

Adding new cities:
1. Update `CITIES` in `config.py`
2. Run `python osm_fetcher.py new_city_name`

## 🔍 How It Works

1. **Data Collection**: Fetch parking data from OpenStreetMap
2. **User Search**: Users share location or enter address
3. **Spot Finding**: Find nearest parking spots within radius
4. **Status Display**: Show real-time status from user reports
5. **Crowd-sourcing**: Users report back when they arrive

## 📊 Features by Deployment

| Feature | PythonAnywhere | Cloud Deploy | Streamlit |
|---------|---------------|--------------|-----------|
| Telegram Bot | ✅ | ✅ | ✅ |
| Web Interface | ❌ | ❌ | ✅ |
| Interactive Maps | ❌ | ❌ | ✅ |
| Statistics Dashboard | ❌ | ❌ | ✅ |
| Docker Support | ❌ | ✅ | ✅ |
| Scalability | ⚠️ | ✅ | ✅ |
| Custom Domain | ✅ | ✅ | ✅ |

## 🔄 Migrating Between Deployments

### PythonAnywhere → Cloud
```bash
# Copy files
cp -r pythonanywhere/* cloud_deploy/

# Update config
cd cloud_deploy
# Modify config.py for cloud environment
# Add Docker and docker-compose.yml
```

### Cloud → Streamlit
```bash
# Copy files
cp -r cloud_deploy/* streamlit/

# Add web interface
cd streamlit
# Create app.py with Streamlit interface
# Add web-specific dependencies
```

## 🛠️ Development Tips

### Testing
```bash
# Test database connection
python -c "from database import init_db; init_db()"

# Test spot finding
python -c "from engine import find_nearest_spots; print(find_nearest_spots(53.9045, 27.5615))"

# Test bot
python main.py
```

### Debugging
```bash
# Enable verbose logging
export PYTHONPATH=.
python -m logging.config -f logging.conf main.py

# Check database
sqlite3 parking.db ".tables"
sqlite3 parking.db "SELECT COUNT(*) FROM spots;"
```

## 📈 Monitoring and Maintenance

### Database Maintenance
```bash
# Clean old reports
sqlite3 parking.db "DELETE FROM reports WHERE datetime(reported_at) < datetime('now', '-30 days');"

# Update statistics
sqlite3 parking.db "SELECT COUNT(*) FROM spots; SELECT COUNT(*) FROM reports;"
```

### Performance Monitoring
- Monitor query response times
- Track database growth
- Monitor user engagement
- Review error logs

## 🔒 Security Considerations

1. **Bot Token**: Never commit to version control
2. **Database**: Keep in secure location, backup regularly
3. **API Keys**: Use environment variables
4. **Network**: Use HTTPS in production

## 🤝 Contributing

1. Choose appropriate deployment folder
2. Follow existing code style
3. Update documentation
4. Test thoroughly

## 📞 Support

For deployment-specific questions, refer to the respective README files:
- `pythonanywhere/README.md` - PythonAnywhere setup
- `cloud_deploy/README.md` - Cloud deployment guide
- `streamlit/README.md` - Streamlit web interface

## 📄 License

This project is open source and available under the MIT License.