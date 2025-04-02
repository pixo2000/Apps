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
            "info": "Station information",
            "scancoords": "Use a more powerful direct scan via the Station's systems (usage: scancoords <x> <y>)"
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
        # Handle basic commands first
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
            for service in ["Trading", "Repairs", "Missions", "Long-Range Scanning"]:
                print(f"- {service}")
            return True
        
        # Check if it's a coordinate scan command - must check this AFTER the basic commands
        elif command.startswith("scancoords "):
            # Import here to avoid circular imports
            from src.commands.scan_commands import handle_coordinate_scan
            coords = command[11:]  # Get everything after "scancoords "
            handle_coordinate_scan(player, coords)
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
            if station.type == "Station" or station.type == "Beacon":
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

def check_coords_for_objects(x, y, dimension_name, data=None):
    """Check what objects exist at specific coordinates"""
    # Import dangerous body types here to avoid circular imports
    from src.config import DANGEROUS_BODY_TYPES
    
    # Initialize result
    result = {
        "found": False,
        "objects": [],
        "is_dangerous": False  # Flag to identify if location contains a dangerous object
    }
    
    # Check for celestial bodies
    if data and "bodies" in data:
        for body_name, body_data in data["bodies"].items():
            if "Coordinates" in body_data:
                # Convert coordinates to integers (they might be strings)
                try:
                    body_x = int(body_data["Coordinates"]["x"])
                    body_y = int(body_data["Coordinates"]["y"])
                except (ValueError, TypeError):
                    body_x = 0
                    body_y = 0
                
                # Check body size - default to 1 if not specified
                try:
                    size_width = int(body_data.get("size", {}).get("width", 1))
                    size_height = int(body_data.get("size", {}).get("height", 1))
                except (ValueError, TypeError):
                    size_width = 1
                    size_height = 1
                    
                # Special case for stars and black holes - ensure minimum size
                if body_data.get("type", "").lower() in [t.lower() for t in DANGEROUS_BODY_TYPES]:
                    size_width = max(size_width, 5)  # Minimum size of 5 for stars and black holes
                    size_height = max(size_height, 5)  # Minimum size of 5 for stars and black holes
                
                # Calculate the coordinate bounds
                min_x = body_x - (size_width // 2)
                max_x = body_x + (size_width // 2)
                min_y = body_y - (size_height // 2)
                max_y = body_y + (size_height // 2)
                
                # Check if coordinates are within the body's bounds
                if min_x <= x <= max_x and min_y <= y <= max_y:
                    result["found"] = True
                    body_obj = {
                        "name": body_name,
                        "type": body_data.get("type", "Unknown"),
                        "description": body_data.get("description", f"A {body_data.get('type', 'celestial body')}")
                    }
                    result["objects"].append(body_obj)
                    
                    # Check if this is a dangerous body type
                    if body_data.get("type", "").lower() in [t.lower() for t in DANGEROUS_BODY_TYPES]:
                        # If the coordinates are anywhere within the bounds of a dangerous body, mark as dangerous
                        result["is_dangerous"] = True
                        result["danger_name"] = body_name
                        result["danger_type"] = body_data.get("type", "Unknown")
                        
                        # Additional check for direct center hit for more detailed messages
                        if x == body_x and y == body_y:
                            result["direct_hit"] = True
                        
                        # Include body size information
                        result["danger_size"] = {
                            "width": size_width,
                            "height": size_height
                        }
            
            # Check for moons
            if 'Moons' in body_data:
                for moon_name, moon_data in body_data['Moons'].items():
                    if 'Coordinates' in moon_data:
                        try:
                            moon_x = int(moon_data["Coordinates"]["x"])
                            moon_y = int(moon_data["Coordinates"]["y"])
                        except (ValueError, TypeError):
                            continue
                        
                        # Check moon size
                        moon_width = int(moon_data.get("size", {}).get("width", 1))
                        moon_height = int(moon_data.get("size", {}).get("height", 1))
                        
                        # Calculate the coordinate bounds
                        min_x = moon_x - (moon_width // 2)
                        max_x = moon_x + (moon_width // 2)
                        min_y = moon_y - (moon_height // 2)
                        max_y = moon_y + (moon_height // 2)
                        
                        # Check if coordinates are within the moon's bounds
                        if (min_x <= x <= max_x and min_y <= y <= max_y):
                            result["found"] = True
                            result["objects"].append({
                                "name": moon_name,
                                "type": "Moon",
                                "parent": body_name,
                                "description": moon_data.get("description", f"Moon of {body_name}")
                            })
    
    # Check for all stations at these coordinates
    for station_id, station in STATIONS.items():
        if station.x == x and station.y == y and station.dimension == dimension_name:
            # Include any type of station (Station, Beacon, etc.)
            result["found"] = True
            station_info = {
                "name": station.name,
                "type": station.type,
                "description": station.description
            }
            
            # Add parent info if available
            if hasattr(station, 'parent_body'):
                station_info["parent"] = station.parent_body
                if hasattr(station, 'parent_moon') and station.parent_moon:
                    station_info["parent"] = station.parent_moon
                    station_info["grandparent"] = station.parent_body
            
            result["objects"].append(station_info)
    
    # Check for hidden signals
    from src.config import HIDDEN_SIGNALS
    if dimension_name in HIDDEN_SIGNALS:
        for signal_name, coords in HIDDEN_SIGNALS[dimension_name].items():
            signal_x = coords["x"]
            signal_y = coords["y"]
            if signal_x == x and signal_y == y:
                result["found"] = True
                result["objects"].append({
                    "name": signal_name,
                    "type": "Special Signal",
                    "description": "An unusual signal of unknown origin"
                })
                
    return result

def is_safe_location(x, y, dimension_name, dimension_data):
    """Check if coordinates are safe (not on a dangerous celestial body)"""
    result = check_coords_for_objects(x, y, dimension_name, dimension_data)
    return not result.get("is_dangerous", False)

def get_nearby_dangers(x, y, dimension_name, dimension_data, warning_distance=15):
    """Check if there are dangerous objects near the specified coordinates"""
    dangers = []
    
    from src.config import DANGEROUS_BODY_TYPES
    
    # Check each body in the dimension
    for body_name, body_data in dimension_data.get('bodies', {}).items():
        body_type = body_data.get("type", "")
        if body_type.lower() in [t.lower() for t in DANGEROUS_BODY_TYPES]:
            if 'Coordinates' in body_data:
                try:
                    body_x = int(body_data["Coordinates"]["x"])
                    body_y = int(body_data["Coordinates"]["y"])
                except (ValueError, TypeError):
                    continue
                
                # Calculate distance to the dangerous body
                distance = max(abs(x - body_x), abs(y - body_y))
                
                # Include size in the calculation - a large star may be dangerous even if further away
                try:
                    size = max(
                        int(body_data.get("size", {}).get("width", 1)),
                        int(body_data.get("size", {}).get("height", 1))
                    )
                except (ValueError, TypeError):
                    size = 1
                
                # Adjust effective distance based on body size
                effective_distance = distance - (size // 2)
                effective_distance = max(0, effective_distance)  # Can't be negative
                
                # If within warning distance
                if effective_distance <= warning_distance:
                    dangers.append({
                        "name": body_name,
                        "type": body_type,
                        "distance": effective_distance,
                        "coords": (body_x, body_y)
                    })
    
    # Sort by distance - closest first
    dangers.sort(key=lambda x: x["distance"])
    return dangers

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