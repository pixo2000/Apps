# Code Overview

This document provides a high-level overview of Spacer's code architecture and main components.

## Core Components

Spacer is structured around several key components:

1. **Player System**: Handles player state, movement, and actions
2. **Dimension System**: Manages dimensions, celestial bodies, and their properties
3. **Command Interface**: Processes user input and executes corresponding actions
4. **Save System**: Handles saving and loading player progress

## Main Files and Their Functions

| File | Description |
|------|-------------|
| `main.py` | Entry point that handles game initialization and the main game loop |
| `player.py` | Defines the Player class with movement and interaction capabilities |
| `player_functions.py` | Contains specialized player functions like scanning |
| `player_input.py` | Processes and routes player commands |
| `dimension.py` | Manages dimension data and celestial bodies |
| `save_manager.py` | Handles saving/loading of player data |

## Execution Flow

The game follows this general execution flow:

1. `main.py` initializes the game and creates/loads a player
2. The main loop repeatedly:
   - Gets user input via `player_input.py`
   - Processes commands and updates game state
   - Autosaves after each command
3. When the player logs out or quits, their progress is saved

## Key Classes

### Player Class

The `Player` class in `player.py` is the central entity representing the player. It handles:
- Movement through coordinates
- Dimension jumping
- Tracking discoveries
- Player state (position, name, alive status)

### Dimension Class

The `Dimension` class in `dimension.py` manages star systems and their contents:
- Loading dimension data from JSON files
- Storing celestial body properties
- Providing access to dimension metadata

### SaveManager Class

The `SaveManager` class in `save_manager.py` handles all persistence operations:
- Saving player state to JSON files
- Loading player data
- Managing player metadata
- Validating player names

## Data Flow

1. Player input → Command processing → Game state changes
2. Game state changes → Autosave → Updated save file
3. Dimension data (JSON) → Dimension objects → Game world representation

## Dependencies

Spacer uses minimal external dependencies:
- `json`: For data storage and parsing
- `os` and `pathlib`: For file operations
- `datetime`: For tracking time and dates
- `tqdm` (optional): For progress bar animations

## Extension Points

The main extension points for adding features are:
- New commands in `player_input.py`
- New player functions in `player_functions.py`
- New dimension data in the `dimensions` folder
