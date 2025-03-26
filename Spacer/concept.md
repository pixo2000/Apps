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
    ├── commands/        # Command system
    │   ├── registry.py           # Command registration and routing
    │   ├── base_command.py       # Base command class/interface
    │   ├── config/               # Command configurations
    │   │   ├── command_config.py # Configuration loader
    │   │   └── commands/         # Individual command config files (YAML/JSON)
    │   │       ├── jump.yaml
    │   │       ├── scan.yaml
    │   │       └── ...
    │   └── definitions/          # Individual command files
    │       ├── jump.py           # Jump command
    │       ├── scan.py           # Scan command
    │       ├── move.py           # Move command
    │       └── ...
    ├── functions/        # Command implementation functions
    │   ├── navigation_functions.py
    │   ├── scan_functions.py
    │   ├── station_functions.py
    │   └── player_functions.py
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

### Command System (Complete Restructure)
- Create `src/commands/registry.py` for command registration and routing
- Create `src/commands/base_command.py` for command interface/class definition
- Create command configuration system:
  - `src/commands/config/command_config.py` to load and validate configs
  - Individual YAML/JSON files in `src/commands/config/commands/` folder
- Individual command definition files in `src/commands/definitions/`:
  - `jump.py`, `scan.py`, `move.py`, `dock.py`, etc.

### Command Functions
- `src/functions/navigation_functions.py` - Core functions for movement and jumps
- `src/functions/scan_functions.py` - Core functions for scanning operations
- `src/functions/station_functions.py` - Core functions for station interactions
- `src/functions/player_functions.py` - Core functions for player management

### World Modules
- `dimension.py` → `src/world/dimension.py`
- `station.py` → `src/world/station.py`
- `scanner.py` → `src/world/scanner.py`

### Utility Modules
- `data_loader.py` → `src/utils/data_loader.py`
- `ui_display.py` → `src/utils/ui_display.py` 
- `player_actions.py` → Split into appropriate function modules

### Configuration
- `config.py` → `src/config.py`

## Command System Architecture

### Command Definition
Each command is defined in its own file with:
1. Command metadata (name, aliases, description)
2. Argument parsing
3. Validation rules
4. Error message templates
5. Execution context requirements
6. Function references for implementation

Example command definition (jump.py):
```python
from commands.base_command import BaseCommand
from functions.navigation_functions import perform_jump

class JumpCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="jump",
            aliases=["j", "warp"],
            description="Jump to another star system",
            context_requirements=["not_docked", "not_landed", "not_moving"],
            error_messages={
                "not_docked": "Cannot jump while docked at a station",
                "not_landed": "Cannot jump while landed on a planet",
                "not_moving": "Cannot jump while in transit",
                "invalid_coords": "Invalid jump coordinates",
                "out_of_range": "Destination is beyond jump range"
            }
        )
    
    def execute(self, game_state, args):
        # Parse and validate arguments
        if not self.validate_context(game_state):
            return False
            
        # Execute the jump using function from navigation_functions
        return perform_jump(game_state, args)
```

### Command Configuration
Commands are configured via YAML/JSON files:
```yaml
# jump.yaml
name: jump
aliases: 
  - j
  - warp
description: Jump to another star system
help_text: |
  JUMP <x> <y> <z> - Jump to coordinates
  JUMP <system_name> - Jump to named system
context_requirements:
  - not_docked
  - not_landed
  - not_moving
error_messages:
  not_docked: Cannot jump while docked at a station
  not_landed: Cannot jump while landed on a planet
  not_moving: Cannot jump while in transit
  invalid_coords: Invalid jump coordinates
  out_of_range: Destination is beyond jump range
cooldown: 5
```

### Command Registry
The registry loads all commands and provides:
- Command registration
- Command lookup by name/alias
- Context validation
- Help generation
- Tab completion

## Core Game Loop

1. Player initialization (new game or load save)
2. Main game loop:
   - Process player input through command registry
   - Validate execution context
   - Execute appropriate command implementation
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
- Plugin system for custom commands

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
- Create proper registration system with code (for closed beta)

The project follows a text-based command interface but is designed with extensibility in mind for potential GUI implementation in the future. The modular command architecture provides flexibility and maintainability while allowing for easy addition of new commands without major refactoring.