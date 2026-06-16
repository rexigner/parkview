# ─────────────────────────────────────────────
#  osm_fetcher.py  —  Pull free-parking nodes from OpenStreetMap
#
#  Run once to seed the database, then re-run weekly to refresh.
#  Usage:
#      python osm_fetcher.py              # fetches all cities in config
#      python osm_fetcher.py minsk        # fetches one city
# ─────────────────────────────────────────────

import sys
import time
import requests
from database import get_conn, init_db
from config import CITIES

OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def build_query(bbox: tuple) -> str:
    s, w, n, e = bbox
    # Fetch nodes AND ways (areas like multi-storey lots).
    # fee=no  → explicitly free
    # no fee tag → possibly free (we label these separately)
    return f"""
[out:json][timeout:90];
(
  node["amenity"="parking"]["fee"="no"]({s},{w},{n},{e});
  way ["amenity"="parking"]["fee"="no"]({s},{w},{n},{e});
  node["amenity"="parking"][!"fee"]({s},{w},{n},{e});
  way ["amenity"="parking"][!"fee"]({s},{w},{n},{e});
);
out center body;
"""


def _classify(tags: dict) -> tuple[str, str]:
    """Return (spot_type, certainty) from OSM tags."""
    access = tags.get("access", "")
    parking = tags.get("parking", "")

    if access in ("private", "permissive") or parking == "underground":
        return "courtyard", "low"
    if parking in ("multi-storey", "surface"):
        return "lot", "high"
    return "street", "high"


def fetch_city(city_name: str) -> int:
    bbox = CITIES.get(city_name)
    if not bbox:
        print(f"[OSM] Unknown city '{city_name}'. Add it to CITIES in config.py.")
        return 0

    print(f"[OSM] Querying Overpass for {city_name} …")
    query = build_query(bbox)

    for attempt in range(3):
        try:
            resp = requests.post(
                OVERPASS_URL,
                data={"data": query},
                timeout=120,
                headers={"User-Agent": "FreeParkingBot/1.0"}
            )
            resp.raise_for_status()
            break
        except requests.RequestException as exc:
            print(f"[OSM] Attempt {attempt + 1} failed: {exc}")
            if attempt < 2:
                time.sleep(10)
    else:
        print("[OSM] All attempts failed. Skipping city.")
        return 0

    elements = resp.json().get("elements", [])
    print(f"[OSM] Received {len(elements)} elements.")

    conn = get_conn()
    cur  = conn.cursor()
    inserted = 0

    for el in elements:
        # Ways expose a synthetic 'center' lat/lon
        if el["type"] == "way":
            center = el.get("center", {})
            lat, lon = center.get("lat"), center.get("lon")
        else:
            lat, lon = el.get("lat"), el.get("lon")

        if lat is None or lon is None:
            continue

        tags     = el.get("tags", {})
        osm_id   = f"{el['type']}/{el['id']}"
        name     = tags.get("name") or tags.get("description") or None
        spot_type, certainty = _classify(tags)

        capacity = None
        raw_cap  = tags.get("capacity")
        if raw_cap and raw_cap.isdigit():
            capacity = int(raw_cap)

        cur.execute("""
            INSERT OR IGNORE INTO spots
                (osm_id, lat, lon, name, spot_type, certainty, city, capacity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (osm_id, lat, lon, name, spot_type, certainty, city_name, capacity))

        if cur.rowcount:
            inserted += 1

    conn.commit()
    conn.close()
    print(f"[OSM] Inserted {inserted} new spots for {city_name}.")
    return inserted


def fetch_all() -> None:
    for city in CITIES:
        fetch_city(city)
        time.sleep(5)   # be polite to Overpass


if __name__ == "__main__":
    init_db()
    if len(sys.argv) > 1:
        fetch_city(sys.argv[1].lower())
    else:
        fetch_all()
