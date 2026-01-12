import streamlit as st
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import folium_static
import requests
import polyline
from datetime import datetime
import os
from dotenv import load_dotenv

st.set_page_config(page_title="Taxi Fleet Dashboard", layout="wide")

# Load .env file
load_dotenv()

# API Keys

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
TOMORROW_IO_API_KEY = os.getenv("TOMORROW_IO_API_KEY")  

# Weather Code Mapping
def map_weather_code(code):
    weather_conditions = {
        1000: "Clear",
        1100: "Mostly Clear",
        1101: "Partly Cloudy",
        1102: "Mostly Cloudy",
        1001: "Cloudy",
        2000: "Fog",
        4000: "Drizzle",
        4200: "Light Rain",
        4001: "Rain",
        4201: "Heavy Rain",
    }
    return weather_conditions.get(code, "Unknown")

# Convert Place Name to Coordinates using Google Geocoding API
def get_coordinates(location):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    
    if response["status"] != "OK":
        st.error(f"Failed to geocode location: {response.get('error_message', 'Unknown error')}")
        return None
    
    coords = response["results"][0]["geometry"]["location"]
    return f"{coords['lat']},{coords['lng']}"

# Function to Fetch Directions
def get_directions(start, end, traffic_model="best_guess", alternatives=False):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode=driving&traffic_model={traffic_model}&departure_time=now&alternatives={str(alternatives).lower()}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()

    if response.get("status") != "OK":
        st.error(f"Google Maps API Error: {response.get('status')} - {response.get('error_message', '')}")
        return None, None, None

    main_route = response["routes"][0]
    main_polyline = polyline.decode(main_route["overview_polyline"]["points"])
    
    alt_polyline = None
    alt_route = None
    if len(response["routes"]) > 1:
        alt_polyline = polyline.decode(response["routes"][1]["overview_polyline"]["points"])
        alt_route = response["routes"][1]

    return main_polyline, main_route, alt_polyline, alt_route

def get_coordinates2(location):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()
    
    if response.get("status") != "OK":
        st.error(f"Failed to geocode location: {response.get('error_message', 'Unknown error')}")
        return None, None
    
    coords = response["results"][0]["geometry"]["location"]
    return coords['lat'], coords['lng']

def display_traffic_map(start_location, zoom):
    lat, lng = get_coordinates2(start_location)
    if lat is None or lng is None:
        return
    
    m = folium.Map(location=[lat, lng], zoom_start=zoom)
    folium.TileLayer("cartodbpositron").add_to(m)
    
    # Add Traffic Layer (Google Maps Traffic Layer via Tile Overlay)
    folium.raster_layers.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=m@221097413,traffic&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Traffic',
        overlay=True,
        control=True
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    folium_static(m)

