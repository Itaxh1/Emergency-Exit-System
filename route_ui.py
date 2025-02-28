import streamlit as st
import requests
import folium
from streamlit_folium import folium_static

# Configure Streamlit App
st.set_page_config(page_title="🚗 Route Avoidance System", layout="wide")

# Title
st.title("🚗 Route Avoidance System")
st.markdown("**Find the safest and fastest route avoiding hazards like traffic, wildfires, and snow.**")

# User Inputs
start = st.text_input("📍 Enter Starting Location (e.g., Santa Cruz)", "Santa Cruz")
end = st.text_input("📍 Enter Destination (e.g., San Jose)", "San Jose")

if st.button("🚦 Find Safe Route"):
    api_url = f"http://127.0.0.1:8000/route?start={start}&end={end}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()

        if "error" in data:
            st.error(f"❌ {data['error']}")
        else:
            st.success(f"✅ **Total Distance:** {data['total_distance']}")

            # Display Hazard Warnings
            if data["warnings"]:
                for warning in data["warnings"]:
                    st.warning(f"⚠️ {warning}")

            # Display Route Steps
            st.subheader("🛣️ **Route Steps:**")
            route_steps = ""
            for i, step in enumerate(data["route"]):
                route_steps += f"<li style='margin-bottom: 8px; font-size: 16px;'><b>Step {i+1}:</b> {step}</li>"

            st.markdown(f"<ul>{route_steps}</ul>", unsafe_allow_html=True)

            # ---- Map 1: Main Route Map ----
            st.subheader("📍 **Main Route Map**")
            if "route_points" in data and len(data["route_points"]) > 1:
                route_map = folium.Map(location=data["route_points"][0], zoom_start=12)

                # Start Marker
                folium.Marker(
                    location=data["route_points"][0],
                    popup=f"<b>Start: {start}</b>",
                    icon=folium.Icon(color="green", icon="play")
                ).add_to(route_map)

                # End Marker
                folium.Marker(
                    location=data["route_points"][-1],
                    popup=f"<b>End: {end}</b>",
                    icon=folium.Icon(color="red", icon="flag")
                ).add_to(route_map)

                # Plot Route with Polyline
                folium.PolyLine(data["route_points"], color="blue", weight=5, opacity=0.7).add_to(route_map)

                # Add Step Markers (Handling Mismatched Lengths Safely)
                for i, coord in enumerate(data["route_points"]):
                    if i < len(data["route"]):  # Prevent index error
                        folium.Marker(
                            location=coord,
                            popup=folium.Popup(f"<b>Step {i+1}</b>: {data['route'][i]}", max_width=300),
                            icon=folium.Icon(color="blue", icon="info-sign")
                        ).add_to(route_map)

                # Render the Map
                folium_static(route_map)

            # ---- Map 2: Traffic Hotspots ----
            st.subheader("🚦 **Traffic Hotspots Map**")
            traffic_map = folium.Map(location=data["route_points"][0], zoom_start=12)

            # Simulated Traffic Hotspots (Manually Added)
            traffic_spots = [
                [37.7749, -122.4194],  # Example location
                [37.7849, -122.4294],  # Example location
                [37.7949, -122.4394]   # Example location
            ]

            for spot in traffic_spots:
                folium.Marker(
                    location=spot,
                    popup="🚦 High Traffic Area",
                    icon=folium.Icon(color="orange", icon="cloud")
                ).add_to(traffic_map)

            # Render Traffic Map
            folium_static(traffic_map)

            # ---- Map 3: Wildfire & Snow Hazard Zones ----
            st.subheader("🔥❄️ **Wildfire & Snow Hazard Zones**")
            hazard_map = folium.Map(location=data["route_points"][0], zoom_start=12)

            # Simulated Wildfire Locations
            wildfire_zones = [
                [37.7049, -122.4894],  # Example location
                [37.7849, -122.4094]   # Example location
            ]

            for fire in wildfire_zones:
                folium.Marker(
                    location=fire,
                    popup="🔥 Wildfire Area",
                    icon=folium.Icon(color="red", icon="fire")
                ).add_to(hazard_map)

            # Simulated Snow Zones
            snow_zones = [
                [38.8049, -120.4194],  # Example location
                [38.8949, -120.4294]   # Example location
            ]

            for snow in snow_zones:
                folium.Marker(
                    location=snow,
                    popup="❄️ Snow-Affected Area",
                    icon=folium.Icon(color="blue", icon="cloud")
                ).add_to(hazard_map)

            # Render Hazard Map
            folium_static(hazard_map)

    else:
        st.error("❌ Failed to fetch the route. Please check the API and try again.")
