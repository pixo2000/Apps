import discord
from discord.ext import commands, tasks
import requests
import os
import json
import asyncio
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Get tokens and keys from environment
bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('HDEV_API_KEY')

# Track the last known match ID to detect new matches
last_known_match_id = None

# Track bot session start time
bot_start_time = None

# Track monitoring statistics
monitoring_cycles = 0
last_check_time = None

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Remove default help command and replace with our custom one
bot.remove_command('help')

# Configuration
TEAM_NAME = "Carings Baes"
TEAM_TAG = "CarBa"
NOTIFICATION_CHANNEL_ID = None  # Will be set when bot joins a server
LOG_CHANNEL_ID = None  # Will be set for command logging

class ValorantAPI:
    """Handles all Valorant API interactions"""
    
    @staticmethod
    def get_team_history():
        """Get the team's match history from the API"""
        try:
            response = requests.get(
                f"https://api.henrikdev.xyz/valorant/v1/premier/{TEAM_NAME}/{TEAM_TAG}/history",
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
            if roster.get('name') == TEAM_NAME or roster.get('tag') == TEAM_TAG:
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
                acs = stats.get('score', 0) // max(match_data.get('data', {}).get('metadata', {}).get('rounds_played', 1), 1)
                
                carba_players.append({
                    'name': f"{name}#{tag}" if tag else name,
                    'agent': agent,
                    'kda': f"{kills}/{deaths}/{assists}",
                    'acs': acs,
                    'kills': kills,
                    'deaths': deaths,
                    'assists': assists
                })
        
        return carba_players, carba_team_color

    @staticmethod
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
        enemy_tag = enemy_team.get('roster', {}).get('tag', '')
        
        # Format enemy team name with tag
        enemy_display = f"{enemy_name}#{enemy_tag}" if enemy_tag else enemy_name
        
        return {
            'won': won,
            'our_score': our_rounds,
            'enemy_score': enemy_rounds,
            'enemy_name': enemy_name,
            'enemy_tag': enemy_tag,
            'enemy_display': enemy_display,
            'final_score': f"{our_rounds} - {enemy_rounds}"
        }

    @staticmethod
    def get_team_history_by_name(team_name, team_tag):
        """Get any team's match history from the API"""
        try:
            # URL encode the team name to handle spaces and special characters
            import urllib.parse
            encoded_team_name = urllib.parse.quote(team_name)
            encoded_team_tag = urllib.parse.quote(team_tag)
            
            response = requests.get(
                f"https://api.henrikdev.xyz/valorant/v1/premier/{encoded_team_name}/{encoded_team_tag}/history",
                headers={"Authorization": api_key, "Accept": "*/*"},
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting history for {team_name}#{team_tag}: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error fetching history for {team_name}#{team_tag}: {e}")
            return None

    @staticmethod
    def extract_team_players(match_data, target_team_name, target_team_tag):
        """Extract players from a specific team in match data"""
        players_data = match_data.get('data', {}).get('players', {})
        all_players = players_data.get('all_players', [])
        
        # Find the target team
        teams = match_data.get('data', {}).get('teams', {})
        target_team_color = None
        
        # Check which team matches our target
        for color, team_data in teams.items():
            roster = team_data.get('roster', {})
            if (roster.get('name', '').lower() == target_team_name.lower() or 
                roster.get('tag', '').lower() == target_team_tag.lower()):
                target_team_color = color.capitalize()  # Red or Blue
                break
        
        if not target_team_color:
            return [], None
        
        # Get the team's players
        team_players = []
        for player in all_players:
            if player.get('team', '').lower() == target_team_color.lower():
                name = player.get('name', 'Unknown')
                tag = player.get('tag', '')
                agent = player.get('character', 'Unknown')
                
                stats = player.get('stats', {})
                kills = stats.get('kills', 0)
                deaths = stats.get('deaths', 0)
                assists = stats.get('assists', 0)
                acs = stats.get('score', 0) // max(match_data.get('data', {}).get('metadata', {}).get('rounds_played', 1), 1)
                
                team_players.append({
                    'name': f"{name}#{tag}" if tag else name,
                    'agent': agent,
                    'kda': f"{kills}/{deaths}/{assists}",
                    'acs': acs,
                    'kills': kills,
                    'deaths': deaths,
                    'assists': assists
                })
        
        return team_players, target_team_color

    @staticmethod
    def get_match_result_for_team(match_data, team_color):
        """Determine if the specified team won or lost and get scores"""
        teams = match_data.get('data', {}).get('teams', {})
        
        if team_color.lower() == 'red':
            our_team = teams.get('red', {})
            enemy_team = teams.get('blue', {})
        else:
            our_team = teams.get('blue', {})
            enemy_team = teams.get('red', {})
        
        our_rounds = our_team.get('rounds_won', 0)
        enemy_rounds = enemy_team.get('rounds_won', 0)
        won = our_team.get('has_won', False)
        
        enemy_name = enemy_team.get('roster', {}).get('name', 'Unknown Team')
        enemy_tag = enemy_team.get('roster', {}).get('tag', '')
        our_name = our_team.get('roster', {}).get('name', 'Unknown Team')
        
        # Format enemy team name with tag
        enemy_display = f"{enemy_name}#{enemy_tag}" if enemy_tag else enemy_name
        
        return {
            'won': won,
            'our_score': our_rounds,
            'enemy_score': enemy_rounds,
            'enemy_name': enemy_name,
            'enemy_tag': enemy_tag,
            'enemy_display': enemy_display,
            'our_name': our_name,
            'final_score': f"{our_rounds} - {enemy_rounds}"
        }

async def log_command(ctx, command_name, result_status="success", error_msg=None, additional_info=None):
    """Log command execution to the designated log channel"""
    if not LOG_CHANNEL_ID:
        return
    
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if not log_channel:
        return
    
    try:
        # Get user info
        user = ctx.author
        guild = ctx.guild.name if ctx.guild else "DM"
        channel = ctx.channel.name if hasattr(ctx.channel, 'name') else "DM"
        
        # Determine embed color based on result
        if result_status == "success":
            color = 0x00ff00  # Green
            status_emoji = ""
        elif result_status == "error":
            color = 0xff0000  # Red
            status_emoji = ""
        else:
            color = 0xffff00  # Yellow
            status_emoji = ""
        
        # Create log embed
        embed = discord.Embed(
            title=f"{status_emoji} Command Executed",
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name=" User",
            value=f"{user.mention} ({user.name}#{user.discriminator})",
            inline=True
        )
        
        embed.add_field(
            name=" Location",
            value=f"**Server:** {guild}\n**Channel:** #{channel}",
            inline=True
        )
        
        embed.add_field(
            name=" Command",
            value=f"`{command_name}`",
            inline=True
        )
        
        # Add user message content
        if ctx.message.content:
            message_content = ctx.message.content[:500] + ('...' if len(ctx.message.content) > 500 else '')
            embed.add_field(
                name=" User Message",
                value=f"```{message_content}```",
                inline=False
            )
        
        if result_status == "error" and error_msg:
            embed.add_field(
                name=" Error",
                value=f"```{error_msg[:1000]}{'...' if len(error_msg) > 1000 else ''}```",
                inline=False
            )
        
        if additional_info:
            embed.add_field(
                name=" Details",
                value=additional_info[:1000] + ('...' if len(additional_info) > 1000 else ''),
                inline=False
            )
        
        embed.set_footer(text=f"User ID: {user.id} | Message ID: {ctx.message.id}")
        
        await log_channel.send(embed=embed)
        
    except Exception as e:
        print(f"Failed to log command: {e}")

@bot.event
async def on_ready():
    """Called when the bot is ready"""
    global bot_start_time
    bot_start_time = datetime.now(timezone.utc)
    
    print(f' {bot.user.name} has connected to Discord!')
    print(f' Monitoring Premier League matches for {TEAM_NAME}')
    
    # Start the match monitoring task
    check_for_new_matches.start()

@bot.event
async def on_guild_join(guild):
    """Set notification channel when joining a server"""
    global NOTIFICATION_CHANNEL_ID
    # Try to find a channel with 'general' or 'valorant' in the name
    for channel in guild.text_channels:
        if any(keyword in channel.name.lower() for keyword in ['general', 'valorant', 'gaming', 'matches']):
            NOTIFICATION_CHANNEL_ID = channel.id
            break
    
    if not NOTIFICATION_CHANNEL_ID and guild.text_channels:
        NOTIFICATION_CHANNEL_ID = guild.text_channels[0].id

@tasks.loop(seconds=30)
async def check_for_new_matches():
    """Check for new Premier League matches"""
    global last_known_match_id, monitoring_cycles, last_check_time
    
    monitoring_cycles += 1
    last_check_time = datetime.now(timezone.utc)
    
    try:
        # Get current history
        history_data = ValorantAPI.get_team_history()
        if not history_data:
            return
        
        # Check for new match
        result = ValorantAPI.get_latest_league_match_id(history_data)
        if not result:
            return
        
        current_match_id, match_info = result
        
        # Check if this is a new match
        if current_match_id != last_known_match_id:
            print(f" NEW MATCH DETECTED: {current_match_id}")
            
            # Get detailed match information
            match_details = ValorantAPI.get_match_details(current_match_id)
            if match_details and match_details.get('status') == 200:
                
                # Extract our players and team info
                carba_players, carba_team_color = ValorantAPI.extract_carba_players(match_details)
                
                if carba_players and carba_team_color:
                    # Get match result
                    match_result = ValorantAPI.get_match_result(match_details, carba_team_color)
                    
                    # Get points info
                    points_info = {
                        'points_before': match_info.get('points_before', 0),
                        'points_after': match_info.get('points_after', 0),
                        'points_gained': match_info.get('points_after', 0) - match_info.get('points_before', 0)
                    }
                    
                    # Send notification to Discord
                    await send_match_notification(carba_players, match_result, points_info, match_details)
                    
                    # Update last known match
                    last_known_match_id = current_match_id
    
    except Exception as e:
        print(f" Error in match monitoring: {e}")

async def send_match_notification(carba_players, match_result, points_info, match_data):
    """Send match notification to Discord"""
    if not NOTIFICATION_CHANNEL_ID:
        return
    
    channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
    if not channel:
        return
    
    # Get map name
    map_name = match_data.get('data', {}).get('metadata', {}).get('map', 'Unknown')
    
    # Format player list sorted by KDA (kills + assists - deaths)
    def calculate_kda_score(player):
        return player['kills'] + player['assists'] - player['deaths']
    
    sorted_players = sorted(carba_players, key=calculate_kda_score, reverse=True)
    player_list = "\n".join([
        f" **{p['name']}** ({p['agent']}) - {p['kda']} | {p['acs']} ACS" 
        for p in sorted_players
    ])
    
    # Create embed
    embed = discord.Embed(
        title=" New Carings Baes Match Result!",
        color=0x00ff00 if match_result['won'] else 0xff0000,
        timestamp=datetime.now(timezone.utc)
    )
    
    embed.add_field(name=" Map", value=map_name, inline=True)
    embed.add_field(
        name=" Final Score", 
        value=f"**{match_result['final_score']}**", 
        inline=True
    )
    embed.add_field(
        name=" Result", 
        value="**VICTORY** " if match_result['won'] else "**DEFEAT** ", 
        inline=True
    )
    
    embed.add_field(
        name=" Enemy Team", 
        value=f"**{match_result['enemy_display']}**", 
        inline=True
    )
    
    embed.add_field(
        name=f" Points (+{points_info['points_gained']})", 
        value=f"{points_info['points_before']}  {points_info['points_after']}", 
        inline=True
    )
    
    # Add empty field for spacing
    embed.add_field(name="\u200b", value="\u200b", inline=True)
    
    embed.add_field(name=" Our Team", value=player_list, inline=False)
    embed.set_footer(text="Premier League Monitor by Ghnter")
    
    await channel.send(embed=embed)

@bot.command(name='latest')
async def latest_match(ctx):
    """Get the latest match result"""
    try:
        # Get team history
        history_data = ValorantAPI.get_team_history()
        if not history_data:
            await ctx.send(" Failed to get match history!")
            return
        
        # Get latest league match
        result = ValorantAPI.get_latest_league_match_id(history_data)
        if not result:
            await ctx.send(" No league matches found!")
            return
        
        match_id, match_info = result
        
        # Get detailed match information
        match_details = ValorantAPI.get_match_details(match_id)
        if not match_details or match_details.get('status') != 200:
            await ctx.send(" Failed to get match details!")
            return
        
        # Extract our players and team info
        carba_players, carba_team_color = ValorantAPI.extract_carba_players(match_details)
        
        if not carba_players or not carba_team_color:
            await ctx.send(" Could not find team data!")
            return
        
        # Get match result
        match_result = ValorantAPI.get_match_result(match_details, carba_team_color)
        
        # Get points info
        points_info = {
            'points_before': match_info.get('points_before', 0),
            'points_after': match_info.get('points_after', 0),
            'points_gained': match_info.get('points_after', 0) - match_info.get('points_before', 0)
        }
        
        # Get map name and date
        map_name = match_details.get('data', {}).get('metadata', {}).get('map', 'Unknown')
        match_date = match_info.get('started_at', '')
        
        # Format player list sorted by KDA (kills + assists - deaths)
        def calculate_kda_score(player):
            return player['kills'] + player['assists'] - player['deaths']
        
        sorted_players = sorted(carba_players, key=calculate_kda_score, reverse=True)
        player_list = "\n".join([
            f" **{p['name']}** ({p['agent']}) - {p['kda']} | {p['acs']} ACS" 
            for p in sorted_players
        ])
        
        # Create embed
        embed = discord.Embed(
            title=" Latest Match Result",
            color=0x00ff00 if match_result['won'] else 0xff0000,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name=" Map", value=map_name, inline=True)
        embed.add_field(
            name=" Final Score", 
            value=f"**{match_result['final_score']}**", 
            inline=True
        )
        embed.add_field(
            name=" Result", 
            value="**VICTORY** " if match_result['won'] else "**DEFEAT** ", 
            inline=True
        )
        
        embed.add_field(
            name=" Enemy Team", 
            value=f"**{match_result['enemy_display']}**", 
            inline=True
        )
        
        embed.add_field(
            name=f" Points (+{points_info['points_gained']})", 
            value=f"{points_info['points_before']}  {points_info['points_after']}", 
            inline=True
        )
        
        # Add empty field for spacing
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        
        embed.add_field(name=" Our Team", value=player_list, inline=False)
        embed.set_footer(text=f"Match ID: {match_id}")
        
        await ctx.send(embed=embed)
        
        # Log successful command
        await log_command(ctx, "!latest", "success", additional_info=f"Match ID: {match_id}")
        
    except Exception as e:
        await ctx.send(f" Error getting latest match: {str(e)}")
        
        # Log failed command
        await log_command(ctx, "!latest", "error", error_msg=str(e))

@bot.command(name='history')
async def match_history(ctx, limit: int = 5):
    """Get recent match history"""
    try:
        if limit > 10:
            limit = 10
        
        # Get team history
        history_data = ValorantAPI.get_team_history()
        if not history_data:
            await ctx.send(" Failed to get match history!")
            return
        
        league_matches = history_data.get('data', {}).get('league_matches', [])
        if not league_matches:
            await ctx.send(" No league matches found!")
            return
        
        # Sort matches by date (most recent first)
        def parse_date(match):
            try:
                date_str = match.get('started_at', '')
                if date_str.endswith('Z'):
                    date_str = date_str.replace('Z', '+00:00')
                return datetime.fromisoformat(date_str)
            except:
                return datetime.min.replace(tzinfo=timezone.utc)
        
        recent_matches = sorted(league_matches, key=parse_date, reverse=True)[:limit]
        
        embed = discord.Embed(
            title=f" Recent Match History ({len(recent_matches)} matches)",
            color=0x0099ff,
            timestamp=datetime.now(timezone.utc)
        )
        
        for i, match in enumerate(recent_matches, 1):
            points_gained = match.get('points_after', 0) - match.get('points_before', 0)
            result = " WIN" if points_gained > 0 else " LOSS" if points_gained < 0 else " DRAW"
            
            match_date = parse_date(match).strftime('%m/%d %H:%M')
            
            embed.add_field(
                name=f"{i}. {match_date}",
                value=f"{result} | Points: {match.get('points_after', 0)} ({points_gained:+d})",
                inline=False
            )
        
        embed.set_footer(text="Use !latest for detailed info on the most recent match")
        await ctx.send(embed=embed)
        
        # Log successful command
        await log_command(ctx, f"!history {limit}", "success", additional_info=f"Showed {len(recent_matches)} matches")
        
    except Exception as e:
        await ctx.send(f" Error getting match history: {str(e)}")
        
        # Log failed command
        await log_command(ctx, f"!history {limit}", "error", error_msg=str(e))

@bot.command(name='lookup')
async def lookup_team_match(ctx, team_name: str, team_tag: str):
    """Look up the latest match for any Premier team"""
    try:
        # Remove # from team_tag if user included it
        if team_tag.startswith('#'):
            team_tag = team_tag[1:]
        
        await ctx.send(f" Looking up latest match for **{team_name}#{team_tag}**...")
        
        # Get team history
        history_data = ValorantAPI.get_team_history_by_name(team_name, team_tag)
        if not history_data:
            await ctx.send(f" Failed to get match history for **{team_name}#{team_tag}**! Check the team name and tag.")
            return
        
        if history_data.get('status') != 200:
            error_msg = history_data.get('errors', [{}])[0].get('message', 'Unknown error')
            await ctx.send(f" API Error: {error_msg}")
            return
        
        # Get latest league match
        result = ValorantAPI.get_latest_league_match_id(history_data)
        if not result:
            await ctx.send(f" No Premier League matches found for **{team_name}#{team_tag}**!")
            return
        
        match_id, match_info = result
        
        # Get detailed match information
        match_details = ValorantAPI.get_match_details(match_id)
        if not match_details or match_details.get('status') != 200:
            await ctx.send(" Failed to get match details!")
            return
        
        # Extract team players and info
        team_players, team_color = ValorantAPI.extract_team_players(match_details, team_name, team_tag)
        
        if not team_players or not team_color:
            await ctx.send(f" Could not find **{team_name}#{team_tag}** in the match data!")
            return
        
        # Get match result
        match_result = ValorantAPI.get_match_result_for_team(match_details, team_color)
        
        # Get points info
        points_info = {
            'points_before': match_info.get('points_before', 0),
            'points_after': match_info.get('points_after', 0),
            'points_gained': match_info.get('points_after', 0) - match_info.get('points_before', 0)
        }
        
        # Get map name and date
        map_name = match_details.get('data', {}).get('metadata', {}).get('map', 'Unknown')
        match_date = match_info.get('started_at', '')
        
        # Parse match date
        try:
            if match_date:
                if match_date.endswith('Z'):
                    match_date = match_date.replace('Z', '+00:00')
                parsed_date = datetime.fromisoformat(match_date)
                match_timestamp = int(parsed_date.timestamp())
            else:
                match_timestamp = None
        except:
            match_timestamp = None
        
        # Format player list sorted by KDA (kills + assists - deaths)
        def calculate_kda_score(player):
            return player['kills'] + player['assists'] - player['deaths']
        
        sorted_players = sorted(team_players, key=calculate_kda_score, reverse=True)
        player_list = "\n".join([
            f" **{p['name']}** ({p['agent']}) - {p['kda']} | {p['acs']} ACS" 
            for p in sorted_players
        ])
        
        # Create embed
        embed = discord.Embed(
            title=f" Latest Match: {team_name}#{team_tag}",
            color=0x00ff00 if match_result['won'] else 0xff0000,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(name=" Map", value=map_name, inline=True)
        embed.add_field(
            name=" Final Score", 
            value=f"**{match_result['final_score']}**", 
            inline=True
        )
        embed.add_field(
            name=" Result", 
            value="**VICTORY** " if match_result['won'] else "**DEFEAT** ", 
            inline=True
        )
        
        if match_timestamp:
            embed.add_field(
                name=" Match Date", 
                value=f"<t:{match_timestamp}:F>", 
                inline=True
            )
        
        embed.add_field(
            name=" Enemy Team", 
            value=f"**{match_result['enemy_display']}**", 
            inline=True
        )
        
        embed.add_field(
            name=f" Points (+{points_info['points_gained']})", 
            value=f"{points_info['points_before']}  {points_info['points_after']}", 
            inline=True
        )
        
        embed.add_field(name=f" {team_name} Roster", value=player_list, inline=False)
        embed.set_footer(text=f"Match ID: {match_id}")
        
        await ctx.send(embed=embed)
        
        # Log successful command
        await log_command(ctx, f"!lookup {team_name} {team_tag}", "success", additional_info=f"Match ID: {match_id}")
        
    except Exception as e:
        await ctx.send(f" Error looking up team: {str(e)}")
        
        # Log failed command
        await log_command(ctx, f"!lookup {team_name} {team_tag}", "error", error_msg=str(e))

@bot.command(name='points')
async def current_points(ctx):
    """Get current Premier League points"""
    try:
        # Get team history
        history_data = ValorantAPI.get_team_history()
        if not history_data:
            await ctx.send(" Failed to get team data!")
            return
        
        # Get latest match for current points
        result = ValorantAPI.get_latest_league_match_id(history_data)
        if not result:
            await ctx.send(" No matches found!")
            return
        
        _, match_info = result
        current_points = match_info.get('points_after', 0)
        
        embed = discord.Embed(
            title=" Current Premier League Points",
            color=0xffd700,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.add_field(
            name=" Carings Baes",
            value=f"**{current_points} Points**",
            inline=False
        )
        
        embed.set_footer(text="Updated after each match")
        await ctx.send(embed=embed)
        
        # Log successful command
        await log_command(ctx, "!points", "success", additional_info=f"Current points: {current_points}")
        
    except Exception as e:
        await ctx.send(f" Error getting points: {str(e)}")
        
        # Log failed command
        await log_command(ctx, "!points", "error", error_msg=str(e))

@bot.command(name='setlogchannel')
@commands.has_permissions(administrator=True)
async def set_log_channel(ctx):
    """Set the current channel for command logging"""
    global LOG_CHANNEL_ID
    LOG_CHANNEL_ID = ctx.channel.id
    
    embed = discord.Embed(
        title=" Log Channel Set",
        description=f"Command logging will now be sent to {ctx.channel.mention}",
        color=0x00ff00
    )
    
    await ctx.send(embed=embed)
    
    # Log this command too
    await log_command(ctx, "!setlogchannel", "success", additional_info=f"Log channel set to #{ctx.channel.name}")

@bot.command(name='disablelog')
@commands.has_permissions(administrator=True)
async def disable_logging(ctx):
    """Disable command logging"""
    global LOG_CHANNEL_ID
    
    # Log the disable command before disabling
    await log_command(ctx, "!disablelog", "success", additional_info="Command logging disabled")
    
    LOG_CHANNEL_ID = None
    
    embed = discord.Embed(
        title=" Logging Disabled",
        description="Command logging has been disabled",
        color=0xffff00
    )
    
    await ctx.send(embed=embed)

@bot.command(name='setchannel')
@commands.has_permissions(administrator=True)
async def set_notification_channel(ctx):
    """Set the current channel for match notifications"""
    global NOTIFICATION_CHANNEL_ID
    NOTIFICATION_CHANNEL_ID = ctx.channel.id
    
    embed = discord.Embed(
        title=" Notification Channel Set",
        description=f"Match notifications will now be sent to {ctx.channel.mention}",
        color=0x00ff00
    )
    
    await ctx.send(embed=embed)
    
    # Log this command
    await log_command(ctx, "!setchannel", "success", additional_info=f"Notification channel set to #{ctx.channel.name}")

@bot.command(name='status')
async def bot_status(ctx):
    """Show bot and API status"""
    try:
        # Test API connection
        api_status = " Online"
        api_response_time = "N/A"
        last_match_status = "N/A"
        
        import time
        start_time = time.time()
        
        try:
            # Test API with a simple request
            history_data = ValorantAPI.get_team_history()
            api_response_time = f"{(time.time() - start_time) * 1000:.0f}ms"
            
            if history_data and history_data.get('status') == 200:
                api_status = " Online"
                
                # Check if we can get the latest match
                result = ValorantAPI.get_latest_league_match_id(history_data)
                if result:
                    match_id, match_info = result
                    last_match_status = f" Latest: {match_id[:8]}..."
                else:
                    last_match_status = " No matches found"
            else:
                api_status = " API Error"
                last_match_status = " Unable to fetch"
                
        except Exception as e:
            api_status = " Connection Failed"
            api_response_time = "Timeout"
            last_match_status = f" Error: {str(e)[:20]}..."
        
        # Bot uptime calculation (real session time)
        if bot_start_time:
            uptime = datetime.now(timezone.utc) - bot_start_time
            uptime_str = f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m {uptime.seconds % 60}s"
        else:
            uptime_str = "Starting up..."
        
        # Monitoring task status with more details
        if check_for_new_matches.is_running():
            monitoring_status = " Running"
            next_iteration = check_for_new_matches.next_iteration
            if next_iteration:
                seconds_until_next = (next_iteration - datetime.now(timezone.utc)).total_seconds()
                monitoring_status += f" (next check in {max(0, int(seconds_until_next))}s)"
        else:
            monitoring_status = " Stopped"
        
        # Server count
        server_count = len(bot.guilds)
        
        # Memory usage (approximate)
        memory_usage = "N/A"
        try:
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_usage = f"{process.memory_info().rss / 1024 / 1024:.1f} MB"
        except ImportError:
            memory_usage = "Unavailable (psutil not installed)"
        except Exception:
            memory_usage = "Error reading memory"
        
        embed = discord.Embed(
            title=" Ghnter Status Dashboard",
            description="Current bot and API status information",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        
        # Bot Status Section
        bot_status_text = f"**Status:**  Online\n**Session Uptime:** {uptime_str}\n**Memory:** {memory_usage}\n**Servers:** {server_count}"
        if bot_start_time:
            bot_status_text += f"\n**Started:** <t:{int(bot_start_time.timestamp())}:R>"
        
        embed.add_field(
            name=" Bot Status",
            value=bot_status_text,
            inline=True
        )
        
        # API Status Section
        embed.add_field(
            name=" API Status",
            value=f"**Henrik API:** {api_status}\n**Response Time:** {api_response_time}\n**Last Match:** {last_match_status}",
            inline=True
        )
        
        # Monitoring Status Section
        monitoring_text = f"**Status:** {monitoring_status}\n**Interval:** 30 seconds\n**Channel:** {'Set' if NOTIFICATION_CHANNEL_ID else 'Not Set'}"
        if NOTIFICATION_CHANNEL_ID:
            channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
            if channel:
                monitoring_text += f"\n**Channel Name:** #{channel.name}"
        
        monitoring_text += f"\n**Cycles Completed:** {monitoring_cycles}"
        if last_check_time:
            monitoring_text += f"\n**Last Check:** <t:{int(last_check_time.timestamp())}:R>"
        
        embed.add_field(
            name=" Monitoring",
            value=monitoring_text,
            inline=True
        )
        
        # Team Configuration
        embed.add_field(
            name=" Configuration",
            value=f"**Team:** {TEAM_NAME}\n**Tag:** {TEAM_TAG}\n**Last Known Match:** {last_known_match_id[:8] + '...' if last_known_match_id else 'None'}",
            inline=False
        )
        
        # Add version info
        embed.set_footer(text=f"Ghnter v2.0 | Discord.py {discord.__version__}")
        
        await ctx.send(embed=embed)
        
        # Log successful command
        await log_command(ctx, "!status", "success", additional_info="Status dashboard displayed")
        
    except Exception as e:
        # Fallback embed if status check fails
        embed = discord.Embed(
            title=" Status Check Failed",
            description=f"Unable to get complete status information: {str(e)}",
            color=0xff0000
        )
        await ctx.send(embed=embed)
        
        # Log failed command
        await log_command(ctx, "!status", "error", error_msg=str(e))

@bot.command(name='help')
async def help_command(ctx):
    """Default help command that redirects to help_valorant"""
    await help_valorant(ctx)

@bot.command(name='help_valorant')
async def help_valorant(ctx):
    """Show available Valorant commands"""
    embed = discord.Embed(
        title=" Ghnter - Valorant Premier Bot",
        description="Commands for monitoring Carings Baes Premier League matches",
        color=0x0099ff
    )
    
    embed.add_field(
        name=" !latest",
        value="Show the latest match result with detailed stats",
        inline=False
    )
    
    embed.add_field(
        name=" !lookup <team_name> <team_tag>",
        value="Look up the latest match for any Premier team\nExample: `!lookup \"Team Liquid\" \"TL\"`",
        inline=False
    )
    
    embed.add_field(
        name=" !history [limit]",
        value="Show recent match history (max 10 matches)",
        inline=False
    )
    
    embed.add_field(
        name=" !points",
        value="Show current Premier League points",
        inline=False
    )
    
    embed.add_field(
        name=" !status",
        value="Show bot and API status information",
        inline=False
    )
    
    embed.add_field(
        name=" !setchannel",
        value="Set current channel for automatic match notifications (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name=" !setlogchannel",
        value="Set current channel for command logging (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name=" !disablelog",
        value="Disable command logging (Admin only)",
        inline=False
    )
    
    embed.add_field(
        name=" Auto Monitoring",
        value="Bot automatically checks for new matches every 30 seconds",
        inline=False
    )
    
    embed.set_footer(text="Made with  for Carings Baes")
    await ctx.send(embed=embed)
    
    # Log successful command
    await log_command(ctx, "!help_valorant", "success", additional_info="Help menu displayed")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(" You don't have permission to use this command!")
        await log_command(ctx, f"!{ctx.command.name if ctx.command else 'unknown'}", "error", error_msg="Missing permissions")
    elif isinstance(error, commands.CommandNotFound):
        pass  # Ignore unknown commands
    else:
        await ctx.send(f" An error occurred: {str(error)}")
        await log_command(ctx, f"!{ctx.command.name if ctx.command else 'unknown'}", "error", error_msg=str(error))

# Initialize last known match ID on startup
@check_for_new_matches.before_loop
async def before_match_monitoring():
    global last_known_match_id
    await bot.wait_until_ready()
    
    # Get initial state
    history_data = ValorantAPI.get_team_history()
    if history_data:
        result = ValorantAPI.get_latest_league_match_id(history_data)
        if result:
            last_known_match_id, _ = result
            print(f" Initial latest match ID: {last_known_match_id}")

if __name__ == "__main__":
    if not bot_token:
        print(" Bot token not found in .env file!")
    elif not api_key:
        print(" API key not found in .env file!")
    else:
        print(" Starting Ghnter - Valorant Premier Bot...")
        print(f" Token loaded: {bot_token[:20]}..." if len(bot_token) > 20 else f" Token: {bot_token}")
        print(f" API Key loaded: {api_key[:15]}..." if len(api_key) > 15 else f" API Key: {api_key}")
        
        # Test API first
        print(" Testing API connection...")
        test_response = ValorantAPI.get_team_history()
        if test_response and test_response.get('status') == 200:
            print(" API connection successful!")
        else:
            print(f" API test failed: {test_response}")
        
        bot.run(bot_token)