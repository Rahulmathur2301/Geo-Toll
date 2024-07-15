# Import required libraries
import streamlit as st
from shapely.geometry import Polygon, LineString
import math
import random
import folium
from folium.plugins import HeatMap
from streamlit.components.v1 import html as st_html

# Custom CSS for styling
st.markdown("""
    <style>
    .main {background-color: #000000;}
    .header {background-color: #4CAF50; padding: 20px; color: black; text-align: center;}
    .subheader {background-color: #e7e7e7; padding: 10px; margin-top: 10px; color: black;}
    .section {padding: 10px; margin-top: 10px; border-radius: 5px; background-color: #ffffff; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); color: black;}
    </style>
    """, unsafe_allow_html=True)

# Initialize coordinates for different locations
location_coordinates = {
    "Meerut": (28.9845, 77.7064),
    "Mathura": (27.4924, 77.6737),
    "Gurugram": (28.4595, 77.0266),
    "Agra": (27.1767, 78.0081)
}

# Define toll zones with their boundaries
toll_areas = {
    "Zone 1": Polygon([(77.5, 28.9), (78.0, 28.9), (78.0, 28.7), (77.5, 28.7)]),
    "Zone 2": Polygon([(77.05, 28.0), (77.55, 28.0), (77.55, 27.75), (77.05, 27.75)]),
    "Zone 3": Polygon([(77.2, 28.1), (77.5, 28.1), (77.5, 28.4), (77.2, 28.4)]),
    "Zone 4": Polygon([(77.65, 27.85), (78.05, 27.85), (78.05, 28.25), (77.65, 28.25)])
}

# Calculate distance between two geographical points
def get_distance(point1, point2):
    lat1, lon1 = point1
    lat2, lon2 = point2
    earth_radius = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return earth_radius * c

# Simulate the movement of a vehicle between two locations
def vehicle_route_simulation(start, end):
    start_point = location_coordinates[start]
    end_point = location_coordinates[end]
    total_distance = get_distance(start_point, end_point)
    route_path = LineString([(start_point[1], start_point[0]), (end_point[1], end_point[0])])
    zones_crossed = []
    distances_in_zones = []
    
    for zone, area in toll_areas.items():
        if route_path.intersects(area):
            intersection = route_path.intersection(area)
            zones_crossed.append(zone)
            distances_in_zones.append(intersection.length * 111.32)  # Convert degrees to km
    
    return total_distance, zones_crossed, distances_in_zones

# Compute toll charges based on vehicle type and zones crossed
def toll_calculation(vehicle, crossed_zones, zone_distances, rate_per_km):
    toll_details = []
    total_toll_cost = 0
    
    for zone, dist in zip(crossed_zones, zone_distances):
        if zone == "Zone 1":
            toll_charge = rate_per_km * dist * 1.55
        elif zone == "Zone 2":
            toll_charge = rate_per_km * dist * 1.25
        elif zone == "Zone 3":
            toll_charge = rate_per_km * dist * 1.35
        else:
            toll_charge = rate_per_km * dist * 1.45
        total_toll_cost += toll_charge
        toll_details.append((zone, dist, toll_charge))
    
    return total_toll_cost, toll_details

# Start Streamlit application
st.markdown('<div class="header">GPS-Based Toll System Simulation</div>', unsafe_allow_html=True)

# User inputs for simulation in columns
col1, col2 = st.columns(2)
with col1:
    start_location = st.selectbox("Choose Start Location", list(location_coordinates.keys()))
with col2:
    end_location = st.selectbox("Choose End Location", list(location_coordinates.keys()))

vehicle_choice = st.selectbox("Select Vehicle Type", ["Car", "Truck", "SUV", "Ambulance"])

# Dynamic pricing based on congestion at the start location
congestion_levels = {loc: random.uniform(0, 1) for loc in location_coordinates}
current_congestion = congestion_levels[start_location]
vehicles_count = round(current_congestion * 500, 0)

