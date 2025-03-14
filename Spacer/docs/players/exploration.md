# Exploration Guide

Exploration is at the heart of Spacer. This guide explains how to discover and track celestial bodies throughout the universe.

## Scanning Systems

The primary way to discover celestial bodies is through the `scan` command:

```
scan
```

When you scan a system, your ship's sensors search for all bodies in the current dimension.

### Scan Results

Scan results show:
- **Type**: The category of the celestial body (star, planet, station, etc.)
- **Name**: The body's name (or "Unknown" if too distant)
- **Coordinates**: The position in the current dimension
- **Distance**: How far away the body is (in seconds of travel time)
- **Signals**: The number of associated objects (moons, stations)
- **Status**: "NEW!" for newly discovered bodies

### Detection Range

- Bodies within 60 units are fully identified
- Bodies beyond 60 units appear as "Unknown"
- Previously discovered bodies are always identified regardless of distance

## Discovery System

As you explore, Spacer tracks your discoveries:

- **Dimensions**: Each dimension you visit is recorded
- **Celestial Bodies**: Each body you discover is logged by dimension

View your discoveries with:

```
discoveries
```

This command displays:
- All dimensions you've visited
- The celestial bodies you've discovered in each dimension

## Celestial Body Types

You may encounter various types of celestial bodies:

- **Stars**: The central body of a system
- **Planets**: Bodies orbiting around stars
- **Moons**: Smaller bodies orbiting planets
- **Stations**: Artificial structures that may orbit planets or exist independently

## Signals

The "Signals" count in scan results indicates:
- Number of moons orbiting a planet
- Number of stations associated with a body

## Travel and Exploration

To explore a celestial body:

1. Use `scan` to discover bodies
2. Find interesting targets in the scan results
3. Use `move X Y` to travel to their coordinates
4. Arriving at the exact coordinates of a body counts as visiting it

## Tips for Efficient Exploration

- Scan immediately after jumping to a new dimension
- Focus on exploring bodies with signals first
- Keep track of your discoveries with the `discoveries` command
- Remember that unknown bodies will be identified when you get within 60 units
