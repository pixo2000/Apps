"""
Surface command handlers for city interactions.
"""
from src.commands.scan_commands import handle_coordinate_scan

def register_surface_commands(command_registry):
    """Register all surface commands"""
    # Add scancoords command to surface command registry
    command_registry["scancoords"] = handle_scancoords_command

def handle_scancoords_command(player, args):
    """Handle scanning coordinates from city surface"""
    # Leverage the existing coordinate scan handler
    handle_coordinate_scan(player, args)
