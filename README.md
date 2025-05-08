### Emergency Route System

## Overview

The Emergency Route System is an advanced web application built with Streamlit that helps users navigate safely during emergency situations. It combines real-time weather data, traffic information, and route planning to provide the safest possible travel options during adverse conditions.

The system visualizes potential hazards like snow, rain, and fire zones along routes, calculates risk assessments, and suggests safe exit points with detailed analytics to help users make informed decisions during emergencies.

## Features

- **Multi-route Planning**: Fetches and displays multiple route options between start and destination points
- **Weather Visualization**: Displays snow, rain, and fire zones with adjustable intensity controls
- **Risk Assessment**: Calculates overall emergency risk based on weather and traffic conditions
- **Safe Exit Recommendations**: Suggests and analyzes safe exit points with detailed metrics
- **Interactive Maps**: Visualizes routes, hazards, and exit points on interactive maps
- **Weather Forecasting**: Shows hourly weather graphs for rainfall, snowfall, and temperature
- **Comparative Analytics**: Provides detailed comparative analysis of exit points
- **Historical Data**: Displays historical safety and evacuation data for informed decision-making


## Installation

1. Clone the repository:


```shellscript
git clone https://github.com/yourusername/emergency-route-system.git
cd emergency-route-system
```

2. Install required dependencies:


```shellscript
pip install -r requirements.txt
```

3. Set up API keys:

1. Get a Google Maps API key from [Google Cloud Platform](https://cloud.google.com/maps-platform/)
2. Get an OpenWeatherMap API key from [OpenWeatherMap](https://openweathermap.org/api)
3. Update the `Config` class in the code with your API keys





## Usage

1. Run the Streamlit application:


```shellscript
streamlit run main.py
```

2. Enter your starting location and destination in the input fields
3. Click "Get Live Routes" to fetch available routes
4. Adjust weather intensity sliders in the sidebar to simulate different conditions
5. Click "Find Safe Exit Points" to get recommendations for safe exits
6. Explore the interactive maps, graphs, and analytics provided


## Code Structure

The application is organized into several key classes:

### Config

Stores API keys and configuration settings for the application.

### APIService

Handles all external API calls including:

- Google Maps Directions API for route planning
- OpenWeatherMap API for weather data
- Simulated traffic data generation
- Nearby cities and exits data


### DataProcessor

Processes data and generates simulations:

- Generates realistic snow, fire, and rain zones
- Calculates emergency risk assessments
- Suggests safe exit points
- Selects the best route based on safety factors


### UI

Manages all Streamlit UI components:

- Renders maps, charts, and visualizations
- Creates interactive controls
- Displays analytics and recommendations


### EmergencyRouteApp

Main application class that coordinates all components and manages the application flow.

## Dependencies

- streamlit: Web application framework
- pydeck: Map visualization
- plotly: Interactive charts and graphs
- requests: API calls
- geopy: Geographic calculations
- numpy: Numerical operations
- pandas: Data manipulation


## Configuration

The application uses the following configuration parameters in the `Config` class:

```python
class Config:
    # API keys
    GOOGLE_MAPS_API_KEY = "YOUR_GOOGLE_MAPS_API_KEY"
    OPENWEATHERMAP_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
    
    # Map settings
    DEFAULT_ZOOM = 5
    DEFAULT_PITCH = 45
    
    # Weather simulation settings
    SNOW_POINTS = 50
    FIRE_POINTS = 50
    RAIN_POINTS = 50
```

## Example Use Cases

1. **Emergency Evacuation Planning**: Plan evacuation routes during natural disasters
2. **First Responder Navigation**: Help emergency services find the safest routes to incidents
3. **Logistics and Transportation**: Plan delivery routes during adverse weather conditions
4. **Travel Safety**: Help travelers avoid hazardous areas during their journeys
5. **Emergency Management**: Assist emergency management agencies in planning and response


## Future Improvements

- Integration with real-time emergency alert systems
- Mobile app version for on-the-go access
- Machine learning models to predict hazard development
- User accounts to save favorite routes and preferences
- Offline mode for use during network outages
- Integration with vehicle navigation systems
- Support for pedestrian and public transit evacuation routes


## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This application uses simulated data for demonstration purposes. In real emergency situations, always follow instructions from local authorities and emergency services.

## Acknowledgements

- Google Maps Platform for route planning capabilities
- OpenWeatherMap for weather data services
- Streamlit for the interactive web application framework
- Plotly and PyDeck for data visualization components
