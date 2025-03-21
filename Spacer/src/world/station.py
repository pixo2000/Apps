"""
Station module for the Spacer game.
Handles station functionality and interactions in console-based interface.
"""
from src.world.dimension import Dimension

class Station:
    def __init__(self, name, description, station_type, x=0, y=0, dimension="A01"):
        self.name = name
        self.description = description
        self.type = station_type
        self.x = x
        self.y = y
        self.dimension = dimension
        self.available_options = {
            "launch": "Return to space",
            "quests": "View available missions",
            "trade": "Trade resources",
            "repair": "Repair your ship",
            "info": "Station information"
        }
    
    def get_description(self):
        """Get full station description"""
        return f"{self.name} - {self.description}"
    
    def display_options(self):
        """Display all available options at the station"""
        print(f"\n== {self.name} Station Interface ==")
        print(f"{self.description}\n")
        print("Available options:")
        
        for cmd, desc in self.available_options.items():
            print(f"  {cmd.ljust(10)} - {desc}")
        
        # Add additional option for showing options again
        print(f"  {'options'.ljust(10)} - Show this menu again")
        
        print("\nType an option or 'help' for more information.")
    
    def handle_command(self, command, player):
        """Process station-specific commands"""
        if command == "launch":
            print("\nLaunching from station...")
            player.docked_at = None
            print("You have left the station and returned to space.")
            return True
            
        elif command == "quests":
            print("\n== Available Missions ==")
            print("No active missions available at this time.")
            print("Check back later.")
            return True
            
        elif command == "trade":
            print("\nTrading functionality not yet implemented.")
            return True
            
        elif command == "repair":
            print("\nShip repair functionality not yet implemented.")
            return True
            
        elif command == "info":
            print(f"\n== {self.name} Information ==")
            print(f"{self.description}")
            print(f"Location: [{self.x}, {self.y}] in {player.dimension.title}")
            print(f"Type: {self.type}")
            
            # Add more detailed information
            print(f"Dimension: {self.dimension}")
            
            # Check if the station is attached to a planet/moon
            if hasattr(self, 'parent_body'):
                attached_to = f"{self.parent_body}"
                if hasattr(self, 'parent_moon') and self.parent_moon:
                    attached_to = f"{self.parent_moon} (Moon of {self.parent_body})"
                print(f"Attached to: {attached_to}")
            
            print("\nStation Services:")
            for service in ["Trading", "Repairs", "Missions"]:
                print(f"- {service}")
            return True
        
        return False  # Command not handled by station

# Dictionary to store stations dynamically loaded from dimensions
STATIONS = {}

def load_stations_from_dimension(dimension_data, dimension_name):
    """Load stations from dimension data into the STATIONS dictionary"""
    # Clear existing stations for this dimension
    for station_id in list(STATIONS.keys()):
        if STATIONS[station_id].dimension == dimension_name:
            del STATIONS[station_id]
            
    # Process all celestial bodies to find stations
    for body_name, body_data in dimension_data.get('bodies', {}).items():
        # Check if this body has stations
        if 'Stations' in body_data:
            for station_name, station_data in body_data['Stations'].items():
                # Get station coordinates
                if 'Coordinates' in station_data:
                    x = int(station_data['Coordinates']['x'])
                    y = int(station_data['Coordinates']['y'])
                else:
                    # If no coordinates, use body coordinates
                    if 'Coordinates' in body_data:
                        x = int(body_data['Coordinates']['x'])
                        y = int(body_data['Coordinates']['y'])
                    else:
                        x, y = 0, 0
                
                # Create a unique station ID
                station_id = f"{dimension_name}_{body_name}_{station_name}".lower().replace(' ', '_')
                
                # Get station description
                description = station_data.get('description', f"A {station_data.get('type', 'unknown')} on {body_name}")
                
                # Add to STATIONS dictionary
                STATIONS[station_id] = Station(
                    station_name, 
                    description, 
                    station_data.get('type', 'Station'),
                    x, y, 
                    dimension_name
                )
        
        # Check if this body has moons with stations
        if 'Moons' in body_data:
            for moon_name, moon_data in body_data['Moons'].items():
                # Process stations on moons
                if 'Stations' in moon_data:
                    for station_name, station_data in moon_data['Stations'].items():
                        # Get station coordinates (use moon coordinates if station doesn't have specific ones)
                        if 'Coordinates' in station_data:
                            x = int(station_data['Coordinates']['x'])
                            y = int(station_data['Coordinates']['y'])
                        else:
                            if 'Coordinates' in moon_data:
                                x = int(moon_data['Coordinates']['x'])
                                y = int(moon_data['Coordinates']['y'])
                            else:
                                x, y = 0, 0
                        
                        # Create a unique station ID for moon station
                        station_id = f"{dimension_name}_{body_name}_{moon_name}_{station_name}".lower().replace(' ', '_')
                        
                        # Get station description
                        description = station_data.get('description', f"A {station_data.get('type', 'unknown')} on {moon_name}, Moon of {body_name}")
                        
                        # Add to STATIONS dictionary
                        STATIONS[station_id] = Station(
                            station_name, 
                            description, 
                            station_data.get('type', 'Station'),
                            x, y, 
                            dimension_name
                        )
                        # Store the parent moon and planet for reference
                        STATIONS[station_id].parent_moon = moon_name
                        STATIONS[station_id].parent_body = body_name

def get_station_at_coords(x, y, dimension_name):
    """Check if there's a station at the given coordinates in the specified dimension"""
    for station_id, station in STATIONS.items():
        if station.x == x and station.y == y and station.dimension == dimension_name:
            # Only return if it's actually a station or beacon type, not a city
            if station.type == "Station":
                return station
    return None

def get_city_at_coords(x, y, dimension_name):
    """Check if there's a city at the given coordinates in the specified dimension"""
    for station_id, station in STATIONS.items():
        if station.x == x and station.y == y and station.dimension == dimension_name:
            # Only return if it's a city type
            if station.type == "City":
                return station
    return None

def get_station_by_id(station_id):
    """Find a station by its ID"""
    if station_id in STATIONS:
        return STATIONS[station_id]
    
    # Try to parse the ID to find the station by other means
    parts = station_id.split('_')
    if len(parts) >= 2:
        dim_name = parts[0]
        
        # Try different parsing methods to find the station
        # Method 1: Look for exact station name match
        for sid, station in STATIONS.items():
            if station.dimension == dim_name and sid.endswith(station_id.split('_', 1)[1]):
                return station
        
        # Method 2: Look for station with matching name in the same dimension
        station_name = station_id.split('_')[-1].replace('_', ' ')
        for sid, station in STATIONS.items():
            if station.dimension == dim_name and station.name.lower() == station_name.lower():
                return station
                
        # Method 3: Just find any station at the coordinates in save file
        # This requires additional code to extract coordinates from save file
        # which we don't have direct access to here
    
    # Debug info to help diagnose station loading issues
    print(f"Debug - Available stations in system: {[s for s in STATIONS.keys() if s.startswith(station_id.split('_')[0])]}")
    
    return None

def load_all_stations():
    """Load stations from all available dimensions"""
    from src.world.dimension import Dimension
    
    # Get all available dimensions
    dimensions = Dimension.get_available_dimensions()
    
    # Load stations from each dimension
    for dim_name in dimensions:
        try:
            dim = Dimension(dim_name)
            load_stations_from_dimension(
                {'bodies': dim.properties}, 
                dim_name
            )
        except Exception as e:
            print(f"Error loading stations from dimension {dim_name}: {e}")