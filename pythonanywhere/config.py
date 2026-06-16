# ─────────────────────────────────────────────
#  config.py  —  All tuneable settings in one place
# ─────────────────────────────────────────────

import os

# Telegram bot token.
# Required on deploy (PythonAnywhere). You can set it as an environment variable.
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")  # paste from @BotFather if running locally

# SQLite path (must be writable). Defaults to local file.
# On PythonAnywhere, use absolute path to your home directory
DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "parking.db"))

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is not set. Set environment variable BOT_TOKEN before starting the bot."
    )

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
