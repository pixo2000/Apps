import requests
import os
import time
import json
import sys
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv('./.env')

# Get API key and webhook URL from environment
api_key = os.getenv('HDEV_API_KEY')
webhook_url = os.getenv('WEBHOOK_URL')

# Debug: Check if environment variables are loaded
if not api_key:
    print("❌ API key not found in environment variables")
else:
    print(f"✅ API key loaded: {api_key[:10]}...")

if not webhook_url:
    print("❌ Webhook URL not found in environment variables")
else:
    print("✅ Webhook URL loaded")

# Track the last known match ID to detect new matches
last_known_match_id = None

def get_team_history():
    """Get the team's match history from the API"""
    try:
        response = requests.get(
            "https://api.henrikdev.xyz/valorant/v1/premier/carings baes/carba/history",
            headers={"Authorization": api_key, "Accept": "*/*"},
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting history: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching history: {e}")
        return None

def get_latest_league_match_id(history_data):
    """Extract the latest league match ID from history data"""
    if not history_data or history_data.get('status') != 200:
        return None
    
    league_matches = history_data.get('data', {}).get('league_matches', [])
    if not league_matches:
        return None
    
    # Sort by date to get the most recent
    def parse_date(match):
        try:
            date_str = match.get('started_at', '')
            if not date_str:
                return datetime.min.replace(tzinfo=timezone.utc)
            
            # Handle different date formats and ensure timezone awareness
            if date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            
            # Fix microseconds format - pad to 6 digits if needed
            if '+' in date_str or '-' in date_str[-6:]:
                # Split at timezone
                if '+' in date_str:
                    dt_part, tz_part = date_str.rsplit('+', 1)
                    tz_part = '+' + tz_part
                else:
                    dt_part, tz_part = date_str.rsplit('-', 1)
                    tz_part = '-' + tz_part
                
                # Fix microseconds in datetime part
                if '.' in dt_part:
                    base_part, micro_part = dt_part.rsplit('.', 1)
                    # Pad microseconds to 6 digits
                    micro_part = micro_part.ljust(6, '0')[:6]
                    date_str = f"{base_part}.{micro_part}{tz_part}"
            
            parsed_date = datetime.fromisoformat(date_str)
            
            # If the datetime is naive (no timezone), assume UTC
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            
            return parsed_date
        except Exception as e:
            print(f"Error parsing date '{match.get('started_at', '')}': {e}")
            return datetime.min.replace(tzinfo=timezone.utc)
    
    latest_match = max(league_matches, key=parse_date)
    return latest_match.get('id'), latest_match

def get_match_details(match_id):
    """Get detailed match information"""
    try:
        response = requests.get(
            f"https://api.henrikdev.xyz/valorant/v2/match/{match_id}",
            headers={"Authorization": api_key, "Accept": "*/*"},
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting match details: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching match details: {e}")
        return None

def extract_carba_players(match_data):
    """Extract Carings Baes players from match data"""
    players_data = match_data.get('data', {}).get('players', {})
    all_players = players_data.get('all_players', [])
    
    # Find our team (Carings Baes / CarBa)
    teams = match_data.get('data', {}).get('teams', {})
    carba_team_color = None
    
    # Check which team is Carings Baes
    for color, team_data in teams.items():
        roster = team_data.get('roster', {})
        if roster.get('name') == 'Carings Baes' or roster.get('tag') == 'CarBa':
            carba_team_color = color.capitalize()  # Red or Blue
            break
    
    if not carba_team_color:
        return [], None
    
    # Get our players
    carba_players = []
    for player in all_players:
        if player.get('team', '').lower() == carba_team_color.lower():
            name = player.get('name', 'Unknown')
            tag = player.get('tag', '')
            agent = player.get('character', 'Unknown')
            
            stats = player.get('stats', {})
            kills = stats.get('kills', 0)
            deaths = stats.get('deaths', 0)
            assists = stats.get('assists', 0)
            
            carba_players.append({
                'name': f"{name}#{tag}" if tag else name,
                'agent': agent,
                'kda': f"{kills}/{deaths}/{assists}"
            })
    
    return carba_players, carba_team_color

def get_match_result(match_data, carba_team_color):
    """Determine if we won or lost and get scores"""
    teams = match_data.get('data', {}).get('teams', {})
    
    if carba_team_color.lower() == 'red':
        our_team = teams.get('red', {})
        enemy_team = teams.get('blue', {})
    else:
        our_team = teams.get('blue', {})
        enemy_team = teams.get('red', {})
    
    our_rounds = our_team.get('rounds_won', 0)
    enemy_rounds = enemy_team.get('rounds_won', 0)
    won = our_team.get('has_won', False)
    
    enemy_name = enemy_team.get('roster', {}).get('name', 'Unknown Team')
    
    return {
        'won': won,
        'our_score': our_rounds,
        'enemy_score': enemy_rounds,
        'enemy_name': enemy_name,
        'final_score': f"{our_rounds} - {enemy_rounds}"
    }

def send_webhook(carba_players, match_result, points_info, match_data):
    """Send notification to Discord webhook"""
    if not webhook_url:
        print("No webhook URL configured")
        return
    
    # Get map name
    map_name = match_data.get('data', {}).get('metadata', {}).get('map', 'Unknown')
    
    # Format player list
    player_list = "\n".join([f"• **{p['name']}** ({p['agent']}) - {p['kda']}" for p in carba_players])
    
    # Create embed
    embed = {
        "title": "🎮 New Carings Baes Match Result!",
        "color": 0x00ff00 if match_result['won'] else 0xff0000,
        "fields": [
            {
                "name": "📍 Map",
                "value": map_name,
                "inline": True
            },
            {
                "name": "🎯 Final Score",
                "value": f"**{match_result['final_score']}** vs {match_result['enemy_name']}",
                "inline": True
            },
            {
                "name": "🏆 Result",
                "value": "**VICTORY** ✅" if match_result['won'] else "**DEFEAT** ❌",
                "inline": True
            },
            {
                "name": "👥 Our Team",
                "value": player_list,
                "inline": False
            },
            {
                "name": "💰 New Score",
                "value": f"**{points_info['points_after']} (+{points_info['points_gained']})**",
                "inline": True
            }
        ],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {
            "text": "Premier League Monitor"
        }
    }
    
    payload = {
        "embeds": [embed]
    }
    
    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 204:
            print("✅ Webhook sent successfully!")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")

def test_webhook():
    """Test the webhook by sending the latest match result"""
    print("🧪 Testing webhook with latest match...")
    
    # Get team history
    history_data = get_team_history()
    if not history_data:
        print("❌ Failed to get history data")
        return
    
    # Get latest league match
    result = get_latest_league_match_id(history_data)
    if not result:
        print("❌ No league matches found")
        return
    
    match_id, match_info = result
    print(f"🔍 Testing with match ID: {match_id}")
    
    # Get detailed match information
    match_details = get_match_details(match_id)
    if not match_details or match_details.get('status') != 200:
        print("❌ Failed to get match details")
        return
    
    # Extract our players and team info
    carba_players, carba_team_color = extract_carba_players(match_details)
    
    if not carba_players or not carba_team_color:
        print("❌ Could not find Carings Baes team data")
        return
    
    # Get match result
    match_result = get_match_result(match_details, carba_team_color)
    
    # Get points info
    points_info = {
        'points_before': match_info.get('points_before', 0),
        'points_after': match_info.get('points_after', 0),
        'points_gained': match_info.get('points_after', 0) - match_info.get('points_before', 0)
    }
    
    print(f"📊 Match Result: {match_result['final_score']} ({'WIN' if match_result['won'] else 'LOSS'})")
    print(f"💰 Points: {points_info['points_after']} (+{points_info['points_gained']})")
    print(f"👥 Players found: {len(carba_players)}")
    
    # Send test webhook notification
    send_webhook(carba_players, match_result, points_info, match_details)
    print("🧪 Test webhook completed!")

def main():
    global last_known_match_id
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_webhook()
        return
    
    print("🚀 Starting Premier League Monitor...")
    print("⏱️  Checking for new matches every 10 seconds")
    print("📡 Press Ctrl+C to stop")
    print("💡 Tip: Run with '--test' to test webhook with latest match")
    
    # Get initial state
    history_data = get_team_history()
    if history_data:
        result = get_latest_league_match_id(history_data)
        if result:
            last_known_match_id, _ = result
            print(f"🔍 Initial latest match ID: {last_known_match_id}")
    
    while True:
        try:
            print(f"🔄 Checking for new matches... ({datetime.now().strftime('%H:%M:%S')})")
            
            # Get current history
            history_data = get_team_history()
            if not history_data:
                print("❌ Failed to get history data")
                time.sleep(10)
                continue
            
            # Check for new match
            result = get_latest_league_match_id(history_data)
            if not result:
                print("❌ No league matches found")
                time.sleep(10)
                continue
            
            current_match_id, match_info = result
            
            # Check if this is a new match
            if current_match_id != last_known_match_id:
                print(f"🆕 NEW MATCH DETECTED: {current_match_id}")
                
                # Get detailed match information
                match_details = get_match_details(current_match_id)
                if match_details and match_details.get('status') == 200:
                    
                    # Extract our players and team info
                    carba_players, carba_team_color = extract_carba_players(match_details)
                    
                    if carba_players and carba_team_color:
                        # Get match result
                        match_result = get_match_result(match_details, carba_team_color)
                        
                        # Get points info
                        points_info = {
                            'points_before': match_info.get('points_before', 0),
                            'points_after': match_info.get('points_after', 0),
                            'points_gained': match_info.get('points_after', 0) - match_info.get('points_before', 0)
                        }
                        
                        print(f"📊 Match Result: {match_result['final_score']} ({'WIN' if match_result['won'] else 'LOSS'})")
                        print(f"💰 Points: {points_info['points_after']} (+{points_info['points_gained']})")
                        
                        # Send webhook notification
                        send_webhook(carba_players, match_result, points_info, match_details)
                        
                        # Update last known match
                        last_known_match_id = current_match_id
                    else:
                        print("❌ Could not find Carings Baes team data")
                else:
                    print("❌ Failed to get match details")
            else:
                print("✅ No new matches")
            
            # Wait 10 seconds before next check
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()