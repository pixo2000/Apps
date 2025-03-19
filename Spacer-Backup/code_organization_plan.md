# Spacer Code Reorganization Plan

## Current Structure
- `save_manager.py`: Save/load game, player name validation, date formatting
- `player.py`: Player entity, movement mechanics, dimension jumping
- `player_input.py`: Command handling, scanning, help display
- `player_functions.py`: Additional player functionality (scanning)
- `dimension.py`: Dimension loading and management
- `main.py`: Game initialization and main loop

## Proposed Structure

### 1. Core Game Modules

#### `game_core.py`
- Game initialization
- Main game loop
- Session management

#### `config.py`
- Constants and configurations
- Version information
- Game settings

### 2. Data Management

#### `save_manager.py`
- Game state saving and loading
- Player registration and validation
- Metadata handling
- Date/time formatting and parsing

#### `data_loader.py`
- Dimension loading
- Universe data management
- Resource loading

### 3. Player System

#### `player.py`
- Player class with core attributes
- Position and state tracking
- Player metadata (UUID, creation date, etc.)

#### `player_actions.py`
- Movement mechanics
- Dimension jumping
- Player status changes

### 4. Scanning and Discovery

#### `scanner.py`
- System scanning functionality
- Celestial body detection
- Discovery tracking
- Distance calculations

#### `discoveries.py`
- Tracking known objects
- Discovery records
- Exploration progress

### 5. User Interface

#### `command_handler.py`
- Command parsing
- Input validation
- Command execution

#### `ui_display.py`
- Help menu
- Loading animations
- Status displays
- Formatted output

### 6. World Definition

#### `dimension.py`
- Dimension class
- Celestial body definitions
- System properties

## Function Mapping

### Save & Load Functions
- `SaveManager.save_game` → `save_manager.py`
- `SaveManager.load_game` → `save_manager.py`
- `SaveManager.player_exists` → `save_manager.py` 
- `Player.load_save_data` → `save_manager.py`

### Player Core Functions
- `Player` class and attributes → `player.py`
- `Player.change_name` → `player.py`
- `Player.kill` → `player.py`
- `Player.position` → `player.py`

### Movement & Navigation Functions
- `Player.move` → `player_actions.py`
- `Player.jump` → `player_actions.py`

### Scanning Functions
- `scan_system` → `scanner.py`
- `scan_celestial_body` → `scanner.py`
- `handle_scan` → `scanner.py`

### UI and Display Functions
- `display_help` → `ui_display.py`
- `display_discoveries` → `ui_display.py`
- `display_other_player_info` → `ui_display.py`
- Custom loading bars → `ui_display.py`

### Command Functions
- `handle_input` → `command_handler.py`
- Command parsing → `command_handler.py`

## Implementation Strategy
1. Create the new module files
2. Move related functions to their new locations
3. Update imports between modules
4. Test functionality after each module's migration
5. Remove deprecated code and comments
6. Add proper documentation

## Additional Improvements
- Add metadata versioning to saved games
- Improve scan range for dimension C12
- Add navigation beacon display on stars when scanning
- Implement player registration with closed beta access codes
- Create "stop" command for canceling movements
- Enable commands while moving
- Improve pathing algorithm
- Add special hidden signal for Voyager 1
