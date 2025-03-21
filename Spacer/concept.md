# Spacer - Interstellar Exploration Simulator

## Project Structure & Architecture

The Spacer game will be restructured with a modular design pattern, separating concerns into individual directories:

```
Spacer/
├── main.py               # Entry point (stays in root)
└── src/
    ├── core/            # Core game functionality
    │   ├── game_core.py
    │   ├── player.py
    │   └── save_manager.py
    ├── commands/        # Split command handler
    │   ├── command_manager.py    # Main command router
    │   ├── navigation.py         # Movement related commands
    │   ├── scan_commands.py      # Scanning related commands
    │   ├── station_commands.py   # Station interaction commands
    │   └── player_commands.py    # Player info/management commands
    ├── world/           # Game world elements
    │   ├── dimension.py
    │   ├── station.py
    │   └── scanner.py
    ├── utils/           # Utility modules
    │   ├── data_loader.py
    │   └── ui_display.py
    └── config.py        # Configuration (moved to src)
```

## File Migrations

### Core Modules
- `game_core.py` → `src/core/game_core.py`
- `player.py` → `src/core/player.py`
- `save_manager.py` → `src/core/save_manager.py`

### Command Modules (Split from command_handler.py)
- Create new `src/commands/command_manager.py` as the main router
- `src/commands/navigation.py` - Extract movement, jump, and coordinate commands
- `src/commands/scan_commands.py` - Extract scanning functionality
- `src/commands/station_commands.py` - Extract station and landing commands
- `src/commands/player_commands.py` - Extract player information commands

### World Modules
- `dimension.py` → `src/world/dimension.py`
- `station.py` → `src/world/station.py`
- `scanner.py` → `src/world/scanner.py`

### Utility Modules
- `data_loader.py` → `src/utils/data_loader.py`
- `ui_display.py` → `src/utils/ui_display.py` 
- `player_actions.py` → Split between `src/commands/navigation.py` and other modules

### Configuration
- `config.py` → `src/config.py`

## Core Game Loop

1. Player initialization (new game or load save)
2. Main game loop:
   - Process player input through command manager
   - Route to appropriate command handler
   - Execute actions
   - Update game state
   - Save progress
3. Game termination (exit or logout)

## Key Features

### Dimension System
- Multiple star systems with unique properties
- Dynamic loading of dimension data from JSON files
- Dimensional travel mechanics

### Celestial Body Exploration
- Planets, moons, stations, and hidden signals
- Surface landing and exploration
- Scanning and discovery mechanics

### Station Interactions
- Docking at space stations
- Station-specific interfaces and commands
- City landing and exploration

### Persistence
- Save/load game state
- Player profile management
- Progress tracking across sessions

## Future Development

- GUI implementation for enhanced visual experience
- Ship customization and upgrades
- Server-side functionality for multiplayer features
- Hardware ID verification for security
- Interactive map system
- Command improvements:
  - Abort command during execution
  - Command queuing system
  - Commands while moving
- Enhanced movement and navigation systems
- Code redemption system for special content
- Version management and release system

## Technical Improvements

- Add keybinds via task to build and run main
- Fix disconnection issues
- Better debugging (clear on first start but not restart/crash)
- Station info should have coordinates, type, and more details
- Implement metadata to ensure version compatibility
- Save game state after each command/send to server
- Test build process and fix symbols
- Improve scanning functionality
  - Sun should be discoverable by default
  - Scan coordinates with move range
  - Show navigation beacon on star when scanning

## Code Cleanup

**Note: 90% of existing notes should be removed as they consist of temporary development reminders or outdated concepts.**

- Remove not needed code
- Remove excessive comments
- Split command manager for better maintainability
- Create proper registration system with code (for closed beta)

The project follows a text-based command interface but is designed with extensibility in mind for potential GUI implementation in the future. The modular architecture supports adding new features without major refactoring.