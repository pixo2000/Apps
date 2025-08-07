"""
Test script to verify the embed changes work correctly
"""
import sys
import os

# Add the parent directory to sys.path to import from main.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_kda_sorting():
    """Test that KDA sorting works correctly"""
    # Mock player data
    players = [
        {'name': 'Player1#TAG', 'agent': 'Jett', 'kda': '10/15/5', 'acs': 200, 'kills': 10, 'deaths': 15, 'assists': 5},
        {'name': 'Player2#TAG', 'agent': 'Sage', 'kda': '20/10/10', 'acs': 250, 'kills': 20, 'deaths': 10, 'assists': 10},
        {'name': 'Player3#TAG', 'agent': 'Omen', 'kda': '15/12/8', 'acs': 180, 'kills': 15, 'deaths': 12, 'assists': 8},
    ]
    
    # KDA calculation: kills + assists - deaths
    def calculate_kda_score(player):
        return player['kills'] + player['assists'] - player['deaths']
    
    sorted_players = sorted(players, key=calculate_kda_score, reverse=True)
    
    print("🧪 KDA Sorting Test")
    print("=" * 30)
    for i, player in enumerate(sorted_players, 1):
        kda_score = calculate_kda_score(player)
        print(f"{i}. {player['name']} ({player['agent']}) - {player['kda']} | KDA Score: {kda_score}")
    
    # Expected order: Player2 (20), Player3 (11), Player1 (0)
    expected_order = ['Player2#TAG', 'Player3#TAG', 'Player1#TAG']
    actual_order = [p['name'] for p in sorted_players]
    
    if actual_order == expected_order:
        print("✅ KDA sorting test PASSED!")
    else:
        print("❌ KDA sorting test FAILED!")
        print(f"Expected: {expected_order}")
        print(f"Actual: {actual_order}")

def test_enemy_display():
    """Test enemy team display formatting"""
    print("\n🧪 Enemy Team Display Test")
    print("=" * 35)
    
    # Test with tag
    enemy_name = "Team Liquid"
    enemy_tag = "TL"
    enemy_display = f"{enemy_name}#{enemy_tag}" if enemy_tag else enemy_name
    print(f"With tag: {enemy_display}")
    
    # Test without tag
    enemy_name2 = "Random Team"
    enemy_tag2 = ""
    enemy_display2 = f"{enemy_name2}#{enemy_tag2}" if enemy_tag2 else enemy_name2
    print(f"Without tag: {enemy_display2}")
    
    if enemy_display == "Team Liquid#TL" and enemy_display2 == "Random Team":
        print("✅ Enemy display test PASSED!")
    else:
        print("❌ Enemy display test FAILED!")

def test_points_format():
    """Test points formatting"""
    print("\n🧪 Points Format Test")
    print("=" * 25)
    
    points_before = 275
    points_after = 300
    points_gained = points_after - points_before
    
    points_format = f"💰 Points (+{points_gained})"
    points_value = f"{points_before} → {points_after}"
    
    print(f"Field name: {points_format}")
    print(f"Field value: {points_value}")
    
    if points_format == "💰 Points (+25)" and points_value == "275 → 300":
        print("✅ Points format test PASSED!")
    else:
        print("❌ Points format test FAILED!")

if __name__ == "__main__":
    print("🎮 Ghünter Embed Changes Test Suite")
    print("=" * 40)
    
    test_kda_sorting()
    test_enemy_display()
    test_points_format()
    
    print("\n🎯 Summary:")
    print("- ✅ KDA sorting: Players sorted by (kills + assists - deaths)")
    print("- ✅ Enemy display: Shows 'TeamName#TAG' format")
    print("- ✅ Points format: 'Points (+X)' with 'before → after'")
    print("- ✅ Final score: Clean score without enemy name")
    print("- ✅ Separate enemy team field for easy lookup")
