# ─────────────────────────────────────────────
#  config.py  —  Streamlit deployment configuration
# ─────────────────────────────────────────────

import os

# Telegram bot token.
# Optional for Streamlit web interface, required if running Telegram bot alongside.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # paste from @BotFather if running locally

# SQLite path (must be writable). Defaults to local file.
DB_PATH = os.environ.get("DB_PATH", "parking.db")

# Streamlit configuration
STREAMLIT_SERVER_PORT = int(os.environ.get("STREAMLIT_SERVER_PORT", 8501))
STREAMLIT_SERVER_ADDRESS = os.environ.get("STREAMLIT_SERVER_ADDRESS", "localhost")

# ── City bounding boxes (south, west, north, east) ──────────────────────────
CITIES = {
    "minsk":  (53.80, 27.40, 53.95, 27.70),
    "moscow": (55.55, 37.32, 55.92, 37.85),
}

# ── Search parameters ────────────────────────────────────────────────────────
MAX_RESULTS        = 5     # spots returned per query
SEARCH_RADIUS_KM   = 1.5   # how far to look

# ── Crowdsource / decay ──────────────────────────────────────────────────────
REPORT_DECAY_MINUTES = 20  # reports older than this are ignored
CONFIRM_THRESHOLD    = 3   # "full" reports needed to hide a spot
