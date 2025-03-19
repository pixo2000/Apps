"""
Station module for the Spacer game.
Handles station functionality and interactions in console-based interface.
"""

class Station:
    def __init__(self, name, description, x=0, y=0, dimension="SOL"):
        self.name = name
        self.description = description
        self.x = x
        self.y = y
        self.dimension = dimension  # Standardmäßig im SOL-System
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
            print("\nStation Services:")
            for service in ["Trading", "Repairs", "Missions"]:
                print(f"- {service}")
            return True
        
        return False  # Command not handled by station

# Pre-defined stations
STATIONS = {
    "alpha": Station("Alpha Dock", "A small trading outpost on the frontier", 10, 15, "SOL"),
    "beta": Station("Beta Station", "A scientific research facility", -20, 30, "SOL"),
    "gamma": Station("Gamma Hub", "A bustling commerce center", 50, -25, "SOL"),
    # Füge die Stationen hinzu, die im SOL-System-Scan angezeigt werden
    "solar": Station("SolarStation", "Central solar observation station", 8, 2, "A01"),
    "navbeacon": Station("NavBeacon", "Primary navigation beacon for the Sol system", 8, -2, "A01")
}

def get_station_at_coords(x, y):
    """Check if there's a station at the given coordinates"""
    for station_id, station in STATIONS.items():
        if station.x == x and station.y == y:
            return station
    return None
