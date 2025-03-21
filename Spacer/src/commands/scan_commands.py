"""
Scanner command handlers for celestial body detection.
"""
import time
import math
from src.world.scanner import handle_scan, scan_celestial_body
from src.world.station import STATIONS

def handle_scan_command(player):
    """Handle the scan command to scan the current system"""
    handle_scan(player)

def handle_specific_scan_command(player, body_name):
    """Handle scanning a specific celestial body"""
    scan_celestial_body(player, body_name)

def handle_simple_scan(player):
    """Scan surroundings for points of interest (simplified version of scanner)"""
    print("\nScanning surrounding space...")
    time.sleep(1)
    
    # Get player position
    player_x = player.x
    player_y = player.y
    dim_name = player.dimension.name
    
    # Find nearby celestial bodies
    nearby_bodies = []
    for body_name, body_data in player.dimension.properties.items():
        if "Coordinates" in body_data:
            body_x = int(body_data["Coordinates"]["x"])
            body_y = int(body_data["Coordinates"]["y"])
            distance = max(abs(player_x - body_x), abs(player_y - body_y))
            if distance <= 10:  # Detect bodies within 10 units
                nearby_bodies.append((body_name, body_data["type"], distance))
    
    # Add nearby stations to scan results
    nearby_stations = []
    for station_id, station in STATIONS.items():
        # Check if the station is in the same dimension
        if station.dimension == player.dimension.name:
            distance = math.sqrt((station.x - player.x)**2 + (station.y - player.y)**2)
            if distance <= 10:  # Stations visible within 10 units
                nearby_stations.append((station, distance))
    
    if nearby_stations:
        print("\nStations detected:")
        for station, distance in sorted(nearby_stations, key=lambda x: x[1]):
            print(f"  {station.name} ({station.type}) - Distance: {distance:.1f} units")
    
    # Display results
    if nearby_bodies:
        print("\nDetected celestial bodies:")
        for name, body_type, dist in sorted(nearby_bodies, key=lambda x: x[2]):
            print(f"  {name} ({body_type}) - Distance: {dist} units")
    else:
        print("\nNo significant celestial bodies detected nearby.")
