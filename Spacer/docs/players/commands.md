# Command Reference

This document contains a complete reference for all commands available in Spacer.

## Navigation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `move X Y` | Travel to coordinates X,Y in the current dimension | `move 15 20` |
| `whereami` | Display current location information | `whereami` |
| `jump DIM` | Jump to dimension DIM | `jump A01` |
| `dimensions` | List all available dimensions | `dimensions` |

## Exploration Commands

| Command | Description | Example |
|---------|-------------|---------|
| `scan` | Scan current system for celestial bodies | `scan` |
| `discoveries` | Display all your discovered bodies and dimensions | `discoveries` |

## Player Commands

| Command | Description | Example |
|---------|-------------|---------|
| `playerinfo` | Display your player information | `playerinfo` |
| `playerinfo NAME` | Display information about another player | `playerinfo OtherCaptain` |
| `changename NAME` | Change your captain's name | `changename NewName` |

## System Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Display all available commands | `help` |
| `logout` | Save and return to the login screen | `logout` |
| `quit` or `exit` | Exit the game | `quit` |
| `self-destruct` | Permanently end your captain's journey | `self-destruct` |

## Command Details

### Movement

The `move` command uses Chebyshev distance, which means diagonal movement takes the same time as horizontal or vertical movement of the same distance. The time to travel equals the distance in seconds.

### Scanning

When you scan a system:
- Bodies within 60 units will be identified by name
- Bodies beyond 60 units appear as "Unknown"
- Already discovered bodies are always identified regardless of distance
- Each scan shows the body's type, coordinates, distance, and number of signals (moons and stations)

### Dimensions

Dimensions are named with a letter followed by two digits (e.g., A01, C12).
Each dimension represents a different star system with its own celestial bodies.

### Player Information

The `playerinfo` command shows:
- Player name and UUID
- Current location
- Dimensions visited
- Bodies discovered
- Total playtime
- Creation date and last login
