"""
Player class with core attributes and state tracking.
"""
import uuid
from dimension import Dimension
from config import DEFAULT_START_POSITION, DEFAULT_START_DIMENSION

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
            
            return True  # Successfully loaded save data
        except Exception as e:
            print(f"Error loading save data: {e}")
            return False  # Failed to load save data
