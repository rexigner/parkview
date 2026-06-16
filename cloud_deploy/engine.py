# ─────────────────────────────────────────────
#  engine.py  —  Spatial search + occupancy scoring
# ─────────────────────────────────────────────

import math
from datetime import datetime, timedelta
from database import get_conn
from config import (
    SEARCH_RADIUS_KM, MAX_RESULTS,
    REPORT_DECAY_MINUTES, CONFIRM_THRESHOLD,
)


# ── Haversine distance ───────────────────────────────────────────────────────

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Return great-circle distance in kilometres."""
    R = 6_371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(d_lon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


# ── Occupancy score ──────────────────────────────────────────────────────────

def get_occupancy(spot_id: int) -> tuple[str, int]:
    """
    Compute live occupancy from decayed user reports.

    Returns
    -------
    status : 'free' | 'likely_full' | 'full'
    report_count : total recent reports (for display)
    """
    conn = get_conn()
    # Use SQLite's own datetime arithmetic to avoid Python↔SQLite format mismatch.
    # CURRENT_TIMESTAMP is UTC; subtracting N minutes keeps everything in-engine.
    rows = conn.execute("""
        SELECT status, COUNT(*) AS cnt
        FROM   reports
        WHERE  spot_id     = ?
          AND  reported_at > datetime('now', ? || ' minutes')
        GROUP  BY status
    """, (spot_id, f"-{REPORT_DECAY_MINUTES}")).fetchall()
    conn.close()

    counts      = {r["status"]: r["cnt"] for r in rows}
    full_count  = counts.get("full", 0)
    free_count  = counts.get("free", 0)
    total       = full_count + free_count

    if full_count >= CONFIRM_THRESHOLD:
        return "full", total
    if full_count > free_count:
        return "likely_full", total
    return "free", total


# ── Nearest-spots query ──────────────────────────────────────────────────────

def find_nearest_spots(user_lat: float, user_lon: float,
                        limit: int = MAX_RESULTS) -> list[dict]:
    """
    Return up to `limit` free/likely-free spots sorted by distance.

    Strategy
    --------
    1. Bounding-box pre-filter in SQL (cheap index scan).
    2. Exact haversine distance in Python.
    3. Occupancy check; skip confirmed-full spots.
    """
    deg = SEARCH_RADIUS_KM / 111.0          # 1° lat ≈ 111 km

    conn = get_conn()
    rows = conn.execute("""
        SELECT id, lat, lon, name, spot_type, certainty, capacity
        FROM   spots
        WHERE  lat BETWEEN ? AND ?
          AND  lon BETWEEN ? AND ?
    """, (
        user_lat - deg, user_lat + deg,
        user_lon - deg, user_lon + deg,
    )).fetchall()
    conn.close()

    results = []
    for row in rows:
        dist_km = haversine(user_lat, user_lon, row["lat"], row["lon"])
        if dist_km > SEARCH_RADIUS_KM:
            continue

        status, report_count = get_occupancy(row["id"])
        if status == "full":
            continue                        # don't show confirmed-full spots

        results.append({
            "id":          row["id"],
            "lat":         row["lat"],
            "lon":         row["lon"],
            "name":        row["name"] or "Unnamed spot",
            "spot_type":   row["spot_type"],
            "certainty":   row["certainty"],
            "capacity":    row["capacity"],
            "distance_m":  int(dist_km * 1000),
            "status":      status,
            "reports":     report_count,
        })

    results.sort(key=lambda x: x["distance_m"])
    return results[:limit]


# ── Reporting ────────────────────────────────────────────────────────────────

def add_report(spot_id: int, user_id: int, status: str) -> None:
    """Persist a user's occupancy report. status must be 'free' or 'full'."""
    if status not in ("free", "full"):
        raise ValueError(f"Invalid status: {status!r}")

    conn = get_conn()
    conn.execute("""
        INSERT INTO reports (spot_id, user_id, status)
        VALUES (?, ?, ?)
    """, (spot_id, user_id, status))
    conn.commit()
    conn.close()
