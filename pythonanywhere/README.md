# 🅿️ Free Parking Bot - PythonAnywhere Deployment

This is the PythonAnywhere-specific deployment configuration for the Free Parking Bot.

## Quick Start

### 1. Upload Files
Upload all files from this directory to your PythonAnywhere account.

### 2. Install Dependencies
```bash
pip install -r requirements_pythonanywhere.txt
```

### 3. Set Environment Variables
In your PythonAnywhere dashboard:
1. Go to "Web" tab
2. Set environment variables:
   - `BOT_TOKEN`: Your bot token from @BotFather
   - `DB_PATH`: `/home/yourusername/parking_bot/parking.db`

### 4. Seed Database (First Time)
```bash
python osm_fetcher.py
```

### 5. Run the Bot
You can run the bot using:
```bash
python pythonanywhere_onefile_runner.py
```

Or create a scheduled task to run continuously.

## PythonAnywhere Specific Files

- `pythonanywhere_onefile_runner.py` - Special runner for PythonAnywhere environment
- `config.py` - Modified for PythonAnywhere paths
- `requirements_pythonanywhere.txt` - Dependencies for PythonAnywhere

## Running as a Web App

1. Go to PythonAnywhere → Web
2. Add a new web app with "Manual configuration"
3. Set the path to point to `pythonanywhere_onefile_runner.py`
4. Set environment variables in the "Environment variables" section

## Database Notes

The SQLite database will be created in your project directory. Make sure the directory is writable by PythonAnywhere.

## Troubleshooting

- Check that `BOT_TOKEN` environment variable is set
- Ensure database path is writable
- Check PythonAnywhere logs for error messages