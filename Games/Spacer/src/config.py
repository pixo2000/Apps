"""
Global configuration settings and constants for the Spacer game.
"""

# Game metadata
VERSION = "0.0.2-BETA" # not used anywhere
GAME_TITLE = "SPACER - EXPLORE AND DIE"

# Player settings
DEFAULT_START_POSITION = {"x": 60, "y": -59}  # Coordinates of Wiesbaden on Earth
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

# Scanning and detection configurations
DEFAULT_SCAN_RANGE = 60
STARS_ALWAYS_VISIBLE = True  # Stars are always visible regardless of discovery status

# Dangerous celestial body types and safety settings
DANGEROUS_BODY_TYPES = ["Star", "Black Hole", "Pulsar"]
DANGER_WARNING_DISTANCE = 15  # Distance at which to warn about dangerous celestial bodies

# Special hidden coordinates
HIDDEN_SIGNALS = {
    "A01": {  # Dimension name
        "Voyager 1": {"x": 2345, "y": -1477, "description": "Ancient Earth probe, requires close proximity for identification"}  # Special hidden signal
    }
}

# Warp paths between star systems
# Each key is a dimension that can warp to the dimensions in its value list
WARP_PATHS = {
    "A01": ["C12", "D14", "N09", "F27"],  # Added F27 (The Great Void)
    "C12": ["A01", "D14", "E15", "G33"],  # Added G33 (Tau Ceti)
    "D14": ["A01", "C12", "C21", "E23"],  # Added E23 (Binary Haven)
    "N09": ["A01", "E15", "E05"],         # Added E05 (Pulsar PSR-E05)
    "C21": ["D14"],                      # From Proxima Centauri you can warp to Sirius
    "E15": ["N09", "C12"],               # From Barnard's Star you can warp to Caliban or Alpha Centauri
    "F27": ["A01"],                      # The Great Void can only warp to Sol
    "G33": ["C12"],                      # Tau Ceti can only warp to Alpha Centauri
    "E23": ["D14"],                      # Binary Haven can only warp to Sirius
    "E05": ["N09"]                       # Pulsar PSR-E05 can only warp to Caliban
}
