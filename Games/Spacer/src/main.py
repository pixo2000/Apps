"""
Main entry point for the Spacer game.
"""
from src.commands.surface_commands import register_surface_commands

def initialize_commands(command_registry):
    """Initialize all game commands"""
    # Register surface commands
    register_surface_commands(command_registry)