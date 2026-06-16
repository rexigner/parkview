# ─────────────────────────────────────────────
#  app.py  —  Streamlit web interface for parking bot
# ─────────────────────────────────────────────

import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
try:
    import plotly.express as px
except ModuleNotFoundError:  # allows app to run even if plotly is missing
    px = None
import folium
from datetime import datetime, timedelta


# Import our existing modules
import sys
import os
sys.path.append(os.path.dirname(__file__))

from config import CITIES, SEARCH_RADIUS_KM, MAX_RESULTS
from database import get_conn, init_db
from engine import add_report, find_nearest_spots, get_occupancy, haversine

# Set page config
st.set_page_config(
    page_title="Free Parking Finder",
    page_icon="🅿️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# ── CSS Styling ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1e3a8a;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .status-free { color: #10b981; }
    .status-likely-full { color: #f59e0b; }
    .status-full { color: #ef4444; }
    .map-container {
        height: 500px;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# ── Helper Functions ──────────────────────────────────────────────────────────
def get_db_stats():
    """Get database statistics"""
    conn = get_conn()
    stats = {
        'total_spots': conn.execute("SELECT COUNT(*) FROM spots").fetchone()[0],
        'total_reports': conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0],
        'cities': conn.execute("SELECT DISTINCT city FROM spots WHERE city IS NOT NULL").fetchall(),
        'spot_types': conn.execute("SELECT spot_type, COUNT(*) FROM spots GROUP BY spot_type").fetchall(),
    }
    conn.close()
    return stats

def create_map(spots, user_location=None):
    """Create a Folium map with parking spots"""
    if user_location:
        map_center = [user_location[0], user_location[1]]
    elif spots:
        avg_lat = np.mean([spot['lat'] for spot in spots])
        avg_lon = np.mean([spot['lon'] for spot in spots])
        map_center = [avg_lat, avg_lon]
    else:
        map_center = [53.9045, 27.5615]  # Default to Minsk center
    
    m = folium.Map(location=map_center, zoom_start=13)
    
    # Add user location if provided
    if user_location:
        folium.Marker(
            location=user_location,
            popup="Your Location",
            icon=folium.Icon(color='blue', icon='user')
        ).add_to(m)
    
    # Add parking spots
    for spot in spots:
        color = {
            'free': 'green',
            'likely_full': 'orange',
            'full': 'red'
        }.get(spot['status'], 'gray')
        
        folium.Marker(
            location=[spot['lat'], spot['lon']],
            popup=f"""
            <b>{spot['name']}</b><br>
            Type: {spot['spot_type']}<br>
            Distance: {spot['distance_m']}m<br>
            Status: {spot['status']}<br>
            Reports: {spot['reports']}
            """,
            icon=folium.Icon(color=color)
        ).add_to(m)
    
    return m

# ── Main App Layout ────────────────────────────────────────────────────────────
def main():
    st.markdown('<div class="main-header">🅿️ Free Parking Finder</div>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose Page", [
        "🏠 Home",
        "🔍 Find Parking",
        "📊 Statistics",
        "🗺️ Map View",
        "⚙️ Settings"
    ])
    
    # Initialize session state
    if 'user_location' not in st.session_state:
        st.session_state.user_location = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = hash(st.session_state.get('session_id', 'anonymous')) % (2**31)
    
    if page == "🏠 Home":
        st.header("Welcome to Free Parking Finder")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            stats = get_db_stats()
            st.metric("Total Spots", stats['total_spots'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Reports", stats['total_reports'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Cities Covered", len(stats['cities']))
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.subheader("How it works")
        st.markdown("""
        1. **📍 Share your location** or enter an address
        2. **🔍 Find nearby parking spots** using our database
        3. **📊 View real-time status** from crowd-sourced reports
        4. **🗺️ See locations on map** with color-coded status
        5. **📝 Report back** when you arrive to help others
        """)
        
        # City selection
        st.subheader("Available Cities")
        available_cities = [city[0] for city in stats['cities'] if city[0]]
        if available_cities:
            st.write(f"Currently supported: {', '.join(available_cities)}")
        else:
            st.warning("No cities found. Please run the OSM data fetcher first.")
    
    elif page == "🔍 Find Parking":
        st.header("Find Parking Spots")
        
        # Location input
        st.subheader("Your Location")
        input_method = st.radio("How would you like to input your location?", [
            "📍 Use current location",
            "🎯 Enter coordinates",
            "🏢 Enter address"
        ])
        
        user_lat, user_lon = None, None
        
        if input_method == "📍 Use current location":
            if st.button("Get My Location"):
                st.info("Location feature requires browser location access")
                # In a real app, you'd use browser's geolocation API
        
        elif input_method == "🎯 Enter coordinates":
            col1, col2 = st.columns(2)
            with col1:
                user_lat = st.number_input("Latitude", value=53.9045, min_value=-90.0, max_value=90.0)
            with col2:
                user_lon = st.number_input("Longitude", value=27.5615, min_value=-180.0, max_value=180.0)
        
        elif input_method == "🏢 Enter address":
            address = st.text_input("Enter address", placeholder="e.g., Independence Ave 10, Minsk")
            if address and st.button("Search Address"):
                st.info("Address geocoding would be implemented here using Nominatim API")
        
        # Search button
        if user_lat and user_lon:
            if st.button("🔍 Find Parking Spots", type="primary"):
                with st.spinner("Searching for parking spots..."):
                    spots = find_nearest_spots(user_lat, user_lon, limit=MAX_RESULTS)
                    
                    if spots:
                        st.session_state.user_location = (user_lat, user_lon)
                        st.success(f"Found {len(spots)} parking spots within {SEARCH_RADIUS_KM} km")
                        
                        # Display results in a table
                        df = pd.DataFrame(spots)
                        
                        # Add status colors
                        def status_color(status):
                            colors = {'free': 'status-free', 'likely_full': 'status-likely-full', 'full': 'status-full'}
                            return f'<span class="{colors.get(status, '')}">{status}</span>'
                        
                        df_display = df[['name', 'spot_type', 'distance_m', 'capacity', 'status', 'reports']].copy()
                        df_display['status'] = df_display['status'].apply(status_color)
                        
                        st.subheader("Nearby Parking Spots")
                        st.markdown(df_display.to_html(escape=False, index=False), unsafe_allow_html=True)
                        
                        # Show map
                        st.subheader("Location Map")
                        map_obj = create_map(spots, (user_lat, user_lon))
                        st.components.v1.html(map_obj._repr_html_(), height=500)
                        
                        # Show spot details
                        st.subheader("Spot Details")
                        for i, spot in enumerate(spots):
                            with st.expander(f"{i+1}. {spot['name']} ({spot['distance_m']}m away)"):
                                st.markdown(f"""
                                **Type:** {spot['spot_type']}<br>
                                **Distance:** {spot['distance_m']}m<br>
                                **Capacity:** {spot['capacity'] or 'Unknown'}<br>
                                **Status:** {spot['status']}<br>
                                **Recent Reports:** {spot['reports']}<br>
                                **Certainty:** {spot['certainty']}
                                """)
                                
                                # Report buttons
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"✅ Still Free", key=f"free_{spot['id']}"):
                                        add_report(spot['id'], st.session_state.user_id, 'free')
                                        st.success("Reported as free! Thank you!")
                                with col2:
                                    if st.button(f"🔴 Full/Busy", key=f"full_{spot['id']}"):
                                        add_report(spot['id'], st.session_state.user_id, 'full')
                                        st.success("Reported as full! Thank you!")
                    else:
                        st.warning("No parking spots found in this area.")
    
    elif page == "📊 Statistics":
        st.header("Parking Statistics")
        
        stats = get_db_stats()
        
        # Basic stats
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Spots", stats['total_spots'])
        col2.metric("Total Reports", stats['total_reports'])
        col3.metric("Cities", len(stats['cities']))
        col4.metric("Spot Types", len(stats['spot_types']))
        
        # Spot types chart
        if stats['spot_types']:
            st.subheader("Parking Spots by Type")
            spot_type_df = pd.DataFrame(stats['spot_types'], columns=['spot_type', 'count'])
            if px is None:
                st.warning("Plotly is not installed; charts are unavailable.")
            else:
                fig = px.bar(spot_type_df, x='spot_type', y='count', title="Parking Spots by Type")
                st.plotly_chart(fig, use_container_width=True)
        
        # Recent reports
        st.subheader("Recent Reports")
        conn = get_conn()
        recent_reports = conn.execute("""
            SELECT s.name, r.status, r.reported_at
            FROM reports r
            JOIN spots s ON r.spot_id = s.id
            ORDER BY r.reported_at DESC
            LIMIT 10
        """).fetchall()
        conn.close()
        
        if recent_reports:
            reports_df = pd.DataFrame(recent_reports, columns=['Spot Name', 'Status', 'Reported At'])
            st.dataframe(reports_df)
        else:
            st.info("No recent reports found")
    
    elif page == "🗺️ Map View":
        st.header("Parking Map")
        
        # Show all spots
        conn = get_conn()
        all_spots = conn.execute("""
            SELECT id, name, lat, lon, spot_type
            FROM spots
            LIMIT 1000
        """).fetchall()
        conn.close()
        
        if all_spots:
            spots_list = []
            for spot in all_spots:
                status, report_count = get_occupancy(spot["id"])
                spots_list.append({
                    'name': spot["name"],
                    'lat': spot["lat"],
                    'lon': spot["lon"],
                    'spot_type': spot["spot_type"],
                    'status': status,
                    'reports': report_count,
                    'distance_m': 0  # Default for map view
                })
            
            # Create map
            map_obj = create_map(spots_list)
            st.components.v1.html(map_obj._repr_html_(), height=600)
            
            # Spot list
            st.subheader("All Parking Spots")
            spots_df = pd.DataFrame(spots_list)
            st.dataframe(spots_df[['name', 'spot_type', 'status', 'reports']])
        else:
            st.warning("No parking spots found. Please run the OSM data fetcher first.")
    
    elif page == "⚙️ Settings":
        st.header("Settings")
        
        st.subheader("Database Management")
        
        if st.button("🔄 Refresh Database"):
            st.info("Database refreshed")
        
        if st.button("📊 Recalculate Statistics"):
            st.info("Statistics recalculated")
        
        # Configuration
        st.subheader("Configuration")
        st.write("Search radius (km):")
        search_radius = st.slider("Search Radius", 0.5, 5.0, SEARCH_RADIUS_KM, 0.1)
        st.write(f"Maximum results: {MAX_RESULTS}")

if __name__ == "__main__":
    main()