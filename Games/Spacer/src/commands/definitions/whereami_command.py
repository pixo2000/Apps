"""
Whereami command for displaying current position and environment.
"""
from src.commands.base_command import BaseCommand
from src.world.station import check_coords_for_objects

class WhereAmICommand(BaseCommand):
    def __init__(self):
        # Lade Konfiguration aus der YAML-Datei
        super().__init__()
    
    def execute(self, player, args):
        """Execute the whereami command"""
        # Get player's current position
        x = player.position("x")
        y = player.position("y")
        dim_name = player.position("dimension")
        
        # Show current position
        print(f"\nYou are at coordinates [{x}, {y}] in dimension {dim_name}.")
        print(f"Dimension name: {player.dimension.title}")
        print(f"Description: {player.dimension.description}")
        
        # Check if there's anything at the current position
        result = check_coords_for_objects(x, y, dim_name, {"bodies": player.dimension.properties})
        
        if result["found"]:
            print("\nAt your current position:")
            for obj in result["objects"]:
                if "parent" in obj and "grandparent" in obj:
                    print(f"- {obj['name']} ({obj['type']}) on {obj['parent']}, Moon of {obj['grandparent']}")
                elif "parent" in obj:
                    print(f"- {obj['name']} ({obj['type']}) on {obj['parent']}")
                else:
                    print(f"- {obj['name']} ({obj['type']})")
        
        # TODO: Add more environmental information here
        
        return "positive"