st.markdown('<div class="subheader">Dynamic Pricing Information</div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
for loc, congestion in congestion_levels.items():
    st.write(f"{loc}: {congestion * 100:.2f}%")
st.markdown('</div>', unsafe_allow_html=True)

base_price_per_km = current_congestion * (0.25 if vehicle_choice == "Car" else 0.50 if vehicle_choice == "Truck" else 0.35 if vehicle_choice == "SUV" else 0.00)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.write(f"Price per km in {start_location}: {base_price_per_km:.2f} INR/km")
st.write(f"Number of vehicles on the road in {start_location}: {vehicles_count}")
st.markdown('</div>', unsafe_allow_html=True)

# Speed limits based on vehicle type and section
speed_restrictions = {
    "Car": {"Section A": 80, "Section B": 100, "Section C": 120},
    "SUV": {"Section A": 90, "Section B": 110, "Section C": 120},
    "Truck": {"Section A": 70, "Section B": 80, "Section C": 90},
    "Ambulance": {"Section A": float("inf"), "Section B": float("inf"), "Section C": float("inf")}
}

# Random vehicle speeds for different sections
random_speeds = {section: random.uniform(50, 120) for section in ["Section A", "Section B", "Section C"]}
st.markdown('<div class="subheader">Speed Information</div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
for section, speed_limit in speed_restrictions[vehicle_choice].items():
    st.write(f"{section} - Speed Limit: {'No limit' if vehicle_choice == 'Ambulance' else f'{speed_limit} km/h'}")
    st.write(f"{section} - Vehicle Speed: {random_speeds[section]:.2f} km/h")
st.markdown('</div>', unsafe_allow_html=True)

# Check for speed limit violations and calculate penalties
speed_penalty = 0
if start_location != end_location:
    for section, speed_limit in speed_restrictions[vehicle_choice].items():
        if random_speeds[section] > speed_limit and vehicle_choice != "Ambulance":
            st.warning(f"Speeding violation in {section}")
            speed_penalty += 500

# Calculate distance, simulate vehicle movement, and compute toll
travel_distance, zones_crossed, zone_distances = vehicle_route_simulation(start_location, end_location)
total_toll_cost, toll_details = toll_calculation(vehicle_choice, zones_crossed, zone_distances, base_price_per_km)

# Display toll details and total amount
st.markdown('<div class="subheader">Toll Information</div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
toll_discount = 0
for zone, distance, cost in toll_details:
    st.write(f"{zone}: Distance: {distance:.2f} km, Cost: {cost:.2f} INR")
    if random.choice([True, False]):
        toll_discount += 150
st.markdown('</div>', unsafe_allow_html=True)

final_amount = total_toll_cost + speed_penalty - toll_discount
st.markdown('<div class="subheader">Total Amount</div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.write(f"Total Distance: {travel_distance:.2f} km")
st.write(f"Total Toll: {total_toll_cost:.2f} INR")
st.write(f"Penalties: {speed_penalty:.2f} INR")
st.write(f"Toll Discount: {toll_discount:.2f} INR")
st.write(f"Final Amount: {final_amount:.2f} INR")
st.markdown('</div>', unsafe_allow_html=True)

# Map visualization of the route and toll zones
start_point = location_coordinates[start_location]
end_point = location_coordinates[end_location]
map_view = folium.Map(location=[(start_point[0] + end_point[0]) / 2, (start_point[1] + end_point[1]) / 2], zoom_start=7)
folium.Marker(location=start_point, popup=start_location, icon=folium.Icon(color="green")).add_to(map_view)
folium.Marker(location=end_point, popup=end_location, icon=folium.Icon(color="red")).add_to(map_view)
folium.PolyLine(locations=[start_point, end_point], color="blue").add_to(map_view)

for zone, boundary in toll_areas.items():
    folium.GeoJson(boundary, name=zone).add_to(map_view)
    zone_center = [boundary.bounds[1] + (boundary.bounds[3] - boundary.bounds[1]) / 2, boundary.bounds[0] + (boundary.bounds[2] - boundary.bounds[0]) / 2]
    folium.Marker(location=zone_center, popup=zone, icon=folium.Icon()).add_to(map_view)

heatmap_data = [(coords[0], coords[1], congestion_levels[loc]) for loc, coords in location_coordinates.items()]
HeatMap(heatmap_data).add_to(map_view)
st_html(map_view._repr_html_(), height=500)