# Function to Fetch Weather Data from Tomorrow.io
def get_weather_data(location):
    coordinates = get_coordinates(location)
    if not coordinates:
        return None
    url = f"https://api.tomorrow.io/v4/timelines?location={coordinates}&fields=temperature,weatherCode&timesteps=1h&apikey={TOMORROW_IO_API_KEY}"
    response = requests.get(url).json()
    
    print(response)

    if "data" not in response or "timelines" not in response["data"]:
        st.error("Failed to fetch weather data.")
        return None
    
    hourly_data = response["data"]["timelines"][0]["intervals"]
    weather_df = pd.DataFrame({
        "Hour": [datetime.strptime(entry["startTime"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d %H:%M") for entry in hourly_data],
        "Temperature (°C)": [entry["values"]["temperature"] for entry in hourly_data],
        "Weather Condition": [map_weather_code(entry["values"].get("weatherCode", 1000)) for entry in hourly_data]
    })
    return weather_df


def get_traffic_data(route):
    traffic_points = []
    for leg in route['legs']:
        for step in leg['steps']:
            if 'traffic_speed_entry' in step and step['traffic_speed_entry']:
                for traffic_data in step['traffic_speed_entry']:
                    traffic_points.append({
                        "location": step['end_location'],
                        "traffic_level": traffic_data['congestion'] if 'congestion' in traffic_data else "Unknown"
                    })
    return traffic_points

def get_directions_with_traffic(start, end, traffic_model="best_guess", alternatives=False):
    url = f"https://maps.googleapis.com/maps/api/directions/json?origin={start}&destination={end}&mode=driving&traffic_model={traffic_model}&departure_time=now&alternatives={str(alternatives).lower()}&key=YOUR_GOOGLE_MAPS_API_KEY"
    response = requests.get(url).json()

    if response.get("status") != "OK":
        st.error(f"Google Maps API Error: {response.get('status')} - {response.get('error_message', '')}")
        return None, None, None, None

    main_route = response["routes"][0]
    main_polyline = polyline.decode(main_route["overview_polyline"]["points"])
    main_traffic = get_traffic_data(main_route)
    
    alt_polyline = None
    alt_route = None
    alt_traffic = None
    if len(response["routes"]) > 1:
        alt_route = response["routes"][1]
        alt_polyline = polyline.decode(alt_route["overview_polyline"]["points"])
        alt_traffic = get_traffic_data(alt_route)

    return main_polyline, main_route, main_traffic, alt_polyline, alt_route, alt_traffic


def main():
    st.title("🚖 Taxi Fleet Management Dashboard")
    st.sidebar.header("Filters")

    start_location = st.sidebar.text_input("Enter Start Location", "Times Square, NYC")
    end_location = st.sidebar.text_input("Enter End Location", "Central Park, NYC")

    st.sidebar.subheader("Dynamic Route Optimization")
    traffic_level = st.sidebar.slider("Traffic Level (%)", 0, 100, 50)
    zoom_level = st.sidebar.slider("Traffic Map Zoom Level", 10, 18, 13)

    route_info = None
    alt_polyline = None
    alt_route_info = None

    if st.sidebar.button("Find Route"):
        traffic_model = "best_guess"
        if traffic_level > 70:
            traffic_model = "pessimistic"
        elif traffic_level < 30:
            traffic_model = "optimistic"

        st.subheader("🚀 Optimal Route Based on Traffic")
        main_polyline, route_info, alt_polyline, alt_route_info = get_directions(start_location, end_location, traffic_model, alternatives=True)

        if route_info:
            eta_main = route_info['legs'][0]['duration']['text']
            st.metric(label="Best Route Distance", value=route_info['legs'][0]['distance']['text'])
            st.metric(label="Best Route ETA", value=eta_main)
        
        if alt_route_info:
            eta_alt = alt_route_info['legs'][0]['duration']['text']
            st.metric(label="Alternative Route Distance", value=alt_route_info['legs'][0]['distance']['text'])
            st.metric(label="Alternative Route ETA", value=eta_alt)

        st.subheader("📍 NYC Optimal Taxi Route Visualization")
        m = folium.Map(location=[40.73061, -73.9352], zoom_start=11)

        if main_polyline:
            folium.PolyLine(locations=main_polyline, color='blue', weight=5, tooltip="Main Route").add_to(m)
        if alt_polyline:
            folium.PolyLine(locations=alt_polyline, color='red', weight=5, tooltip="Alternative Route").add_to(m)
        
        folium_static(m)

    # Cost Estimation Section
    st.subheader("🚖 Route Cost Estimation")
    vehicle_type = st.radio("Select Vehicle Type", ["Sedan", "SUV", "Luxury"])

    fuel_efficiency = {"Sedan": 30, "SUV": 20, "Luxury": 15}  # MPG
    fuel_price_per_gallon = 3.5  # USD per gallon
    base_fare = 5  # Base fare for trip

    

    if route_info:
        distance_miles = float(route_info['legs'][0]['distance']['text'].split()[0])
        fuel_used_main = distance_miles / fuel_efficiency[vehicle_type]
        fuel_cost_main = fuel_used_main * fuel_price_per_gallon
        estimated_fare_main = round(base_fare + fuel_cost_main, 2)

        cost_data = pd.DataFrame({
            "Route": ["Main Route"],
            "Distance (miles)": [distance_miles],
            "Fuel Cost ($)": [round(fuel_cost_main, 2)],
            "Estimated Fare ($)": [estimated_fare_main]
        })

        st.table(cost_data)
    
    if alt_polyline and route_info:
        alt_distance_miles = distance_miles * 1.1  # Assume 10% longer for alternate route
        fuel_used_alt = alt_distance_miles / fuel_efficiency[vehicle_type]
        fuel_cost_alt = fuel_used_alt * fuel_price_per_gallon
        estimated_fare_alt = round(base_fare + fuel_cost_alt, 2)

        alt_cost_data = pd.DataFrame({
            "Route": ["Alternative Route"],
            "Distance (miles)": [alt_distance_miles],
            "Fuel Cost ($)": [round(fuel_cost_alt, 2)],
            "Estimated Fare ($)": [estimated_fare_alt]
        })

        st.table(alt_cost_data)

    if st.sidebar.button("Show Traffic Map"):
        st.subheader("🚦 Real-Time Traffic Conditions")
        display_traffic_map(start_location, zoom_level)

    # Weather Data
    st.subheader("⛅ Hourly Weather Trends Based on Start Location")
    weather_df = get_weather_data(start_location)
    if weather_df is not None:
        fig_weather = px.line(weather_df, x="Hour", y="Temperature (°C)", title="Hourly Temperature Trends")
        st.plotly_chart(fig_weather)
        
        fig_weather_conditions = px.bar(weather_df, x="Hour", y="Weather Condition", title="Hourly Weather Conditions", text="Weather Condition")
        st.plotly_chart(fig_weather_conditions)

if __name__ == "__main__":
    main()