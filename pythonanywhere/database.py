# ─────────────────────────────────────────────
#  database.py  —  SQLite schema + connection helper
# ─────────────────────────────────────────────

import sqlite3
from config import DB_PATH


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets you access columns by name
    return conn


def init_db() -> None:
    """Create tables if they don't exist yet."""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS spots (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            osm_id      TEXT    UNIQUE,
            lat         REAL    NOT NULL,
            lon         REAL    NOT NULL,
            name        TEXT,
            spot_type   TEXT    DEFAULT 'street',   -- street | courtyard | lot
            certainty   TEXT    DEFAULT 'high',      -- high | low
            city        TEXT,
            capacity    INTEGER
        );

        -- Crowdsourced status reports from users
        CREATE TABLE IF NOT EXISTS reports (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            spot_id     INTEGER NOT NULL,
            user_id     INTEGER NOT NULL,
            status      TEXT    NOT NULL,            -- 'full' | 'free'
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (spot_id) REFERENCES spots(id)
        );

        -- Speed up proximity queries with a bounding-box pre-filter
        CREATE INDEX IF NOT EXISTS idx_spots_lat ON spots(lat);
        CREATE INDEX IF NOT EXISTS idx_spots_lon ON spots(lon);

        -- Speed up occupancy score lookups
        CREATE INDEX IF NOT EXISTS idx_reports_spot ON reports(spot_id, reported_at);

        -- Per-user settings (language, etc.)
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id INTEGER PRIMARY KEY,
            lang    TEXT NOT NULL DEFAULT 'en'  -- 'en' | 'ru'
        );
    """)
    conn.commit()
    conn.close()
    print("[DB] Schema ready.")

