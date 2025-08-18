"""
Main command router for player inputs.
"""
import time
from src.commands.registry import cmd_registry
from src.commands.station_commands import handle_station_input, handle_planet_input
from src.core.save_manager import SaveManager

# Create save manager instance
save_mgr = SaveManager()

# Track if commands have been initialized
_commands_initialized = False

def initialize_commands():
    """Load all commands into the registry, but only on first run"""
    global _commands_initialized
    
    if not _commands_initialized:
        # Only load commands the first time
        cmd_registry.registered_aliases = set()
        cmd_registry.load_all_commands()
        _commands_initialized = True

def handle_input(player):
    """Process player commands and execute appropriate actions"""
    # Check if player is docked at a station
    if player.docked_at:
        return handle_station_input(player)
    
    # Check if player is landed on a planet
    if player.landed_on:
        return handle_planet_input(player)
    
    # Don't accept commands if player is dead
    if player.is_dead:
        print("\n☠ You are deceased. Game over.")
        return "negative"
        
    # Get the raw user input (without converting to lowercase)
    user_input = input(f"\n[{player.position('dimension')}:{player.position('x')},{player.position('y')}] {player.name} > ")
    
    # Handle empty input
    if not user_input.strip():
        return "positive"
    
    # Split input into command and arguments
    parts = user_input.split(None, 1)
    command_name = parts[0].lower()
    args = parts[1] if len(parts) > 1 else ""
    
    # Get the command object
    command = cmd_registry.get_command(command_name)
    
    # If command not found
    if not command:
        print(f"\n✗ Unknown command: '{command_name}'. Type 'help' for available commands.")
        return "positive"
    
    # Execute the command
    result = command.execute(player, args)
    
    # Save after every command (only if not already returning "negative" or "logout")
    if result != "negative" and result != "logout":
        save_mgr.save_game(player)
    
    return result
