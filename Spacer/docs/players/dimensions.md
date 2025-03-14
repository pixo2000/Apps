# Dimensions Guide

In Spacer, the universe is divided into different dimensions, each representing a unique star system with its own celestial bodies.

## What are Dimensions?

Dimensions in Spacer are separate star systems that you can travel between. Each dimension has:

- A unique identifier (e.g., A01, C12)
- A descriptive name
- A collection of celestial bodies (stars, planets, moons, stations)
- Its own coordinate system

## Dimension Naming

Dimensions are named with a letter followed by two digits:
- The letter indicates the sector (A, B, C, etc.)
- The two digits indicate the specific system within that sector

For example:
- A01: The first system in sector A
- C12: The twelfth system in sector C

## Traveling Between Dimensions

To travel between dimensions, use the `jump` command followed by the dimension name:

```
jump A01
```

When you jump to a new dimension:
1. Your coordinates reset to (10, 10)
2. You'll receive information about the new system
3. The dimension is added to your discovered dimensions list

## Discovering New Dimensions

To see all available dimensions:

```
dimensions
```

This command lists:
- All dimensions you can visit
- Whether you've discovered them or not
- For discovered dimensions, their name and description

## Dimension Coordinate System

Each dimension has its own 2D coordinate system:
- X and Y coordinates can be positive or negative
- Movement uses the Chebyshev distance (maximum of X or Y difference)
- Each unit of distance takes one second to travel

## Tips for Dimensional Travel

- Use `whereami` to check your current dimension
- Use `discoveries` to see which dimensions you've visited
- After jumping to a new dimension, always use `scan` to discover celestial bodies
- Each dimension has unique celestial bodies to discover
