# Getting Started with Spacer

Welcome, Captain! This guide will help you take your first steps in the universe of Spacer.

## Starting the Game

Launch the game by running the main script:

```
python main.py
```

## Creating a Captain

When you first start the game, you'll be prompted to create a new captain:

1. Enter a name for your captain when prompted
   - Names must be 3-15 characters long
   - Can contain letters, numbers, and underscores
   - Cannot be reserved words like "new", "exit", etc.

2. Once your captain is created, you'll receive a welcome message and the game will begin

## Understanding Your Interface

After creating or loading a captain, you'll see the command interface:

```
[A01:10,10] YourName >
```

This shows:
- `A01`: Your current dimension
- `10,10`: Your current coordinates (x,y)
- `YourName`: Your captain's name

## Your First Commands

Here are some essential commands to get started:

1. `help` - Display all available commands
2. `scan` - Scan your current system for celestial bodies
3. `move X Y` - Move to coordinates X,Y in the current dimension
4. `whereami` - Get detailed information about your current location

## Your First Exploration

Here's a recommended sequence for your first session:

1. Use `scan` to discover what's in your current system
2. Choose a celestial body from the scan results
3. Use `move X Y` to navigate to its coordinates
4. Use `dimensions` to see what other star systems exist
5. Use `jump X##` to travel to another dimension when ready

## Saving and Exiting

- Your game saves automatically after each command
- Use `logout` to exit to the main menu
- Use `quit` or `exit` to close the game completely

Now you're ready to explore the universe! Good luck, Captain!
