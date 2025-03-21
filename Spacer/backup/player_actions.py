"""
Player movement mechanics and dimension jumping functionality.
"""
import time
from dimension import Dimension
from config import MOVEMENT_SPEED

class PlayerActions:
    @staticmethod
    def move(player, x, y): # animation is here cuz its not static
        """Move the player to specified coordinates"""
        # Calculate the distance (maximum of x or y difference for diagonal movement)
        distance = max(abs(x - player.x), abs(y - player.y))
        
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
            if remaining == 1:
                display_percent = 100  # Always show 100% for the final step
            else:
                display_percent = int(percent)
            
            # Add extra buffer space to ensure previous output is completely overwritten
            buffer_space = " " * 40
            
            # Display improved movement animation with spaceship
            if remaining > 1:
                print(f"\r[{spacebar}] Moving... {remaining} seconds remaining [{display_percent}%]{buffer_space}", end="", flush=True)
                time.sleep(MOVEMENT_SPEED)
            else:
                print(f"\r[{spacebar}] Moving... Final approach [{display_percent}%]{buffer_space}", end="", flush=True)
                time.sleep(MOVEMENT_SPEED)
                
        # Update position
        player.x = x
        player.y = y
        print(f"\n\n✓ Arrived at coordinates [{x}, {y}]\n")

    @staticmethod
    def jump(player, dimension_name):
        """Jump to a different dimension"""
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
                
                # Create loading bar with customized appearance
                bar = '█' * bar_filled + '▒' * bar_empty
                percent = int(progress * 100)
                
                # Print loading bar with "Charging" prefix
                print(f"\rCharging [" + bar + f"] {percent}%", end="", flush=True)
                time.sleep(0.1)
            print()  # Line break after loading completes

            print(f"\n➤ Jump sequence activated! Entering hyperspace...")
            time.sleep(1)
            
            # Animation for the jump
            jump_animation = ["■□□□□", "□■□□□", "□□■□□", "□□□■□", "□□□□■", "□□□■□", "□□■□□", "□■□□□"]
            for _ in range(3):  # 3 cycles of animation
                for frame in jump_animation:
                    print(f"\r▻▻▻ {frame} ◅◅◅", end="", flush=True)
                    time.sleep(0.1)
            
            # Update player state
            player.dimension = new_dimension
            player.x = 10
            player.y = 10
            
            # Add dimension to known dimensions if not already there
            if dimension_name not in player.known_dimensions:
                player.known_dimensions.append(dimension_name)
            
            print(f"\n\n✓ JUMP COMPLETE")
            print(f"\n== Welcome to {new_dimension.title} ==")
            print(f"» {new_dimension.description}")
            print(f"» Starting coordinates: [10, 10]\n")
            
        except ValueError as e:
            print(f"\n✗ JUMP FAILED: {str(e)}\n")
