
import streamlit as st
import folium
from streamlit_folium import folium_static


import requests
from fastapi import FastAPI
from typing import Dict

app = FastAPI()


GOOGLE_MAPS_API_KEY = "AIzaSyCcy95nDmWbTetdEYPLzgy9yv3yM7DiARM"

# Hazard Data Simulation
fire_zones = {"Santa Cruz"}  # Simulating fire alerts
snow_areas = {"Lake Tahoe"}  # Simulating snow alerts

# Function to Get Directions from Google Maps API
def get_directions(start: str, end: str):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    return response.json()

# Function to Check for Hazards
def check_hazards(start: str, end: str):
    warnings = []
    if start in fire_zones or end in fire_zones:
        warnings.append("⚠️ Route may be affected by wildfires.")
    if start in snow_areas or end in snow_areas:
        warnings.append("❄️ Route may be affected by snow.")
    return warnings

@app.get("/")
def read_root():
    return {"message": "Use /route?start=Santa Cruz&end=San Jose to get directions"}

@app.get("/route")
def get_route(start: str, end: str) -> Dict:
    directions = get_directions(start, end)
    if directions["status"] == "OK":
        route_steps = [step["html_instructions"] for step in directions["routes"][0]["legs"][0]["steps"]]
        total_distance = directions["routes"][0]["legs"][0]["distance"]["text"]

        # Extract waypoints (latitude, longitude)
        route_points = []
        for step in directions["routes"][0]["legs"][0]["steps"]:
            lat = step["start_location"]["lat"]
            lng = step["start_location"]["lng"]
            route_points.append([lat, lng])
        
        # Append final destination
        route_points.append([
            directions["routes"][0]["legs"][0]["end_location"]["lat"],
            directions["routes"][0]["legs"][0]["end_location"]["lng"]
        ])

        warnings = check_hazards(start, end)

        return {
            "route": route_steps,
            "total_distance": total_distance,
            "route_points": route_points,
            "warnings": warnings
        }
    else:
        return {"error": "No route found"}
