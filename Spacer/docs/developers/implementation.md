# Implementation Details

This document describes the specific implementation details and design decisions in Spacer.

## Player System

### Player Identification

Players are identified by both name and UUID:
- Names are user-facing and can be changed
- UUIDs are permanent and used for save files
- This allows name changes without losing save data

```python
def __init__(self, name):
    self.name = name
    self.uuid = str(uuid.uuid4())  # Generate unique UUID for new player
    # ...
```

### Movement System

Movement uses Chebyshev distance (maximum of X or Y difference):
- This allows diagonal movement in the same time as straight movement
- Each unit takes one second of game time

```python
def move(self, x, y):
    # Calculate the distance (maximum of x or y difference for diagonal movement)
    distance = max(abs(x - self.x), abs(y - self.y))
    # ...
```

### Dimension Jumping

Dimension jumping resets player coordinates and updates their known dimensions:

```python
def jump(self, dimension_name):
    # ...
    self.dimension = new_dimension
    self.x = 10
    self.y = 10
    
    # Mark dimension as discovered if it's new
    if dimension_name not in self.known_dimensions:
        self.known_dimensions.append(dimension_name)
        self.known_bodies[dimension_name] = []
    # ...
```

## Scanning System

The scanning system uses distance calculations to determine what information is available:

```python
def scan_system(player):
    # ...
    # Determine if body should be identified (if it's close enough or already known)
    if movement_distance <= 60 or body_name in player.known_bodies.get(dimension_name, []):
        # Body is close enough to identify or already known
        # ...
    else:
        # Limited information for distant bodies (only coordinates are known)
        # ...
```

Key features:
- Bodies within 60 units are fully identified
- Previously discovered bodies are always identified
- Unknown bodies show only coordinates and distance

## Save System

### File Structure

Save files are stored as JSON with the player's UUID as the filename:

```python
def save_game(self, player):
    # ...
    # Use the UUID for the filename instead of the player name
    save_path = self.save_directory / f"{player.uuid}.json"
    # ...
```

### Data Format

The save data includes:
- Basic player info (name, UUID)
- Position data (x, y, dimension)
- Discovery data (known dimensions and bodies)
- Meta data (playtime, creation date, last login)
- Status data (is_dead)

### Playtime Tracking

Playtime is tracked across sessions:
- Stored in a formatted string (dd:hh:mm:ss)
- Parsed back to seconds for calculations
- Updated at logout/game exit

## Input Processing

The command system uses a case-insensitive approach for command detection:

```python
def handle_input(name):
    # ...
    # Get the raw user input (without converting to lowercase)
    user_input = input(f"\n[{name.position('dimension')}:{name.position('x')},{name.position('y')}] {name.name} > ")
    
    # Create a lowercase version for command detection only
    command_lower = user_input.lower()
    # ...
```

This allows preserving case for parameters while making commands case-insensitive.

## Dimension System

Dimensions are loaded from JSON files with a standardized structure:

```python
def load_dimension(self):
    # ...
    with open(file_path, 'r') as f:
        dimension_data = json.load(f)
        if self.name in dimension_data:
            dimension_data = dimension_data[self.name]
            self.title = dimension_data['title']
            self.description = dimension_data['description']
            self.properties = {}
            # Store celestial bodies as properties
            for body_name, body_data in dimension_data['bodies'].items():
                self.properties[body_name] = body_data
    # ...
```

The system supports:
- Multiple body types (stars, planets, moons, stations)
- Nested structures (planets with moons)
- Coordinate-based positioning
