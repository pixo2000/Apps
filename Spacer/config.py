"""
Global configuration settings and constants for the Spacer game.
"""

# Game metadata
VERSION = "0.9.0"
GAME_TITLE = "SPACER - INTERSTELLAR EXPLORATION SIMULATOR"

# Player settings
DEFAULT_START_POSITION = {"x": 60, "y": -60}  # Coordinates of Wiesbaden on Earth
DEFAULT_START_DIMENSION = "A01"
DEFAULT_SCAN_RANGE = 60  # Maximum identifiable distance for scans
DEFAULT_START_LANDED = True
DEFAULT_START_CITY = "Wiesbaden"
DEFAULT_START_BODY = "Earth"
DEFAULT_START_MOON = None

# File paths
SAVE_DIRECTORY = "saves"
DIMENSIONS_DIRECTORY = "dimensions"
DIMENSIONS_CONFIG = "dimensions.json"

# Game UI settings
LOADING_BAR_LENGTH = 40
ANIMATION_SPEED = 0.1
MOVEMENT_SPEED = 0.8

# Reserved system names that cannot be used for players
RESERVED_NAMES = ["new", "exit", "quit", "logout", "help"]

# Player name pattern requirements
NAME_MIN_LENGTH = 3
NAME_MAX_LENGTH = 15
NAME_PATTERN = r'^[a-zA-Z0-9_]{3,15}$'

# Special hidden coordinates
HIDDEN_SIGNALS = {
    "A01": {  # Dimension name
        "Voyager 1": {"x": 2345, "y": -1477}  # Special hidden signal
    }
}
