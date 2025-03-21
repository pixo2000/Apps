"""
Player class with core attributes and state tracking.
"""
import uuid
from station import STATIONS
from dimension import Dimension
from config import DEFAULT_START_POSITION, DEFAULT_START_DIMENSION, DEFAULT_START_LANDED, DEFAULT_START_CITY, DEFAULT_START_BODY, DEFAULT_START_MOON

class Player:
    def __init__(self, name):
        self.name = name
        self.x = DEFAULT_START_POSITION["x"]
        self.y = DEFAULT_START_POSITION["y"]
        self.dimension = Dimension(DEFAULT_START_DIMENSION)
        self.known_dimensions = [DEFAULT_START_DIMENSION]  # Start with the first dimension as known
        self.known_bodies = {}  # Dictionary for discovered celestial bodies by dimension
        self.uuid = str(uuid.uuid4())  # Generate unique ID for the player
        self.creation_date = None  # Will be set during game initialization
        self.playtime = 0  # Playtime in seconds
        self.last_login = None  # Will be updated when saving
        self.is_dead = False  # Player's living status
        self.docked_at = None  # Will hold station object when docked
        
        # Set up initial landing state
        self.landed_on = DEFAULT_START_CITY if DEFAULT_START_LANDED else None
        self.landed_on_body = DEFAULT_START_BODY if DEFAULT_START_LANDED else None
        self.landed_on_moon = DEFAULT_START_MOON if DEFAULT_START_LANDED else None
    
    def change_name(self, new_name):
        """Change the player's name"""
        self.name = new_name
        return True
        
    def kill(self):
        """Marks the player as deceased"""
        self.is_dead = True
        print("\n☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠")
        print("☠           GAME OVER            ☠")
        print(f"☠  Captain {self.name} has perished.  ☠")
        print("☠ Your journey ends here, among  ☠")
        print("☠     the stars you explored.    ☠")
        print("☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠ ☠\n")
        return True
        
    def position(self, variable):
        """Get position information"""
        if variable == "x":
            return self.x
        elif variable == "y":
            return self.y
        elif variable == "dimension":
            return self.dimension.name
    
    def load_save_data(self, save_data):
        """Load player data from a save dictionary"""
        try:
            # Load basic player info
            if "name" in save_data:
                self.name = save_data["name"]
            
            # Load UUID
            if "uuid" in save_data:
                self.uuid = save_data["uuid"]
            
            # Load position data
            if "position" in save_data:
                position = save_data["position"]
                if "x" in position:
                    self.x = position["x"]
                if "y" in position:
                    self.y = position["y"]
                if "dimension" in position:
                    # Load the dimension object
                    dim_name = position["dimension"]
                    self.dimension = Dimension(dim_name)
            
            # Load discoveries
            if "discoveries" in save_data:
                discoveries = save_data["discoveries"]
                # Load known dimensions
                if "known_dimensions" in discoveries:
                    self.known_dimensions = discoveries["known_dimensions"]
                # Load discovered celestial bodies
                if "known_bodies" in discoveries:
                    self.known_bodies = discoveries["known_bodies"]
            
            # Load creation date
            if "creation_date" in save_data:
                self.creation_date = save_data["creation_date"]
            
            # Load last login time
            if "last_login" in save_data:
                self.last_login = save_data["last_login"]
                
            # Load player status
            if "is_dead" in save_data:
                self.is_dead = save_data["is_dead"]
            
            # Load docked status if it exists
            if "docked_at" in save_data and save_data["docked_at"]:
                from station import STATIONS, get_station_by_id
                station_id = save_data["docked_at"]
                station = get_station_by_id(station_id)
                if station:
                    self.docked_at = station
                else:
                    print(f"Warning: Could not find station with ID {station_id}")
            
            # Load landed status if it exists
            if "landed_on" in save_data and save_data["landed_on"]:
                self.landed_on = save_data["landed_on"]
                
            # Load parent body for landing if it exists
            if "landed_on_body" in save_data and save_data["landed_on_body"]:
                self.landed_on_body = save_data["landed_on_body"]
                
            # Load parent moon for landing if it exists
            if "landed_on_moon" in save_data and save_data["landed_on_moon"]:
                self.landed_on_moon = save_data["landed_on_moon"]
            
            return True  # Successfully loaded save data
        except Exception as e:
            print(f"Error loading save data: {e}")
            return False  # Failed to load save data
    
    def get_save_data(self):
        """Get player data to save"""
        data = {
            "name": self.name,
            "uuid": self.uuid,
            "position": {
                "x": self.x,
                "y": self.y,
                "dimension": self.dimension.name
            },
            "discoveries": {
                "known_dimensions": self.known_dimensions,
                "known_bodies": self.known_bodies
            },
            "creation_date": self.creation_date,
            "last_login": self.last_login,
            "is_dead": self.is_dead,
            "landed_on": self.landed_on,
            "landed_on_body": self.landed_on_body,
            "landed_on_moon": getattr(self, "landed_on_moon", None)
        }
        
        # Save docked status
        if self.docked_at:
            # Find station id
            station_id = None
            for sid, station in STATIONS.items():
                if station is self.docked_at:
                    station_id = sid
                    break
                    
            # Make sure we found a station ID
            if station_id:
                data["docked_at"] = station_id
            else:
                # Fallback: create a temporary ID based on station properties
                temp_id = f"{self.dimension.name}_{self.docked_at.name}".lower().replace(' ', '_')
                data["docked_at"] = temp_id
                print(f"Warning: Station ID not found, using generated ID: {temp_id}")
        else:
            data["docked_at"] = None
                
        return data
