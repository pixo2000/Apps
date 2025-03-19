import time
from dimension import Dimension

class Player:
    def __init__(self, name):
        self.name = name
        self.x = 10
        self.y = 10
        self.dimension = Dimension('A01')
        self.known_dimensions = ["A01"]  # Start mit der ersten Dimension als bekannt
        self.known_bodies = {}  # Dictionary für entdeckte Himmelskörper nach Dimension
        self.uuid = None  # Wird beim Speichern festgelegt
        self.creation_date = None  # Wird in main.py gesetzt
        self.playtime = 0  # Spielzeit in Sekunden
        self.last_login = None  # Wird beim Speichern aktualisiert
        self.is_dead = False  # Lebensstatus des Spielers
    
    def move(self, x, y):
        # Calculate the distance (maximum of x or y difference for diagonal movement)
        distance = max(abs(x - self.x), abs(y - self.y))
        
        if distance == 0:
            print("\n✓ Already at the requested coordinates.\n")
            return
            
        print(f"\n➤ Setting course to coordinates [{x}, {y}]")
        
        # Show countdown and wait for each field
        for remaining in range(distance, 0, -1):
            progress = distance - remaining
            bar_length = 30
            
            # Calculate percentage for positioning
            percent = (progress / distance) * 100
            
            # For the final step (approaching 100%), ensure the ship is at the very end
            if remaining == 1:
                ship_position = bar_length - 1  # Place at the very end for final step
            else:
                # Otherwise calculate normal position
                ship_position = int((progress / distance) * bar_length)
            
            # Ensure ship position is within valid range
            ship_position = min(max(0, ship_position), bar_length - 1)
            
            # Create the spacebar with the ship at the correct position
            spacebar = "·" * ship_position + "🚀" + "·" * (bar_length - ship_position - 1)
            
            # Calculate percentage (fixed to avoid showing multiple percentages)
            display_percent = int(percent)
            
            # Add extra buffer space to ensure previous output is completely overwritten
            buffer_space = " " * 40
            
            # Display improved movement animation with spaceship
            if remaining > 1:
                print(f"\r[{spacebar}] Moving... {remaining} seconds remaining [{display_percent}%]{buffer_space}", end="", flush=True)
                time.sleep(0.8)
            else:
                print(f"\r[{spacebar}] Moving... Final approach [{display_percent}%]{buffer_space}", end="", flush=True)
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

    def jump(self, dimension_name):
        try:
            new_dimension = Dimension(dimension_name)
            print(f"\n▼ DIMENSIONAL JUMP SEQUENCE INITIATED ▼")
            print(f"➤ Target: {new_dimension.title}")
            print(f"➤ Preparing and calibrating jump engines...")
            
            # Replace tqdm with custom loading bar
            total_steps = 100
            bar_width = 40
            
            for step in range(total_steps + 1):
                # Calculate progress
                progress = step / total_steps
                bar_filled = int(bar_width * progress)
                bar_empty = bar_width - bar_filled
                
                # Create loading bar with customized appearance (similar to tqdm '░▒█')
                bar = '█' * bar_filled + '▒' * bar_empty
                percent = int(progress * 100)
                
                # Print loading bar with "Charging" prefix
                print(f"\rCharging [" + bar + f"] {percent}%", end="", flush=True)
                time.sleep(0.1)
            print()  # Line break after loading completes

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
            
            print(f"\n\n✓ JUMP COMPLETE")
            print(f"\n== Welcome to {new_dimension.title} ==")
            print(f"» {new_dimension.description}")
            print(f"» Starting coordinates: [10, 10]\n")
            
        except ValueError as e:
            print(f"\n✗ JUMP FAILED: {str(e)}\n")
    
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
            
            # Load playtime (handled in main.py)
            
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
