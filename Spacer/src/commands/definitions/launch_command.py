"""
Launch command for Spacer game.
"""
from src.commands.base_command import BaseCommand

class LaunchCommand(BaseCommand):
    def __init__(self):
        super().__init__(
            name="launch",
            aliases=["undock", "takeoff"],
            description="Launch from a station or planetary surface",
            context_requirements=[],
            error_messages={
                "not_applicable": "You are already in space."
            }
        )
    
    def execute(self, player, args):
        """Execute the launch command"""
        # Check if player is docked at a station
        if player.docked_at:
            print("\nLaunching from station...")
            player.docked_at = None
            print("You have left the station and returned to space.")
            return "positive"
        
        # Check if player is on a planetary surface
        elif player.landed_on:
            city_name = player.landed_on
            body_name = getattr(player, "landed_on_body", "Unknown Body")
            moon_name = getattr(player, "landed_on_moon", None)
            
            display_location = body_name
            if moon_name:
                display_location = f"{moon_name} (Moon of {body_name})"
                
            print(f"\nLaunching from {city_name} on {display_location}...")
            player.landed_on = None
            player.landed_on_body = None
            if hasattr(player, "landed_on_moon"):
                player.landed_on_moon = None
            print("You have successfully returned to orbit.")
            return "positive"
        
        # Not docked or landed
        else:
            print(f"\n✗ {self.error_messages['not_applicable']}")
            return "positive"
