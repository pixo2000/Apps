"""
Entry point for the Spacer game.
"""
import os
import sys
import time

# Add PyInstaller-friendly resource path function
def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    # Import here to use the resource path function if needed
    from game_core import run_game
    
    try:
        # Create saves directory if it doesn't exist
        saves_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saves")
        os.makedirs(saves_dir, exist_ok=True)
        
        # Run game with debug off for release executable
        run_game("false")
    except Exception as e:
        # Show error and prevent immediate window closing
        print(f"\nCritical error: {e}")
        print("\nPress Enter to exit...")
        input()
        sys.exit(1)
