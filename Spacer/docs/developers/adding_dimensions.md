# Adding Dimensions

This guide explains how to add new dimensions (star systems) to Spacer.

## Dimension File Structure

Each dimension is defined in its own JSON file in the `dimensions` directory. The filename should match the dimension ID (e.g., `A01.json` for dimension A01).

### Basic Structure

```json
{
    "DimensionID": {
        "title": "System Name",
        "description": "Brief description of the system",
        "bodies": {
            // Celestial bodies defined here
        }
    }
}
```

### Example Dimension

Here's an example of a complete dimension file:

```json
{
    "B05": {
        "title": "Epsilon Eridani",
        "description": "A young star system with developing planets",
        "bodies": {
            "Epsilon Eridani": {
                "type": "Star",
                "Coordinates": {"x": "0", "y": "0"},
                "size": {"width": "8", "height": "8"}
            },
            "Aegir": {
                "type": "Planet",
                "Coordinates": {"x": "15", "y": "22"},
                "size": {"width": "4", "height": "4"},
                "Moons": {
                    "Ran": {
                        "type": "Moon",
                        "Coordinates": {"x": "17", "y": "22"},
                        "size": {"width": "1", "height": "1"}
                    }
                }
            },
            "Trading Post Alpha": {
                "type": "Station",
                "Coordinates": {"x": "5", "y": "5"},
                "size": {"width": "2", "height": "2"}
            }
        }
    }
}
```

## Body Types

You can include various types of celestial bodies:

- **Stars**: Central bodies of the system
- **Planets**: Bodies orbiting stars
- **Moons**: Smaller bodies orbiting planets
- **Stations**: Artificial structures

## Body Properties

Each celestial body requires these properties:

| Property | Description | Example |
|----------|-------------|---------|
| `type` | Body type | `"Star"`, `"Planet"`, `"Moon"`, `"Station"` |
| `Coordinates` | X/Y position | `{"x": "10", "y": "15"}` |
| `size` | Width/height | `{"width": "5", "height": "5"}` |

### Optional Properties

- **Moons**: A dictionary of moons orbiting a planet
- **Stations**: A dictionary of stations orbiting a body

## Enabling the Dimension

After creating the dimension file, you need to enable it by adding it to the `dimensions.json` file in the root directory:

```json
{
    "enabled": [
        "A01",
        "B02",
        "B05",  // Your new dimension
        "C12"
    ]
}
```

## Positioning Tips

When designing your dimension, consider these positioning tips:

1. **Central Star**: Place the main star near coordinates (0,0)
2. **Planetary Spacing**: Space planets with reasonable distances (10-30 units)
3. **Moon Placement**: Place moons 2 units away from their parent planet
4. **Station Placement**: Place stations strategically near planets or at waypoints
5. **Scan Range**: Remember that players can only identify bodies within 60 units unless already discovered

## Dimension Naming Convention

Follow these conventions for dimension IDs:

- One letter followed by two digits (e.g., A01, B05, C12)
- The letter indicates the sector (A, B, C, etc.)
- The digits indicate the system number within that sector

## Testing Your Dimension

After adding your dimension:

1. Launch the game
2. Use the `dimensions` command to verify your dimension appears
3. Jump to your dimension with `jump YOURDIMID`
4. Test exploration with `scan` and `move` commands

If your dimension doesn't appear or loads incorrectly, check for JSON syntax errors in your dimension file.
