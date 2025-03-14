# File Structure

This document explains the organization of files in the Spacer project.

## Core Files

| File | Purpose |
|------|---------|
| `main.py` | The entry point for the game, handles initialization and the main game loop |
| `player.py` | Defines the Player class with core player functionality |
| `player_functions.py` | Contains player-related functions like scanning systems |
| `player_input.py` | Processes player commands and routes to appropriate handlers |
| `dimension.py` | Manages dimension loading and provides access to celestial bodies |
| `save_manager.py` | Handles saving and loading player data |

## Data Files

| File/Directory | Purpose |
|----------------|---------|
| `dimensions/` | Directory containing JSON files for each dimension |
| `dimensions/*.json` | Individual dimension data files with celestial body information |
| `dimensions.json` | Configuration file listing enabled dimensions |
| `saves/` | Directory containing player save files |

## Documentation Files

| File/Directory | Purpose |
|----------------|---------|
| `docs/` | Main documentation directory |
| `docs/players/` | Documentation for players |
| `docs/developers/` | Documentation for developers |
| `idea.md` | Original game concept notes |
| `notes.md` | Development notes and TODOs |

## Save File Structure

Save files are stored in the `saves` directory with the following naming convention:

```
{player-uuid}.json
```

Each save file contains:

```json
{
    "name": "PlayerName",
    "uuid": "player-unique-id",
    "position": {
        "x": 10,
        "y": 10,
        "dimension": "A01"
    },
    "discoveries": {
        "known_dimensions": ["A01", "B03"],
        "known_bodies": {
            "A01": ["Sun", "Earth", "Mars"],
            "B03": ["Alpha Centauri"]
        }
    },
    "playtime": "00:02:34:12",
    "creation_date": "16.09.22 - 15:30",
    "last_login": "18.09.22 - 20:15",
    "is_dead": false
}
```

## Dimension File Structure

Dimension files are stored in the `dimensions` directory with the name matching the dimension ID:

```
A01.json
```

The structure of a dimension file is:

```json
{
    "A01": {
        "title": "Sol System",
        "description": "Our home solar system",
        "bodies": {
            "Sun": {
                "type": "Star",
                "Coordinates": {"x": "0", "y": "0"},
                "size": {"width": "10", "height": "10"}
            },
            "Earth": {
                "type": "Planet",
                "Coordinates": {"x": "25", "y": "25"},
                "size": {"width": "5", "height": "5"},
                "Moons": {
                    "Moon": {
                        "type": "Moon",
                        "Coordinates": {"x": "27", "y": "25"},
                        "size": {"width": "2", "height": "2"}
                    }
                }
            }
        }
    }
}
```

## Directory Structure Overview

```
spacer/
├── dimensions/            # Dimension data files
│   ├── A01.json
│   ├── B03.json
│   └── ...
├── docs/                  # Documentation
│   ├── players/           # Player docs
│   └── developers/        # Developer docs
├── saves/                 # Player save files
│   └── *.json
├── main.py                # Entry point
├── player.py              # Player class
├── player_functions.py    # Player-related functions
├── player_input.py        # Command processing
├── dimension.py           # Dimension handling
├── save_manager.py        # Save/load functionality
├── dimensions.json        # Dimension configuration
├── idea.md                # Concept notes
└── notes.md               # Development notes
```
