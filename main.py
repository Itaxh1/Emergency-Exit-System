import streamlit as st
import pydeck as pdk
import random
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from geopy.distance import geodesic
import numpy as np
import pandas as pd

# Configuration and constants
class Config:
    # API keys
    GOOGLE_MAPS_API_KEY = "AIzaSyCcy95nDmWbTetdEYPLzgy9yv3yM7DiARM"
    OPENWEATHERMAP_API_KEY = "1d83c4f40e4a712ab9c57d0db16b1349"
    
    # Map settings
    DEFAULT_ZOOM = 5
    DEFAULT_PITCH = 45
    
    # Weather simulation settings
    SNOW_POINTS = 50
    FIRE_POINTS = 50
    RAIN_POINTS = 50

# API Service class for all external API calls
class APIService:
    @staticmethod
    def get_directions(start, end, alternatives=True):
        """Get directions from Google Maps API"""
        try:
            # URL for Google Maps Directions API
            url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&alternatives={str(alternatives).lower()}&departure_time=now&traffic_model=best_guess&key={Config.GOOGLE_MAPS_API_KEY}"
            
            # Send the GET request to the Directions API
            response = requests.get(url, timeout=10)
            
            # Parse the JSON response
            directions = response.json()

            # Check if the request was successful
            if directions["status"] == "OK":
                return directions
            else:
                st.error(f"Error fetching directions: {directions['status']}")
                return None
        except Exception as e:
            st.error(f"Failed to get directions: {str(e)}")
            return None
    
    @staticmethod
    def get_weather_data(lat, lon):
        """Fetch weather data"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={Config.OPENWEATHERMAP_API_KEY}&units=metric"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                st.error(f"Weather API error: {response.status_code}")
                return []
                
            data = response.json()
            
            hourly_data = []
            
            # Process the hourly weather data
            for entry in data.get('list', []):
                timestamp = entry.get('dt')
                temperature = entry.get('main', {}).get('temp')
                humidity = entry.get('main', {}).get('humidity')
                rain = entry.get('rain', {}).get('3h', 0)  # Rain in the last 3 hours
                snow = entry.get('snow', {}).get('3h', 0)  # Snow in the last 3 hours
                
                hourly_data.append({
                    'timestamp': timestamp,
                    'temperature': temperature,
                    'humidity': humidity,
                    'rain': rain,
                    'snow': snow
                })
            
            return hourly_data
        except Exception as e:
            st.error(f"Failed to get weather data: {str(e)}")
            return []

    @staticmethod
    def get_traffic_data(route_points):
        """Get traffic data for route points"""
        try:
            # Simulated traffic data for demonstration
            traffic_data = []
            for i, (lat, lon) in enumerate(route_points):
                severity = "High" if i % 3 == 0 else "Medium" if i % 3 == 1 else "Low"
                traffic_data.append({
                    "lat": lat, 
                    "lon": lon, 
                    "severity": severity,
                    "name": f"Traffic Point {i+1}"
                })
            return traffic_data
        except Exception as e:
            st.error(f"Failed to get traffic data: {str(e)}")
            return []

    @staticmethod
    def get_nearby_cities_and_exits(lat, lon, radius_km=50):
        """Get nearby cities and highway exits"""
        try:
            # Simulate nearby cities
            nearby_cities = []
            for i in range(5):
                city_lat = lat + ((-1)**i) * (i * 0.05)
                city_lon = lon + ((-1)**(i+1)) * (i * 0.05)
                distance = geodesic((lat, lon), (city_lat, city_lon)).km
                
                nearby_cities.append({
                    "city": f"City {i+1}",
                    "latitude": city_lat,
                    "longitude": city_lon,
                    "distance_km": distance
                })
            
            # Simulate highway exits
            highway_exits = []
            for i in range(3):
                exit_lat = lat + ((-1)**i) * (i * 0.03)
                exit_lon = lon + ((-1)**(i+1)) * (i * 0.04)
                
                highway_exits.append({
                    "exit_name": f"Exit {i+1}",
                    "exit_lat": exit_lat,
                    "exit_lon": exit_lon,
                    "distance_km": geodesic((lat, lon), (exit_lat, exit_lon)).km
                })
            
            return nearby_cities, highway_exits
        except Exception as e:
            st.error(f"Failed to get nearby locations: {str(e)}")
            return [], []

# Data processing class
class DataProcessor:
    @staticmethod
    def generate_snow_zones(start_lat, start_lon, end_lat, end_lon, num_zones=10):
        """Generate realistic snow zone clusters"""
        # Define snow zone clusters (more realistic than random points)
        snow_zones = []
        
        # Create clusters in northern areas (snow is more common in north)
        north_bias = 0.1  # Bias snow zones toward north
        
        # Calculate the route bounding box
        min_lat = min(start_lat, end_lat) - 0.5
        max_lat = max(start_lat, end_lat) + 0.5
        min_lon = min(start_lon, end_lon) - 0.5
        max_lon = max(start_lon, end_lon) + 0.5
        
        # Generate cluster centers
        for _ in range(num_zones):
            # Bias toward northern areas
            center_lat = random.uniform(min_lat + north_bias, max_lat + north_bias)
            center_lon = random.uniform(min_lon, max_lon)
            
            # Generate points around the center (cluster)
            cluster_size = random.randint(3, 8)
            for i in range(cluster_size):
                point_lat = center_lat + random.uniform(-0.2, 0.2)
                point_lon = center_lon + random.uniform(-0.2, 0.2)
                intensity = random.uniform(0.4, 1.0)
                
                snow_zones.append({
                    "lat": point_lat,
                    "lon": point_lon,
                    "intensity": intensity,
                    "radius": random.uniform(2000, 5000),
                    "name": f"Snow Zone {len(snow_zones) + 1}"
                })
                
        return snow_zones
    
    @staticmethod
    def generate_fire_zones(start_lat, start_lon, end_lat, end_lon, num_zones=8):
        """Generate realistic fire zone clusters"""
        fire_zones = []
        
        # Calculate the route bounding box
        min_lat = min(start_lat, end_lat) - 0.5
        max_lat = max(start_lat, end_lat) + 0.5
        min_lon = min(start_lon, end_lon) - 0.5
        max_lon = max(start_lon, end_lon) + 0.5
        
        # Generate cluster centers
        for _ in range(num_zones):
            center_lat = random.uniform(min_lat, max_lat)
            center_lon = random.uniform(min_lon, max_lon)
            
            # Generate points around the center (cluster)
            cluster_size = random.randint(4, 10)
            for i in range(cluster_size):
                point_lat = center_lat + random.uniform(-0.15, 0.15)
                point_lon = center_lon + random.uniform(-0.15, 0.15)
                intensity = random.uniform(0.5, 1.0)
                
                fire_zones.append({
                    "lat": point_lat,
                    "lon": point_lon,
                    "intensity": intensity,
                    "radius": random.uniform(1500, 4000),
                    "name": f"Fire Zone {len(fire_zones) + 1}"
                })
                
        return fire_zones
    
    @staticmethod
    def generate_rain_zones(start_lat, start_lon, end_lat, end_lon, num_zones=12):
        """Generate realistic rain zone clusters"""
        rain_zones = []
        
        # Calculate the route bounding box
        min_lat = min(start_lat, end_lat) - 0.5
        max_lat = max(start_lat, end_lat) + 0.5
        min_lon = min(start_lon, end_lon) - 0.5
        max_lon = max(start_lon, end_lon) + 0.5
        
        # Generate cluster centers
        for _ in range(num_zones):
            center_lat = random.uniform(min_lat, max_lat)
            center_lon = random.uniform(min_lon, max_lon)
            
            # Generate points around the center (cluster)
            cluster_size = random.randint(5, 12)
            for i in range(cluster_size):
                point_lat = center_lat + random.uniform(-0.25, 0.25)
                point_lon = center_lon + random.uniform(-0.25, 0.25)
                intensity = random.uniform(0.3, 0.9)
                
                rain_zones.append({
                    "lat": point_lat,
                    "lon": point_lon,
                    "intensity": intensity,
                    "radius": random.uniform(3000, 7000),
                    "name": f"Rain Zone {len(rain_zones) + 1}"
                })
                
        return rain_zones
    
    @staticmethod
    def apply_intensity_factor(zones, intensity_factor):
        """Apply intensity factor to weather zones"""
        for zone in zones:
            zone["adjusted_intensity"] = zone["intensity"] * intensity_factor
            # Also adjust the radius based on intensity
            zone["adjusted_radius"] = zone["radius"] * (0.5 + intensity_factor * 0.5)
        return zones
    
    @staticmethod
    def suggest_safe_exits(lat, lon, weather_data=None, traffic_data=None, 
                          snow_zones=None, fire_zones=None, rain_zones=None,
                          snow_factor=0.5, fire_factor=0.5, rain_factor=0.5):
        """Suggest safe exit places based on current location, weather, and traffic"""
        # Define possible exit directions (8 directions)
        directions = [
            (0.1, 0),    # North
            (0.07, 0.07), # Northeast
            (0, 0.1),    # East
            (-0.07, 0.07), # Southeast
            (-0.1, 0),   # South
            (-0.07, -0.07), # Southwest
            (0, -0.1),   # West
            (0.07, -0.07)  # Northwest
        ]
        
        exit_suggestions = []
        
        for i, (dlat, dlon) in enumerate(directions):
            exit_lat = lat + dlat
            exit_lon = lon + dlon
            
            # Calculate safety score (higher is better)
            safety_score = 100 - (i * 10 % 50)  # Varies from 50-100
            
            # Adjust for weather if available
            if weather_data and len(weather_data) > 0:
                # Reduce safety for high snow or rain
                snow = weather_data[0].get('snow', 0)
                rain = weather_data[0].get('rain', 0)
                safety_score -= (snow * 10 + rain * 5)
            
            # Adjust for traffic if available
            if traffic_data:
                # Find closest traffic point
                min_distance = float('inf')
                severity = "Low"
                
                for point in traffic_data:
                    dist = geodesic((lat, lon), (point['lat'], point['lon'])).km
                    if dist < min_distance:
                        min_distance = dist
                        severity = point['severity']
                
                # Adjust safety score based on traffic severity
                if severity == "High":
                    safety_score -= 30
                elif severity == "Medium":
                    safety_score -= 15
            
            # Adjust for snow zones
            snow_impact = 0
            if snow_zones:
                for zone in snow_zones:
                    dist = geodesic((exit_lat, exit_lon), (zone['lat'], zone['lon'])).km
                    if dist < 20:  # If within 20km
                        impact = 20 * zone.get('adjusted_intensity', zone['intensity']) * snow_factor
                        snow_impact += impact
                        safety_score -= impact
            
            # Adjust for fire zones
            fire_impact = 0
            if fire_zones:
                for zone in fire_zones:
                    dist = geodesic((exit_lat, exit_lon), (zone['lat'], zone['lon'])).km
                    if dist < 25:  # If within 25km
                        impact = 30 * zone.get('adjusted_intensity', zone['intensity']) * fire_factor
                        fire_impact += impact
                        safety_score -= impact
            
            # Adjust for rain zones
            rain_impact = 0
            if rain_zones:
                for zone in rain_zones:
                    dist = geodesic((exit_lat, exit_lon), (zone['lat'], zone['lon'])).km
                    if dist < 15:  # If within 15km
                        impact = 15 * zone.get('adjusted_intensity', zone['intensity']) * rain_factor
                        rain_impact += impact
                        safety_score -= impact
            
            # Ensure safety score is within bounds
            safety_score = max(0, min(100, safety_score))
            
            # Generate simulated emergency services data
            emergency_services = []
            for service_type in ["Hospital", "Police", "Fire Station"]:
                distance = random.uniform(2, 15)
                emergency_services.append({
                    "type": service_type,
                    "distance_km": distance,
                    "response_time_min": distance * 1.2  # Approximate response time
                })
            
            # Generate historical safety data
            historical_safety = {
                "past_incidents": random.randint(0, 20),
                "avg_response_time": random.uniform(5, 15),
                "evacuation_success_rate": random.uniform(70, 98)
            }
            
            # Generate road condition data
            road_conditions = {
                "road_quality": random.uniform(50, 100),
                "traffic_flow": random.uniform(40, 100),
                "visibility": random.uniform(60, 100) - (snow_impact * 0.5) - (rain_impact * 0.3)
            }
            
            exit_suggestions.append({
                "lat": exit_lat, 
                "lon": exit_lon,
                "direction": ["North", "Northeast", "East", "Southeast", "South", "Southwest", "West", "Northwest"][i],
                "safety_score": safety_score,
                "recommendation": "Highly Recommended" if safety_score > 80 else 
                                 "Recommended" if safety_score > 60 else
                                 "Use with Caution" if safety_score > 40 else "Not Recommended",
                "weather_impacts": {
                    "snow_impact": snow_impact,
                    "fire_impact": fire_impact,
                    "rain_impact": rain_impact
                },
                "emergency_services": emergency_services,
                "historical_safety": historical_safety,
                "road_conditions": road_conditions,
                "terrain_difficulty": random.uniform(10, 50),
                "cell_coverage": random.uniform(60, 100)
            })
        
        # Sort by safety score (highest first)
        exit_suggestions.sort(key=lambda x: x['safety_score'], reverse=True)
        
        return exit_suggestions[:3]  # Return top 3 safest exits

    @staticmethod
    def calculate_emergency_risk(weather_data, traffic_data, snow_zones=None, fire_zones=None, rain_zones=None,
                               snow_factor=0.5, fire_factor=0.5, rain_factor=0.5):
        """Calculate overall emergency risk based on weather and traffic"""
        # Initialize risk factors
        snow_risk = 0
        rain_risk = 0
        fire_risk = 0
        traffic_risk = 0
        
        # Calculate weather risks
        if weather_data and len(weather_data) > 0:
            snow_values = [entry.get('snow', 0) for entry in weather_data]
            rain_values = [entry.get('rain', 0) for entry in weather_data]
            
            max_snow = max(snow_values) if snow_values else 0
            max_rain = max(rain_values) if rain_values else 0
            
            # Scale to 0-100
            snow_risk = min(100, max_snow * 20)
            rain_risk = min(100, max_rain * 10)
        
        # Calculate traffic risk
        if traffic_data:
            severity_counts = {"High": 0, "Medium": 0, "Low": 0}
            for point in traffic_data:
                severity_counts[point.get('severity', "Low")] += 1
            
            # Weight by severity
            traffic_risk = (severity_counts["High"] * 10 + severity_counts["Medium"] * 5) / max(1, len(traffic_data)) * 10
            traffic_risk = min(100, traffic_risk)
        
        # Calculate snow risk from snow zones
        if snow_zones:
            snow_intensities = [zone.get('adjusted_intensity', zone['intensity']) for zone in snow_zones]
            avg_snow_intensity = sum(snow_intensities) / len(snow_intensities) if snow_intensities else 0
            snow_risk = max(snow_risk, avg_snow_intensity * 100 * snow_factor)
        
        # Calculate fire risk from fire zones
        if fire_zones:
            fire_intensities = [zone.get('adjusted_intensity', zone['intensity']) for zone in fire_zones]
            avg_fire_intensity = sum(fire_intensities) / len(fire_intensities) if fire_intensities else 0
            fire_risk = avg_fire_intensity * 100 * fire_factor
        
        # Calculate rain risk from rain zones
        if rain_zones:
            rain_intensities = [zone.get('adjusted_intensity', zone['intensity']) for zone in rain_zones]
            avg_rain_intensity = sum(rain_intensities) / len(rain_intensities) if rain_intensities else 0
            rain_risk = max(rain_risk, avg_rain_intensity * 100 * rain_factor)
        
        # Calculate overall risk (weighted average)
        overall_risk = (snow_risk * 0.2 + rain_risk * 0.2 + fire_risk * 0.3 + traffic_risk * 0.3)
        
        return {
            "overall_risk": overall_risk,
            "snow_risk": snow_risk,
            "rain_risk": rain_risk,
            "fire_risk": fire_risk,
            "traffic_risk": traffic_risk,
            "risk_level": "High" if overall_risk > 70 else "Medium" if overall_risk > 40 else "Low"
        }
    
    @staticmethod
    def select_best_route(routes, snow_zones, fire_zones, rain_zones, 
                         snow_factor, fire_factor, rain_factor):
        """Select the best route based on weather conditions"""
        route_scores = []
        
        for idx, route in enumerate(routes):
            # Get route points
            route_points = [(step["start_location"]["lat"], step["start_location"]["lng"]) 
                           for step in route["legs"][0]["steps"]]
            route_points.append((route["legs"][0]["end_location"]["lat"], 
                               route["legs"][0]["end_location"]["lng"]))
            
            # Calculate risk score for this route
            risk_score = 0
            
            # Check snow zones near route
            for snow_zone in snow_zones:
                for route_lat, route_lon in route_points:
                    dist = geodesic((snow_zone['lat'], snow_zone['lon']), (route_lat, route_lon)).km
                    if dist < 20:  # If snow zone is within 20km of any route point
                        risk_score += 2 * snow_zone.get('adjusted_intensity', snow_zone['intensity']) * snow_factor
            
            # Check fire zones near route
            for fire_zone in fire_zones:
                for route_lat, route_lon in route_points:
                    dist = geodesic((fire_zone['lat'], fire_zone['lon']), (route_lat, route_lon)).km
                    if dist < 25:  # If fire zone is within 25km of any route point
                        risk_score += 3 * fire_zone.get('adjusted_intensity', fire_zone['intensity']) * fire_factor
            
            # Check rain zones near route
            for rain_zone in rain_zones:
                for route_lat, route_lon in route_points:
                    dist = geodesic((rain_zone['lat'], rain_zone['lon']), (route_lat, route_lon)).km
                    if dist < 15:  # If rain zone is within 15km of any route point
                        risk_score += 1.5 * rain_zone.get('adjusted_intensity', rain_zone['intensity']) * rain_factor
            
            # Add base score from route duration
            duration_seconds = route["legs"][0]["duration"]["value"]
            duration_score = duration_seconds / 60  # 1 point per minute
            
            # Total score (lower is better)
            total_score = risk_score + duration_score
            
            route_scores.append({
                "route_index": idx,
                "risk_score": risk_score,
                "duration_score": duration_score,
                "total_score": total_score
            })
        
        # Sort routes by total score (lower is better)
        route_scores.sort(key=lambda x: x["total_score"])
        
        # Return the sorted route indices
        return [score["route_index"] for score in route_scores]

# UI Components class
class UI:
    @staticmethod
    def render_header():
        """Render the application header"""
        st.set_page_config(page_title="🚗 Emergency Route System", layout="wide")
        
        # Header with logo and title
        col1, col2 = st.columns([1, 5])
        with col1:
            st.image("https://avatars.githubusercontent.com/u/26956905?v=4", width=80)
        with col2:
            st.title("🚦 Emergency Route System")
            st.markdown("**Find the safest and fastest route with live traffic and weather updates.**")
    
    @staticmethod
    def render_input_section():
        """Render the input section"""
        col1, col2, col3 = st.columns([3, 3, 2])
        
        with col1:
            start = st.text_input("Starting Location", "Los Angeles")
        
        with col2:
            end = st.text_input("Destination", "San Francisco")
        
        with col3:
            date = st.date_input("Select Date", datetime.today())
        
        return start, end, date
    
    @staticmethod
    def render_weather_intensity_sliders():
        """Render sliders for weather intensity"""
        st.sidebar.title("⚙️ Weather Intensity Controls")
        
        snow_factor = st.sidebar.slider("❄️ Snow Intensity", 0.0, 1.0, 0.5, 0.01, 
                                   help="Adjust the intensity of snow conditions")
        
        fire_factor = st.sidebar.slider("🔥 Fire Risk Intensity", 0.0, 1.0, 0.5, 0.01,
                                   help="Adjust the intensity of fire risk conditions")
        
        rain_factor = st.sidebar.slider("🌧️ Rain Intensity", 0.0, 1.0, 0.5, 0.01,
                                   help="Adjust the intensity of rain conditions")
        
        # Add an apply button to update the map
        apply_changes = st.sidebar.button("Apply Changes", use_container_width=True)
        
        return snow_factor, fire_factor, rain_factor, apply_changes
    
    @staticmethod
    def render_route_map(routes, city_markers, traffic_hotspots, 
                        snow_zones, fire_zones, rain_zones,
                        recommended_route_index=0):
        """Render the route map with markers"""
        all_layers = []
        all_route_coords = []
        
        # Define route colors - make them more distinct
        route_colors = [
            [0, 255, 0],     # Green for recommended route
            [255, 0, 0],     # Red for route 2
            [0, 0, 255],     # Blue for route 3
            [255, 255, 0],   # Yellow for route 4 (if needed)
            [255, 0, 255]    # Magenta for route 5 (if needed)
        ]
        
        # Process each route
        for idx, route in enumerate(routes):
            # Extract route points
            route_points = []
            for step in route["legs"][0]["steps"]:
                route_points.append([step["start_location"]["lat"], step["start_location"]["lng"]])
                
                # Add intermediate points if available for smoother routes
                if "path" in step:
                    for point in step["path"]:
                        route_points.append([point["lat"], point["lng"]])
            
            # Add the final endpoint
            route_points.append([route["legs"][0]["end_location"]["lat"], 
                               route["legs"][0]["end_location"]["lng"]])
            
            # Add route coordinates to center the map correctly
            all_route_coords.extend(route_points)
            
            # Determine if this is the recommended route
            is_recommended = (idx == recommended_route_index)
            
            # Create route line layer with traffic data
            route_layer = pdk.Layer(
                "PathLayer",
                data=[{
                    "path": [[point[1], point[0]] for point in route_points],
                    "name": f"Route {idx + 1}" + (" (Recommended)" if is_recommended else ""),
                    "color": route_colors[0] if is_recommended else route_colors[idx % len(route_colors)]
                }],
                get_path="path",
                get_color="color",
                get_width=15 if is_recommended else 10,
                pickable=True,
                auto_highlight=True,
                width_scale=20,
                width_min_pixels=2,
                joint_rounded=True,
                cap_rounded=True,
            )
            
            # Adding route markers with route numbers
            # Start marker
            start_marker = pdk.Layer(
                "ScatterplotLayer",
                data=[{
                    "position": [route_points[0][1], route_points[0][0]],
                    "color": route_colors[0] if is_recommended else route_colors[idx % len(route_colors)],
                    "name": f"Route {idx + 1} Start" + (" (Recommended)" if is_recommended else "")
                }],
                get_position="position",
                get_color="color",
                get_radius=2000,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=6,
                line_width_min_pixels=1,
            )
            
            # End marker
            end_marker = pdk.Layer(
                "ScatterplotLayer",
                data=[{
                    "position": [route_points[-1][1], route_points[-1][0]],
                    "color": route_colors[0] if is_recommended else route_colors[idx % len(route_colors)],
                    "name": f"Route {idx + 1} End" + (" (Recommended)" if is_recommended else "")
                }],
                get_position="position",
                get_color="color",
                get_radius=2000,
                pickable=True,
                opacity=0.8,
                stroked=True,
                filled=True,
                radius_scale=6,
                line_width_min_pixels=1,
            )
            
            # Route label
            route_label = pdk.Layer(
                "TextLayer",
                data=[{
                    "position": [route_points[len(route_points)//2][1], route_points[len(route_points)//2][0]],
                    "text": f"Route {idx + 1}" + (" (Recommended)" if is_recommended else "")
                }],
                get_position="position",
                get_text="text",
                get_size=18,
                get_color=[255, 255, 255],
                get_angle=0,
                get_text_anchor="middle",
                get_alignment_baseline="center",
                get_pixel_offset=[0, -10],
                background_color=[0, 0, 0, 150],
                background_padding=[5, 3],
            )
            
            all_layers.extend([route_layer, start_marker, end_marker, route_label])
        
        # # Add city markers
        # city_layer = pdk.Layer(
        #     "ScatterplotLayer",
        #     data=city_markers,
        #     get_position=["lon", "lat"],
        #     get_color=[0, 255, 0],  # Green for city markers
        #     get_radius=5000,
        #     pickable=True,
        # )
        
        # Add traffic hotspots
        for point in traffic_hotspots:
            if point["severity"] == "High":
                point["color"] = [255, 0, 0]  # Red
            elif point["severity"] == "Medium":
                point["color"] = [255, 165, 0]  # Orange
            else:
                point["color"] = [255, 255, 0]  # Yellow
        
        traffic_layer = pdk.Layer(
            "ScatterplotLayer",
            data=traffic_hotspots,
            get_position=["lon", "lat"],
            get_color="color",
            get_radius=3000,
            pickable=True,
        )
        
        # Add snow zones
        snow_layer = pdk.Layer(
            "ScatterplotLayer",
            data=snow_zones,
            get_position=["lon", "lat"],
            get_color=[[255, 255, 255, int(255 * zone.get('adjusted_intensity', zone['intensity']))] for zone in snow_zones],
            get_radius="adjusted_radius" if "adjusted_radius" in snow_zones[0] else "radius",
            pickable=True,
            opacity=0.7,
        )
        
        # Add fire zones
        fire_layer = pdk.Layer(
            "ScatterplotLayer",
            data=fire_zones,
            get_position=["lon", "lat"],
            get_color=[[255, 69, 0, int(255 * zone.get('adjusted_intensity', zone['intensity']))] for zone in fire_zones],
            get_radius="adjusted_radius" if "adjusted_radius" in fire_zones[0] else "radius",
            pickable=True,
            opacity=0.7,
        )
        
        # Add rain zones
        rain_layer = pdk.Layer(
            "ScatterplotLayer",
            data=rain_zones,
            get_position=["lon", "lat"],
            get_color=[[30, 144, 255, int(255 * zone.get('adjusted_intensity', zone['intensity']))] for zone in rain_zones],
            get_radius="adjusted_radius" if "adjusted_radius" in rain_zones[0] else "radius",
            pickable=True,
            opacity=0.6,
        )
        
        # Define the center of the map from the collected route coordinates
        center_lat = sum([coords[0] for coords in all_route_coords]) / len(all_route_coords) if all_route_coords else 37.7749
        center_lon = sum([coords[1] for coords in all_route_coords]) / len(all_route_coords) if all_route_coords else -122.4194
        
        # Create the map
        st.pydeck_chart(pdk.Deck(
            layers=[snow_layer, fire_layer, rain_layer, traffic_layer, *all_layers],
            initial_view_state=pdk.ViewState(
                latitude=center_lat,
                longitude=center_lon,
                zoom=Config.DEFAULT_ZOOM,
                pitch=Config.DEFAULT_PITCH
            ),
            tooltip={"text": "{name}\nSeverity: {severity}\nIntensity: {intensity}"},
            map_style="mapbox://styles/mapbox/dark-v10",
        ))
        
        # Add a legend for routes
        st.subheader("Route Legend")
        cols = st.columns(len(routes))
        for idx, route in enumerate(routes):
            with cols[idx]:
                is_recommended = (idx == recommended_route_index)
                color = "green" if is_recommended else ["red", "blue", "yellow", "magenta"][idx % 4]
                st.markdown(
                    f"<div style='display: flex; align-items: center;'>"
                    f"<div style='width: 20px; height: 10px; background-color: {color}; margin-right: 10px;'></div>"
                    f"<div><strong>Route {idx + 1}</strong>{' (Recommended)' if is_recommended else ''}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
                st.markdown(f"**Distance:** {route['legs'][0]['distance']['text']}")
                st.markdown(f"**Duration:** {route['legs'][0]['duration']['text']}")
    
    @staticmethod
    def render_weather_graphs(hourly_weather_data):
        """Render weather graphs"""
        # Create tabs for different weather data
        tab1, tab2, tab3 = st.tabs(["🌧️ Rainfall", "❄️ Snowfall", "🌡️ Temperature"])
        
        with tab1:
            UI._plot_hourly_graph(hourly_weather_data, 'rain', 'Rainfall (mm)', 'blue')
        
        with tab2:
            UI._plot_hourly_graph(hourly_weather_data, 'snow', 'Snowfall (mm)', 'lightblue')
        
        with tab3:
            UI._plot_hourly_graph(hourly_weather_data, 'temperature', 'Temperature (°C)', 'orange')
    
    @staticmethod
    def _plot_hourly_graph(hourly_data, metric, title, color):
        """Helper method to plot hourly graphs"""
        if not hourly_data or not hourly_data[0]:
            st.info(f"No {metric} data available")
            return
            
        hourly_vals = [data.get(metric, 0) for data in hourly_data]
        times = [datetime.utcfromtimestamp(data.get('timestamp', 0)).strftime('%H:%M') 
                for data in hourly_data]
        
        # Create interactive plotly bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=times,
            y=hourly_vals,
            marker=dict(color=color),
            name=title
        ))

        fig.update_layout(
            title=f"Hourly {title}",
            xaxis_title="Time",
            yaxis_title=title,
            template="plotly_white"
        )

        st.plotly_chart(fig)
    
    @staticmethod
    def render_safe_exits(safe_exits, snow_zones, fire_zones, rain_zones, 
                         snow_factor, fire_factor, rain_factor):
        """Render safe exit points with detailed analytics"""
        st.subheader("🚪 Recommended Safe Exit Points")
        
        # Create columns for each exit point
        cols = st.columns(len(safe_exits))
        
        for i, exit_point in enumerate(safe_exits):
            with cols[i]:
                st.markdown(f"### Exit {i+1}: {exit_point['direction']}")
                st.markdown(f"**Safety Score:** {exit_point['safety_score']:.1f}/100")
                st.markdown(f"**Recommendation:** {exit_point['recommendation']}")
                st.markdown(f"**Coordinates:** {exit_point['lat']:.4f}, {exit_point['lon']:.4f}")
                
                # Add a small map for each exit
                st.pydeck_chart(pdk.Deck(
                    layers=[
                        pdk.Layer(
                            "ScatterplotLayer",
                            data=[{"position": [exit_point['lon'], exit_point['lat']], "color": [0, 255, 0]}],
                            get_position="position",
                            get_color="color",
                            get_radius=300,
                        )
                    ],
                    initial_view_state=pdk.ViewState(
                        latitude=exit_point['lat'],
                        longitude=exit_point['lon'],
                        zoom=10,
                    ),
                    map_style="mapbox://styles/mapbox/streets-v11",
                ))
                
                # Add a button to view detailed analytics for this exit
                if st.button(f"View Detailed Analytics for Exit {i+1}", key=f"exit_{i}"):
                    st.session_state.selected_exit = i
        
        # If an exit is selected, show detailed analytics
        if hasattr(st.session_state, 'selected_exit'):
            selected_exit = safe_exits[st.session_state.selected_exit]
            
            # Generate analytics data for the selected exit
            analytics_data = DataProcessor.generate_exit_analytics(
                selected_exit, snow_zones, fire_zones, rain_zones,
                snow_factor, fire_factor, rain_factor
            )
            
            # Render the analytics
            UI.render_exit_analytics(selected_exit, analytics_data)
    
    @staticmethod
    def render_exit_analytics(exit_point, analytics_data):
        """Render detailed analytics for an exit point"""
        st.subheader(f"📊 Detailed Analytics for Exit: {exit_point['direction']}")
        
        # Create tabs for different analytics
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🔍 Safety Analysis", 
            "📈 Time Forecast", 
            "🏥 Resources", 
            "🔄 Comparative Analysis",
            "📜 Historical Data"
        ])
        
        with tab1:
            # Safety score gauge
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=exit_point['safety_score'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Safety Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkgreen"},
                    'steps': [
                        {'range': [0, 40], 'color': "red"},
                        {'range': [40, 60], 'color': "orange"},
                        {'range': [60, 80], 'color': "yellow"},
                        {'range': [80, 100], 'color': "green"},
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': exit_point['safety_score']
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig)
            
            # Weather impact breakdown
            st.subheader("Weather Impact Breakdown")
            impact_data = {
                'Factor': ['Snow Impact', 'Fire Impact', 'Rain Impact'],
                'Impact Score': [
                    exit_point['weather_impacts']['snow_impact'],
                    exit_point['weather_impacts']['fire_impact'],
                    exit_point['weather_impacts']['rain_impact']
                ]
            }
            
            fig = px.bar(impact_data, x='Factor', y='Impact Score', 
                        color='Impact Score', color_continuous_scale='Reds')
            st.plotly_chart(fig)
            
            # Nearest hazards
            st.subheader("Distance to Nearest Hazards")
            hazard_data = pd.DataFrame({
                'Hazard Type': ['Snow Zone', 'Fire Zone', 'Rain Zone'],
                'Distance (km)': [
                    analytics_data['nearest_hazards']['snow_distance_km'] or 100,
                    analytics_data['nearest_hazards']['fire_distance_km'] or 100,
                    analytics_data['nearest_hazards']['rain_distance_km'] or 100
                ]
            })
            
            fig = px.bar(hazard_data, x='Hazard Type', y='Distance (km)', 
                        color='Distance (km)', color_continuous_scale='Greens')
            st.plotly_chart(fig)
            
            # Terrain analysis
            st.subheader("Terrain Analysis")
            terrain_data = pd.DataFrame({
                'Factor': ['Elevation (m)', 'Slope (°)', 'Vegetation Density (%)', 'Water Bodies'],
                'Value': [
                    analytics_data['terrain_analysis']['elevation'],
                    analytics_data['terrain_analysis']['slope'],
                    analytics_data['terrain_analysis']['vegetation_density'],
                    analytics_data['terrain_analysis']['water_bodies']
                ]
            })
            
            fig = px.bar(terrain_data, x='Factor', y='Value', color='Value')
            st.plotly_chart(fig)
        
        with tab2:
            # Safety forecast over time
            st.subheader("24-Hour Safety Forecast")
            forecast_df = pd.DataFrame(analytics_data['safety_forecast'])
            
            fig = px.line(forecast_df, x='hour', y='safety_score', 
                         title='Projected Safety Score Over Next 24 Hours')
            fig.update_layout(xaxis_title="Hour", yaxis_title="Safety Score")
            st.plotly_chart(fig)
            
            # Weather impact forecast
            st.subheader("Weather Impact Forecast")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=forecast_df['hour'], y=forecast_df['snow_impact'], 
                                    mode='lines', name='Snow Impact', line=dict(color='lightblue')))
            fig.add_trace(go.Scatter(x=forecast_df['hour'], y=forecast_df['fire_impact'], 
                                    mode='lines', name='Fire Impact', line=dict(color='orange')))
            fig.add_trace(go.Scatter(x=forecast_df['hour'], y=forecast_df['rain_impact'], 
                                    mode='lines', name='Rain Impact', line=dict(color='blue')))
            
            fig.update_layout(title='Weather Impact Forecast',
                             xaxis_title='Hour',
                             yaxis_title='Impact Score')
            st.plotly_chart(fig)
            
            # Best time to evacuate
            best_hour = forecast_df.loc[forecast_df['safety_score'].idxmax()]['hour']
            worst_hour = forecast_df.loc[forecast_df['safety_score'].idxmin()]['hour']
            
            st.info(f"🕒 **Best time to evacuate:** Hour {int(best_hour)}:00 (Safety Score: {forecast_df['safety_score'].max():.1f})")
            st.warning(f"⚠️ **Avoid evacuating at:** Hour {int(worst_hour)}:00 (Safety Score: {forecast_df['safety_score'].min():.1f})")
        
        with tab3:
            # Emergency services
            st.subheader("🚑 Emergency Services")
            services_df = pd.DataFrame(exit_point['emergency_services'])
            
            fig = px.bar(services_df, x='type', y='distance_km', 
                        title='Distance to Emergency Services',
                        labels={'type': 'Service Type', 'distance_km': 'Distance (km)'})
            st.plotly_chart(fig)
            
            # Response time
            fig = px.bar(services_df, x='type', y='response_time_min', 
                        title='Estimated Response Time',
                        labels={'type': 'Service Type', 'response_time_min': 'Response Time (min)'})
            st.plotly_chart(fig)
            
            # Resource availability
            st.subheader("📦 Resource Availability")
            resources_df = pd.DataFrame(analytics_data['resource_availability'])
            
            fig = px.bar(resources_df, x='name', y='availability', 
                        title='Resource Availability (%)',
                        color='availability', color_continuous_scale='Greens')
            st.plotly_chart(fig)
            
            # Road conditions
            st.subheader("🛣️ Road Conditions")
            road_data = pd.DataFrame({
                'Factor': ['Road Quality', 'Traffic Flow', 'Visibility'],
                'Score': [
                    exit_point['road_conditions']['road_quality'],
                    exit_point['road_conditions']['traffic_flow'],
                    exit_point['road_conditions']['visibility']
                ]
            })
            
            fig = px.bar(road_data, x='Factor', y='Score', 
                        title='Road Condition Factors',
                        color='Score', color_continuous_scale='Blues')
            st.plotly_chart(fig)
        
        with tab4:
            # Comparative metrics
            st.subheader("🔄 Comparative Analysis")
            comparative_df = pd.DataFrame({
                'Metric': list(analytics_data['comparative_metrics'].keys()),
                'Score': list(analytics_data['comparative_metrics'].values())
            })
            
            fig = px.bar(comparative_df, x='Metric', y='Score', 
                        title='Comparative Metrics (Higher is Better)',
                        color='Score', color_continuous_scale='Viridis')
            st.plotly_chart(fig)
            
            # Radar chart for overall comparison
            categories = list(analytics_data['comparative_metrics'].keys())
            values = list(analytics_data['comparative_metrics'].values())
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='This Exit'
            ))
            
            # Add average values for comparison
            avg_values = [random.uniform(40, 70) for _ in categories]
            fig.add_trace(go.Scatterpolar(
                r=avg_values,
                theta=categories,
                fill='toself',
                name='Average Exit'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title="Exit Performance vs. Average"
            )
            st.plotly_chart(fig)
            
            # Cell coverage and communication
            st.subheader("📱 Communication Reliability")
            comm_data = {
                'Factor': ['Cell Coverage', 'Emergency Radio', 'Internet Access'],
                'Score': [exit_point['cell_coverage'], 
                         random.uniform(50, 90), 
                         random.uniform(40, 85)]
            }
            
            fig = px.bar(comm_data, x='Factor', y='Score', 
                        title='Communication Reliability Scores',
                        color='Score', color_continuous_scale='Purples')
            st.plotly_chart(fig)
        
        with tab5:
            # Historical evacuation data
            st.subheader("📜 Historical Evacuation Data")
            hist_df = pd.DataFrame(analytics_data['historical_evacuation'])
            
            fig = px.line(hist_df, x='year', y='success_rate', 
                         title='Historical Evacuation Success Rate (%)')
            st.plotly_chart(fig)
            
            fig = px.line(hist_df, x='year', y='avg_evacuation_time', 
                         title='Historical Average Evacuation Time (minutes)')
            st.plotly_chart(fig)
            
            fig = px.bar(hist_df, x='year', y='incidents', 
                        title='Number of Evacuation Incidents per Year')
            st.plotly_chart(fig)
            
            # Historical safety score
            st.subheader("🏆 Safety Rating History")
            years = list(range(2015, 2025))
            ratings = [random.uniform(60, 95) for _ in years]
            
            fig = px.line(x=years, y=ratings, 
                         title='Historical Safety Rating for This Exit',
                         labels={'x': 'Year', 'y': 'Safety Rating'})
            st.plotly_chart(fig)
    
    @staticmethod
    def render_risk_assessment(risk_data):
        """Render risk assessment dashboard"""
        st.subheader("⚠️ Emergency Risk Assessment")
        
        # Create gauge chart for overall risk
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=risk_data["overall_risk"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Risk Level"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "darkred"},
                'steps': [
                    {'range': [0, 30], 'color': "green"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "red"},
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': risk_data["overall_risk"]
                }
            }
        ))
        
        fig.update_layout(height=250)
        st.plotly_chart(fig)
        
        # Display individual risk factors
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Snow Risk", f"{risk_data['snow_risk']:.1f}%", 
                     delta="High" if risk_data['snow_risk'] > 70 else "Medium" if risk_data['snow_risk'] > 30 else "Low")
        
        with col2:
            st.metric("Rain Risk", f"{risk_data['rain_risk']:.1f}%", 
                     delta="High" if risk_data['rain_risk'] > 70 else "Medium" if risk_data['rain_risk'] > 30 else "Low")
        
        with col3:
            st.metric("Fire Risk", f"{risk_data['fire_risk']:.1f}%", 
                     delta="High" if risk_data['fire_risk'] > 70 else "Medium" if risk_data['fire_risk'] > 30 else "Low")
        
        with col4:
            st.metric("Traffic Risk", f"{risk_data['traffic_risk']:.1f}%", 
                     delta="High" if risk_data['traffic_risk'] > 70 else "Medium" if risk_data['traffic_risk'] > 30 else "Low")
        
        # Emergency recommendations based on risk level
        st.subheader("🚨 Emergency Recommendations")
        
        if risk_data["risk_level"] == "High":
            st.error("""
            **HIGH RISK DETECTED**
            - Consider postponing your journey if possible
            - Stay updated with local emergency services
            - Ensure your vehicle is fully prepared for emergency conditions
            - Keep emergency supplies and contact information readily available
            """)
        elif risk_data["risk_level"] == "Medium":
            st.warning("""
            **MEDIUM RISK DETECTED**
            - Proceed with caution
            - Monitor weather and traffic conditions regularly
            - Have alternative routes planned
            - Keep emergency contacts accessible
            """)
        else:
            st.success("""
            **LOW RISK DETECTED**
            - Conditions appear favorable for travel
            - Still recommended to check for updates before departure
            - Follow normal safety precautions
            """)
    
    @staticmethod
    def render_weather_points_legend():
        """Render a legend for weather points"""
        st.subheader("🗺️ Map Legend")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### ❄️ Snow Areas")
            st.markdown("White circles indicate snow-affected areas. Larger and more opaque circles indicate higher snow intensity.")
        
        with col2:
            st.markdown("### 🔥 Fire Risk Areas")
            st.markdown("Orange-red circles indicate fire risk areas. Larger and more opaque circles indicate higher fire risk.")
        
        with col3:
            st.markdown("### 🌧️ Rain Areas")
            st.markdown("Blue circles indicate rain-affected areas. Larger and more opaque circles indicate higher rainfall.")

# Main application class
class EmergencyRouteApp:
    def __init__(self):
        """Initialize the application"""
        # Initialize session state variables if they don't exist
        if "routes" not in st.session_state:
            st.session_state.routes = None
        if "weather_data" not in st.session_state:
            st.session_state.weather_data = None
        if "traffic_data" not in st.session_state:
            st.session_state.traffic_data = None
        if "safe_exits" not in st.session_state:
            st.session_state.safe_exits = None
        if "risk_assessment" not in st.session_state:
            st.session_state.risk_assessment = None
        if "snow_zones" not in st.session_state:
            st.session_state.snow_zones = None
        if "fire_zones" not in st.session_state:
            st.session_state.fire_zones = None
        if "rain_zones" not in st.session_state:
            st.session_state.rain_zones = None
        if "recommended_route_index" not in st.session_state:
            st.session_state.recommended_route_index = 0
        if "snow_factor" not in st.session_state:
            st.session_state.snow_factor = 0.5
        if "fire_factor" not in st.session_state:
            st.session_state.fire_factor = 0.5
        if "rain_factor" not in st.session_state:
            st.session_state.rain_factor = 0.5
    
    def run(self):
        """Run the application"""
        # Render header
        UI.render_header()
        
        # Render input section
        start, end, date = UI.render_input_section()
        
        # Render weather intensity sliders in sidebar
        snow_factor, fire_factor, rain_factor, apply_changes = UI.render_weather_intensity_sliders()
        
        # Update session state with slider values
        st.session_state.snow_factor = snow_factor
        st.session_state.fire_factor = fire_factor
        st.session_state.rain_factor = rain_factor
        
        # Add action buttons
        col1, col2 = st.columns(2)
        
        with col1:
            get_routes = st.button("🚦 Get Live Routes", use_container_width=True)
        
        with col2:
            find_exits = st.button("🏃 Find Safe Exit Points", use_container_width=True, 
                                  disabled=st.session_state.routes is None)
        
        # Process route request
        if get_routes:
            with st.spinner("Fetching routes..."):
                directions = APIService.get_directions(start, end, alternatives=True)
                
                if directions and directions.get("routes"):
                    st.session_state.routes = directions["routes"][:3]
                    st.success(f"✅ Found {len(st.session_state.routes)} routes!")
                    
                    # Get the first route's start and end points
                    start_lat = st.session_state.routes[0]["legs"][0]["start_location"]["lat"]
                    start_lon = st.session_state.routes[0]["legs"][0]["start_location"]["lng"]
                    end_lat = st.session_state.routes[0]["legs"][0]["end_location"]["lat"]
                    end_lon = st.session_state.routes[0]["legs"][0]["end_location"]["lng"]
                    
                    # Get weather data
                    st.session_state.weather_data = APIService.get_weather_data(start_lat, start_lon)
                    
                    # Get traffic data for the route
                    route_points = [(step["start_location"]["lat"], step["start_location"]["lng"]) 
                                   for step in st.session_state.routes[0]["legs"][0]["steps"]]
                    st.session_state.traffic_data = APIService.get_traffic_data(route_points)
                    
                    # Generate snow, fire, and rain zones
                    st.session_state.snow_zones = DataProcessor.generate_snow_zones(
                        start_lat, start_lon, end_lat, end_lon)
                    
                    st.session_state.fire_zones = DataProcessor.generate_fire_zones(
                        start_lat, start_lon, end_lat, end_lon)
                    
                    st.session_state.rain_zones = DataProcessor.generate_rain_zones(
                        start_lat, start_lon, end_lat, end_lon)
                    
                    # Apply intensity factors
                    st.session_state.snow_zones = DataProcessor.apply_intensity_factor(
                        st.session_state.snow_zones, st.session_state.snow_factor)
                    
                    st.session_state.fire_zones = DataProcessor.apply_intensity_factor(
                        st.session_state.fire_zones, st.session_state.fire_factor)
                    
                    st.session_state.rain_zones = DataProcessor.apply_intensity_factor(
                        st.session_state.rain_zones, st.session_state.rain_factor)
                    
                    # Calculate risk assessment
                    st.session_state.risk_assessment = DataProcessor.calculate_emergency_risk(
                        st.session_state.weather_data, 
                        st.session_state.traffic_data,
                        st.session_state.snow_zones,
                        st.session_state.fire_zones,
                        st.session_state.rain_zones,
                        st.session_state.snow_factor,
                        st.session_state.fire_factor,
                        st.session_state.rain_factor
                    )
                    
                    # Set recommended route
                    route_order = DataProcessor.select_best_route(
                        st.session_state.routes,
                        st.session_state.snow_zones,
                        st.session_state.fire_zones,
                        st.session_state.rain_zones,
                        st.session_state.snow_factor,
                        st.session_state.fire_factor,
                        st.session_state.rain_factor
                    )
                    st.session_state.recommended_route_index = route_order[0]
                else:
                    st.error("❌ No routes found. Please check your input and try again.")
        
        # Apply changes from sliders
        if apply_changes and st.session_state.routes:
            # Apply intensity factors
            if st.session_state.snow_zones:
                st.session_state.snow_zones = DataProcessor.apply_intensity_factor(
                    st.session_state.snow_zones, st.session_state.snow_factor)
            
            if st.session_state.fire_zones:
                st.session_state.fire_zones = DataProcessor.apply_intensity_factor(
                    st.session_state.fire_zones, st.session_state.fire_factor)
            
            if st.session_state.rain_zones:
                st.session_state.rain_zones = DataProcessor.apply_intensity_factor(
                    st.session_state.rain_zones, st.session_state.rain_factor)
            
            # Recalculate risk assessment
            st.session_state.risk_assessment = DataProcessor.calculate_emergency_risk(
                st.session_state.weather_data, 
                st.session_state.traffic_data,
                st.session_state.snow_zones,
                st.session_state.fire_zones,
                st.session_state.rain_zones,
                st.session_state.snow_factor,
                st.session_state.fire_factor,
                st.session_state.rain_factor
            )
            
            # Recalculate recommended route
            route_order = DataProcessor.select_best_route(
                st.session_state.routes,
                st.session_state.snow_zones,
                st.session_state.fire_zones,
                st.session_state.rain_zones,
                st.session_state.snow_factor,
                st.session_state.fire_factor,
                st.session_state.rain_factor
            )
            st.session_state.recommended_route_index = route_order[0]
            
            st.success("✅ Weather intensity changes applied!")
        
        # Process find exits request
        if find_exits and st.session_state.routes:
            with st.spinner("Finding safe exit points..."):
                start_lat = st.session_state.routes[0]["legs"][0]["start_location"]["lat"]
                start_lon = st.session_state.routes[0]["legs"][0]["start_location"]["lng"]
                
                st.session_state.safe_exits = DataProcessor.suggest_safe_exits(
                    start_lat, 
                    start_lon,
                    st.session_state.weather_data,
                    st.session_state.traffic_data,
                    st.session_state.snow_zones,
                    st.session_state.fire_zones,
                    st.session_state.rain_zones,
                    st.session_state.snow_factor,
                    st.session_state.fire_factor,
                    st.session_state.rain_factor
                )
        
        # Display routes if available
        if st.session_state.routes:
            st.subheader("🛣️ Available Routes")
            
            # Display route information
            for idx, route in enumerate(st.session_state.routes):
                is_recommended = (idx == st.session_state.recommended_route_index)
                with st.expander(f"Route {idx+1} - {route['legs'][0]['distance']['text']} ({route['legs'][0]['duration']['text']})" + 
                                (" ✅ RECOMMENDED" if is_recommended else "")):
                    st.markdown("### Turn-by-Turn Directions")
                    for step in route["legs"][0]["steps"]:
                        st.markdown(f"- {step['html_instructions']} ({step['distance']['text']}, {step['duration']['text']})", 
                                   unsafe_allow_html=True)
            
            # Create simulated city markers
            city_markers = []
            for i in range(10):
                start_lat = st.session_state.routes[0]["legs"][0]["start_location"]["lat"]
                start_lon = st.session_state.routes[0]["legs"][0]["start_location"]["lng"]
                end_lat = st.session_state.routes[0]["legs"][0]["end_location"]["lat"]
                end_lon = st.session_state.routes[0]["legs"][0]["end_location"]["lng"]
                
                # Interpolate between start and end
                t = i / 10
                city_lat = start_lat + (end_lat - start_lat) * t
                city_lon = start_lon + (end_lon - start_lon) * t
                
                city_markers.append({"lat": city_lat, "lon": city_lon, "name": f"City {i+1}"})
            
            # Render the route map
            UI.render_route_map(
                st.session_state.routes, 
                city_markers, 
                st.session_state.traffic_data,
                st.session_state.snow_zones,
                st.session_state.fire_zones,
                st.session_state.rain_zones,
                st.session_state.recommended_route_index
            )
            
            # Render weather points legend
            UI.render_weather_points_legend()
            
            # Display nearby cities and exits
            start_lat = st.session_state.routes[0]["legs"][0]["start_location"]["lat"]
            start_lon = st.session_state.routes[0]["legs"][0]["start_location"]["lng"]
            nearby_cities, highway_exits = APIService.get_nearby_cities_and_exits(start_lat, start_lon)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏙️ Nearby Cities")
                if nearby_cities:
                    for city in nearby_cities:
                        st.markdown(f"- **{city['city']}** ({city['distance_km']:.1f} km)")
                else:
                    st.info("No nearby cities found")
            
            with col2:
                st.subheader("🛣️ Nearby Highway Exits")
                if highway_exits:
                    for exit_point in highway_exits:
                        st.markdown(f"- **{exit_point['exit_name']}** ({exit_point['distance_km']:.1f} km)")
                else:
                    st.info("No nearby highway exits found")
            
            # Display weather graphs if data is available
            if st.session_state.weather_data:
                UI.render_weather_graphs(st.session_state.weather_data)
            
            # Display risk assessment if available
            if st.session_state.risk_assessment:
                UI.render_risk_assessment(st.session_state.risk_assessment)
        
        # Display safe exits if available
        if st.session_state.safe_exits:
            UI.render_safe_exits(
                st.session_state.safe_exits,
                st.session_state.snow_zones,
                st.session_state.fire_zones,
                st.session_state.rain_zones,
                st.session_state.snow_factor,
                st.session_state.fire_factor,
                st.session_state.rain_factor
            )
        
        # Add footer
        st.markdown("---")
        st.markdown("### 📱 Emergency Contacts")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Emergency Services:** 911")
        with col2:
            st.markdown("**Road Assistance:** 1-800-AAA-HELP")
        with col3:
            st.markdown("**Weather Hotline:** 1-800-WX-ALERT")

# Add the missing generate_exit_analytics function to DataProcessor
def generate_exit_analytics(exit_point, snow_zones, fire_zones, rain_zones, 
                          snow_factor, fire_factor, rain_factor):
    """Generate detailed analytics for an exit point"""
    # Calculate distance to nearest hazards
    nearest_snow = float('inf')
    nearest_fire = float('inf')
    nearest_rain = float('inf')
    
    if snow_zones:
        for zone in snow_zones:
            dist = geodesic((exit_point['lat'], exit_point['lon']), (zone['lat'], zone['lon'])).km
            nearest_snow = min(nearest_snow, dist)
    
    if fire_zones:
        for zone in fire_zones:
            dist = geodesic((exit_point['lat'], exit_point['lon']), (zone['lat'], zone['lon'])).km
            nearest_fire = min(nearest_fire, dist)
    
    if rain_zones:
        for zone in rain_zones:
            dist = geodesic((exit_point['lat'], exit_point['lon']), (zone['lat'], zone['lon'])).km
            nearest_rain = min(nearest_rain, dist)
    
    # Generate time-based safety forecast
    hours = list(range(24))
    safety_forecast = []
    
    base_safety = exit_point['safety_score']
    for hour in hours:
        # Simulate changing conditions over time
        time_factor = 1.0 + 0.2 * np.sin(hour / 24 * 2 * np.pi)
        hourly_safety = min(100, max(0, base_safety * time_factor))
        
        safety_forecast.append({
            'hour': hour,
            'safety_score': hourly_safety,
            'snow_impact': exit_point['weather_impacts']['snow_impact'] * (1 + 0.3 * np.sin(hour / 12 * np.pi)),
            'fire_impact': exit_point['weather_impacts']['fire_impact'] * (1 - 0.2 * np.sin(hour / 8 * np.pi)),
            'rain_impact': exit_point['weather_impacts']['rain_impact'] * (1 + 0.4 * np.sin(hour / 6 * np.pi))
        })
    
    # Generate comparative data with other exits
    comparative_metrics = {
        'emergency_service_proximity': random.uniform(60, 95),
        'road_accessibility': random.uniform(70, 98),
        'evacuation_speed': random.uniform(65, 90),
        'shelter_availability': random.uniform(50, 85),
        'communication_reliability': random.uniform(75, 95)
    }
    
    # Generate resource availability data
    resources = [
        {'name': 'Fuel Stations', 'availability': random.uniform(50, 100)},
        {'name': 'Medical Facilities', 'availability': random.uniform(40, 90)},
        {'name': 'Food & Water', 'availability': random.uniform(60, 95)},
        {'name': 'Shelter', 'availability': random.uniform(55, 85)},
        {'name': 'Communication', 'availability': random.uniform(70, 100)}
    ]
    
    # Generate historical evacuation success data
    historical_evac = []
    for i in range(10):
        year = 2015 + i
        historical_evac.append({
            'year': year,
            'success_rate': random.uniform(70, 95),
            'avg_evacuation_time': random.uniform(20, 60),
            'incidents': random.randint(1, 8)
        })
    
    return {
        'nearest_hazards': {
            'snow_distance_km': nearest_snow if nearest_snow != float('inf') else None,
            'fire_distance_km': nearest_fire if nearest_fire != float('inf') else None,
            'rain_distance_km': nearest_rain if nearest_rain != float('inf') else None
        },
        'safety_forecast': safety_forecast,
        'comparative_metrics': comparative_metrics,
        'resource_availability': resources,
        'historical_evacuation': historical_evac,
        'terrain_analysis': {
            'elevation': random.uniform(100, 1000),
            'slope': random.uniform(1, 15),
            'vegetation_density': random.uniform(10, 80),
            'water_bodies': random.randint(0, 5)
        }
    }

# Add the function to the DataProcessor class
DataProcessor.generate_exit_analytics = generate_exit_analytics

# Main entry point
if __name__ == "__main__":
    app = EmergencyRouteApp()
    app.run()
