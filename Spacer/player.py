import time
from dimension import Dimension
import uuid

class Player:
    def __init__(self, name):
        self.name = name
        self.uuid = str(uuid.uuid4())  # Generate unique UUID for new player
        self.x = 10
        self.y = 10
        self.dimension = Dimension('A01')
        self.is_dead = False  # Player's alive status
        
        # Discovery tracking
        self.known_dimensions = ['A01']  # Start with home dimension
        self.known_bodies = {
            'A01': []  # Will store names of known bodies by dimension
        }
    
    def move(self, x, y):
        # Calculate the distance (maximum of x or y difference for diagonal movement)
        distance = max(abs(x - self.x), abs(y - self.y))
        
        if distance == 0:
            print("\n✓ Already at the requested coordinates.\n")
            return
            
        print(f"\n➤ Setting course to coordinates [{x}, {y}]")
        
        # Show countdown and wait for each field
        for i in range(distance + 1):  # +1 to ensure we reach 100%
            progress = i
            bar_length = 30
            
            # Create a dynamic spaceship movement animation
            ship_position = int((progress/distance) * (bar_length-3)) if distance > 0 else bar_length-3
            spacebar = "·" * ship_position + "🚀" + "·" * (bar_length - ship_position - 3)
            percent = int((progress/distance) * 100) if distance > 0 else 100
            
            # Display improved movement animation with spaceship
            if i < distance:
                remaining = distance - i
                line_content = f"[{spacebar}] Moving... {remaining} second{'s' if remaining > 1 else ' '} remaining [{percent}%]"
            else:
                # Final frame shows 100%
                line_content = f"[{spacebar}] Moving... Arrival imminent [100%]"
                
            # Ensure the line is properly cleared with padding
            print(f"\r{line_content}{' ' * 10}", end="", flush=True)
            
            if i < distance:  # Don't sleep after the last frame
                time.sleep(0.8)
                
        # Update position
        self.x = x
        self.y = y
        print(f"\n\n✓ Arrived at coordinates [{x}, {y}]\n")
    
    def position(self, variable):
        if variable == "x":
            return self.x
        elif variable == "y":
            return self.y
        elif variable == "dimension":
            return self.dimension.name
        
    def change_name(self, new_name):
        """Change the player's name"""
        old_name = self.name
        self.name = new_name
        return old_name

    def jump(self, dimension_name):
        try:
            new_dimension = Dimension(dimension_name)
            print(f"\n▼ DIMENSIONAL JUMP SEQUENCE INITIATED ▼")
            print(f"➤ Target: {new_dimension.title}")
            print(f"➤ Preparing and calibrating jump engines...")
            
            # Ladeleiste anzeigen
            loading_bar_length = 30
            for i in range(loading_bar_length + 1):
                bar = '█' * i + '-' * (loading_bar_length - i)
                print(f"\rCharging: [{bar}] {int((i/loading_bar_length) * 100)}%", end="", flush=True)
                time.sleep(0.1)
            print("\nCharging: [██████████████████████████████] 100%")

            print(f"\n➤ Jump sequence activated! Entering hyperspace...")
            time.sleep(1)
            
            # Animation für den Sprung
            jump_animation = ["■□□□□", "□■□□□", "□□■□□", "□□□■□", "□□□□■", "□□□■□", "□□■□□", "□■□□□"]
            for _ in range(3):  # 3 cycles of animation
                for frame in jump_animation:
                    print(f"\r▻▻▻ {frame} ◅◅◅", end="", flush=True)
                    time.sleep(0.1)
            
            self.dimension = new_dimension
            self.x = 10
            self.y = 10
            
            # Mark dimension as discovered if it's new
            if dimension_name not in self.known_dimensions:
                self.known_dimensions.append(dimension_name)
                self.known_bodies[dimension_name] = []
                print(f"\n✓ NEW DIMENSION DISCOVERED: {new_dimension.title}")
            
            print(f"\n\n✓ JUMP COMPLETE")
            print(f"\n== Welcome to {new_dimension.title} ==")
            print(f"» {new_dimension.description}")
            print(f"» Starting coordinates: [10, 10]\n")
            
        except ValueError as e:
            print(f"\n✗ JUMP FAILED: {str(e)}\n")

    def load_save_data(self, save_data):
        """Load player state from save data"""
        if not save_data:
            return False
        
        try:
            # Set position
            self.x = save_data["position"]["x"]
            self.y = save_data["position"]["y"]
            
            # Set current dimension
            dimension_name = save_data["position"]["dimension"]
            self.dimension = Dimension(dimension_name)
            
            # Load discoveries
            self.known_dimensions = save_data["discoveries"]["known_dimensions"]
            self.known_bodies = save_data["discoveries"]["known_bodies"]
            
            # Load dead status if available
            if "is_dead" in save_data:
                self.is_dead = save_data["is_dead"]
            
            # Load UUID if available, otherwise generate one
            if "uuid" in save_data:
                self.uuid = save_data["uuid"]
            else:
                # Generate a new UUID for older save files
                self.uuid = str(uuid.uuid4())
                
            return True
        except Exception as e:
            print(f"Error loading save data: {e}")
            return False

    def kill(self):
        """Set player as dead"""
        self.is_dead = True
        print("\n☠ ☠ ☠ YOU HAVE DIED ☠ ☠ ☠")
        print("Your journey ends here.")
        return "negative"  # Signal to end the game
