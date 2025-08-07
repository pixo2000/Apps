import discord
from discord.ext import commands
import random
import asyncio
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

# Load environment variables
load_dotenv()

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Required to access member data and roles
intents.guilds = True   # Required to access guild data
bot = commands.Bot(command_prefix='!', intents=intents)

# Valorant maps
VALORANT_MAPS = [
    "Bind", "Haven", "Split", "Ascent", "Icebox", 
    "Breeze", "Fracture", "Pearl", "Lotus", "Sunset", 
    "Abyss", "Corrode"
]

# Admin users from .env
ADMIN_USERS = [
    int(os.getenv('ADMIN_USER_1', 0)),
    int(os.getenv('ADMIN_USER_2', 0)),
    int(os.getenv('ADMIN_USER_3', 0))
]

# Filter out any zero values (empty env vars)
ADMIN_USERS = [user_id for user_id in ADMIN_USERS if user_id != 0]

# Default team role IDs from .env (optional)
DEFAULT_TEAM_A_ROLE_ID = int(os.getenv('TEAM_A_ROLE_ID', 0)) or None
DEFAULT_TEAM_B_ROLE_ID = int(os.getenv('TEAM_B_ROLE_ID', 0)) or None

# Default logging configuration from .env (optional)
DEFAULT_LOGGING_SERVER_ID = int(os.getenv('LOGGING_SERVER_ID', 0)) or None
DEFAULT_LOGGING_CHANNEL_ID = int(os.getenv('LOGGING_CHANNEL_ID', 0)) or None

# Tournament team role IDs from .env (optional)
DEFAULT_TEAM_1_ROLE_ID = int(os.getenv('TEAM_1_ROLE_ID', 0)) or None
DEFAULT_TEAM_2_ROLE_ID = int(os.getenv('TEAM_2_ROLE_ID', 0)) or None
DEFAULT_TEAM_3_ROLE_ID = int(os.getenv('TEAM_3_ROLE_ID', 0)) or None
DEFAULT_TEAM_4_ROLE_ID = int(os.getenv('TEAM_4_ROLE_ID', 0)) or None

# Logging function
async def log_event(channel_id: int, embed: discord.Embed):
    """Log game events to the designated logging channel"""
    session = get_game_session(channel_id)
    if session.logging_channel_id:
        try:
            # First try to get the channel directly (same server)
            logging_channel = bot.get_channel(session.logging_channel_id)
            
            # If not found and we have a default server ID, try that server
            if not logging_channel and DEFAULT_LOGGING_SERVER_ID:
                server = bot.get_guild(DEFAULT_LOGGING_SERVER_ID)
                if server:
                    logging_channel = server.get_channel(session.logging_channel_id)
            
            if logging_channel:
                await logging_channel.send(embed=embed)
            else:
                print(f"Logging channel {session.logging_channel_id} not found or not accessible")
        except Exception as e:
            print(f"Failed to log to channel {session.logging_channel_id}: {e}")

# Custom View for map selection (ban/pick) buttons
class MapSelectionView(discord.ui.View):
    def __init__(self, session, channel_id, phase, current_team):
        super().__init__(timeout=300)  # 5 minute timeout
        self.session = session
        self.channel_id = channel_id
        self.phase = phase  # "banning" or "picking"
        self.current_team = current_team
        self.status_message = None
        self.maps_message = None
        
        # Add buttons for each available map
        self.update_buttons()
    
    def update_buttons(self):
        # Clear existing buttons
        self.clear_items()
        
        # Don't add new buttons if we're in voting phase
        if self.session.current_phase == "voting":
            return
        
        # Add buttons for each available map (max 25 buttons per view)
        for i, map_name in enumerate(self.session.available_maps[:25]):
            button = discord.ui.Button(
                label=map_name,
                style=discord.ButtonStyle.secondary,
                custom_id=f"map_{i}",
                row=i // 5  # Distribute across 5 rows
            )
            button.callback = self.create_map_callback(map_name)
            self.add_item(button)
    
    def create_map_callback(self, map_name):
        async def map_callback(interaction: discord.Interaction):
            await self.handle_map_selection(interaction, map_name)
        return map_callback
    
    async def handle_map_selection(self, interaction: discord.Interaction, map_name: str):
        user_id = interaction.user.id
        
        # Check if user is in the correct team for their turn
        if self.session.team_a_turn and user_id not in self.session.team_a:
            await interaction.response.send_message(
                f"❌ It's Team A's turn to {self.phase[:-4]}!", 
                ephemeral=True
            )
            return
        elif not self.session.team_a_turn and user_id not in self.session.team_b:
            await interaction.response.send_message(
                f"❌ It's Team B's turn to {self.phase[:-4]}!", 
                ephemeral=True
            )
            return
        
        # Process the selection
        if self.phase == "banning":
            await self.handle_ban(interaction, map_name)
        elif self.phase == "picking":
            await self.handle_pick(interaction, map_name)
    
    async def handle_ban(self, interaction: discord.Interaction, map_name: str):
        # Ban the map
        self.session.available_maps.remove(map_name)
        self.session.banned_maps.append(map_name)
        current_team = "Team A" if self.session.team_a_turn else "Team B"
        self.session.banned_by.append(current_team)
        self.session.phase_count += 1
        
        await interaction.response.send_message(
            f"✅ **{current_team}** banned **{map_name}**!", 
            ephemeral=True
        )
        
        # Log the ban
        log_embed = discord.Embed(
            title="🚫 Map Banned",
            description=f"**{current_team}** banned **{map_name}**",
            color=0xe74c3c
        )
        log_embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=True
        )
        log_embed.add_field(
            name="Banned Maps",
            value=", ".join(self.session.banned_maps),
            inline=False
        )
        await log_event(self.channel_id, log_embed)
        
        # Switch turns and check phase
        self.session.team_a_turn = not self.session.team_a_turn
        
        if self.session.phase_count >= 4:  # 4 bans done, start picking
            self.session.current_phase = "picking"
            self.session.phase_count = 0
            await self.start_picking_phase()
        else:
            # Continue banning phase
            next_team = "Team A" if self.session.team_a_turn else "Team B"
            self.current_team = next_team
            await self.update_embeds()
    
    async def handle_pick(self, interaction: discord.Interaction, map_name: str):
        # Pick the map
        self.session.available_maps.remove(map_name)
        self.session.picked_maps.append(map_name)
        current_team = "Team A" if self.session.team_a_turn else "Team B"
        self.session.picked_by.append(current_team)
        self.session.phase_count += 1
        
        await interaction.response.send_message(
            f"✅ **{current_team}** picked **{map_name}**!", 
            ephemeral=True
        )
        
        # Log the pick
        log_embed = discord.Embed(
            title="✅ Map Picked",
            description=f"**{current_team}** picked **{map_name}**",
            color=0x27ae60
        )
        log_embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=True
        )
        log_embed.add_field(
            name="Picked Maps",
            value=", ".join(self.session.picked_maps),
            inline=False
        )
        await log_event(self.channel_id, log_embed)
        
        # Switch turns and check if picking is done
        self.session.team_a_turn = not self.session.team_a_turn
        
        if self.session.phase_count >= 2:  # 2 picks done, start final map voting
            await self.start_voting_phase()
        else:
            # Continue picking phase
            next_team = "Team A" if self.session.team_a_turn else "Team B"
            self.current_team = next_team
            await self.update_embeds()
    
    async def start_picking_phase(self):
        # Disable all buttons and update to picking phase
        for item in self.children:
            item.disabled = True
        
        self.phase = "picking"
        next_team = "Team A" if self.session.team_a_turn else "Team B"
        self.current_team = next_team
        
        # Update existing embeds instead of creating new messages
        self.update_buttons()
        
        # Update status embed
        status_embed = self.create_status_embed()
        status_embed.title = "🎯 Pick Phase Started!"
        status_embed.description = f"**{next_team}**'s turn to pick"
        
        # Update maps embed  
        maps_embed = self.create_maps_embed()
        
        # Edit existing messages instead of sending new ones
        try:
            await self.maps_message.edit(embed=maps_embed)
            await self.status_message.edit(embed=status_embed, view=self)
        except discord.NotFound:
            pass  # Messages were deleted
    
    async def start_voting_phase(self):
        # Disable all buttons and update phase
        for item in self.children:
            item.disabled = True
        
        self.session.current_phase = "voting"
        
        # First update embeds to show the final pick with disabled buttons
        await self.update_embeds()
        
        if len(self.session.available_maps) > 0:
            self.session.final_map = random.choice(self.session.available_maps)
            self.session.voting_users = self.session.team_a + self.session.team_b
            self.session.votes_for_map = 0
            
            # Update final status
            final_embed = discord.Embed(
                title="🎲 Picking Phase Complete!",
                description=f"**{self.session.final_map}** was randomly chosen as the potential 3rd map",
                color=0x3498db
            )
            
            final_embed.add_field(
                name="🗳️ Voting Phase Starting",
                value="A voting interface will appear below for the final map selection.",
                inline=False
            )
            
            try:
                await self.status_message.edit(embed=final_embed, view=self)
            except discord.NotFound:
                pass
            
            # Start voting
            channel = self.status_message.channel
            
            # Create voting embed and view
            voting_embed = discord.Embed(
                title="🗳️ Final Map Vote",
                description=f"Vote on the final map: **{self.session.final_map}**",
                color=0x3498db
            )
            
            total_players = self.session.team_size * 2
            voting_embed.add_field(
                name="Progress",
                value=f"Votes cast: 0/{total_players}\n"
                      f"Votes for map: 0",
                inline=False
            )
            
            voting_embed.add_field(
                name="Instructions",
                value="Click the buttons below to vote!\n"
                      "🟢 **Yes** - Accept this map\n"
                      "🔴 **No** - Reject this map",
                inline=False
            )
            
            # Create and send voting view
            view = VotingView(self.session, self.channel_id, self.session.final_map)
            message = await channel.send(embed=voting_embed, view=view)
            view.message = message
        else:
            # No maps left for voting
            final_embed = discord.Embed(
                title="✅ Match Ready",
                description="No maps left for 3rd map. Best of 2!",
                color=0x27ae60
            )
            
            try:
                await self.status_message.edit(embed=final_embed, view=self)
            except discord.NotFound:
                pass
    
    def create_status_embed(self):
        phase_name = "Ban Phase" if self.phase == "banning" else "Pick Phase"
        action = "ban" if self.phase == "banning" else "pick"
        
        embed = discord.Embed(
            title=f"🎯 {phase_name}",
            description=f"**{self.current_team}**'s turn to {action}",
            color=0xe74c3c if self.phase == "banning" else 0x27ae60
        )
        
        # Show progress
        if self.phase == "banning":
            embed.add_field(
                name="📋 Progress",
                value=f"Bans: {len(self.session.banned_maps)}/4",
                inline=True
            )
        else:
            embed.add_field(
                name="📋 Progress",
                value=f"Picks: {len(self.session.picked_maps)}/2",
                inline=True
            )
        
        embed.add_field(
            name="Available Maps",
            value=f"{len(self.session.available_maps)} maps remaining",
            inline=True
        )
        
        return embed
    
    def create_maps_embed(self):
        embed = discord.Embed(
            title="Map Selection Progress",
            description="Current picks and bans in order",
            color=0x9b59b6
        )
        
        # Show banned maps in order
        if self.session.banned_maps:
            banned_text = ""
            for i, map_name in enumerate(self.session.banned_maps):
                team_name = self.session.banned_by[i]
                banned_text += f"{i+1}. 🚫 **{map_name}** (banned by {team_name})\n"
            
            embed.add_field(
                name="🚫 Banned Maps",
                value=banned_text,
                inline=False
            )
        
        # Show picked maps in order
        if self.session.picked_maps:
            picked_text = ""
            for i, map_name in enumerate(self.session.picked_maps):
                team_name = self.session.picked_by[i]
                picked_text += f"{i+1}. ✅ **{map_name}** (picked by {team_name})\n"
            
            embed.add_field(
                name="✅ Picked Maps",
                value=picked_text,
                inline=False
            )
        
        # Show current phase progress
        if self.phase == "banning":
            embed.add_field(
                name="📊 Ban Progress",
                value=f"{len(self.session.banned_maps)}/4 bans completed",
                inline=True
            )
        elif self.phase == "picking":
            embed.add_field(
                name="📊 Pick Progress", 
                value=f"{len(self.session.picked_maps)}/2 picks completed",
                inline=True
            )
        
        return embed
    
    async def update_embeds(self):
        # Update buttons first
        self.update_buttons()
        
        # Update status embed
        status_embed = self.create_status_embed()
        
        # Update maps embed
        maps_embed = self.create_maps_embed()
        
        try:
            await self.status_message.edit(embed=status_embed, view=self)
            await self.maps_message.edit(embed=maps_embed)
        except discord.NotFound:
            pass  # Messages were deleted
    
    async def on_timeout(self):
        # Disable buttons when timeout occurs
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="⏰ Selection Timeout",
            description=f"{self.phase.title()} phase has timed out.",
            color=0x95a5a6
        )
        
        try:
            await self.status_message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass  # Message was deleted

# Custom View for voting buttons
class VotingView(discord.ui.View):
    def __init__(self, session, channel_id, map_name):
        super().__init__(timeout=300)  # 5 minute timeout
        self.session = session
        self.channel_id = channel_id
        self.map_name = map_name
        self.message = None
    
    async def update_embed(self):
        if not self.message:
            return
            
        total_players = self.session.team_size * 2
        votes_cast = total_players - len(self.session.voting_users)
        
        embed = discord.Embed(
            title="🗳️ Final Map Vote",
            description=f"Vote on the final map: **{self.map_name}**",
            color=0x3498db
        )
        
        embed.add_field(
            name="Progress",
            value=f"Votes cast: {votes_cast}/{total_players}\n"
                  f"Votes for map: {self.session.votes_for_map}",
            inline=False
        )
        
        if len(self.session.voting_users) > 0:
            embed.add_field(
                name="Instructions",
                value="Click the buttons below to vote!\n"
                      "🟢 **Yes** - Accept this map\n"
                      "🔴 **No** - Reject this map",
                inline=False
            )
        
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass  # Message was deleted
    
    @discord.ui.button(label="Yes ✅", style=discord.ButtonStyle.green, custom_id="vote_yes")
    async def vote_yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, True)
    
    @discord.ui.button(label="No ❌", style=discord.ButtonStyle.red, custom_id="vote_no")
    async def vote_no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_vote(interaction, False)
    
    async def handle_vote(self, interaction: discord.Interaction, vote_yes: bool):
        user_id = interaction.user.id
        
        # Check if user can vote
        if user_id not in self.session.voting_users:
            await interaction.response.send_message(
                "❌ You're not part of this match or have already voted!", 
                ephemeral=True
            )
            return
        
        # Record vote
        self.session.voting_users.remove(user_id)
        if vote_yes:
            self.session.votes_for_map += 1
        
        vote_text = "yes" if vote_yes else "no"
        await interaction.response.send_message(
            f"✅ You voted **{vote_text}** for **{self.map_name}**!", 
            ephemeral=True
        )
        
        # Log the vote
        log_embed = discord.Embed(
            title="🗳️ Vote Cast",
            description=f"{interaction.user.mention} voted **{vote_text}** for **{self.map_name}**",
            color=0x3498db if vote_yes else 0xe74c3c
        )
        log_embed.add_field(
            name="Progress",
            value=f"Votes cast: {self.session.team_size * 2 - len(self.session.voting_users)}/{self.session.team_size * 2}",
            inline=True
        )
        await log_event(self.channel_id, log_embed)
        
        # Update the embed
        await self.update_embed()
        
        # Check if voting is complete
        if len(self.session.voting_users) == 0:
            await self.finish_voting()
    
    async def finish_voting(self):
        total_players = self.session.team_size * 2
        percentage_yes = (self.session.votes_for_map / total_players) * 100
        
        # Disable buttons
        for item in self.children:
            item.disabled = True
        
        if percentage_yes >= 50:
            self.session.picked_maps.append(self.session.final_map)
            self.session.current_phase = "complete"
            
            embed = discord.Embed(
                title="✅ Map Approved!",
                description=f"**{self.session.final_map}** was approved with {percentage_yes:.1f}% yes votes!",
                color=0x27ae60
            )
            
            embed.add_field(
                name="🏆 Final Map Pool",
                value="\n".join([f"{i+1}. {map_name}" for i, map_name in enumerate(self.session.picked_maps)]),
                inline=False
            )
            
            # Log map approval
            log_embed = discord.Embed(
                title="✅ Final Map Approved",
                description=f"**{self.session.final_map}** approved with {percentage_yes:.1f}% yes votes",
                color=0x27ae60
            )
            log_embed.add_field(
                name="Final Map Pool",
                value="\n".join([f"{i+1}. {map_name}" for i, map_name in enumerate(self.session.picked_maps)]),
                inline=False
            )
            await log_event(self.channel_id, log_embed)
            
        else:
            # Map rejected, choose new random map
            if len(self.session.available_maps) > 1:
                # Track the rejected map
                self.session.rejected_maps.append(self.session.final_map)
                self.session.available_maps.remove(self.session.final_map)
                old_map = self.session.final_map
                self.session.final_map = random.choice(self.session.available_maps)
                self.session.voting_users = self.session.team_a + self.session.team_b
                self.session.votes_for_map = 0
                
                # Update the existing voting embed instead of creating new messages
                embed = discord.Embed(
                    title="🗳️ Final Map Vote",
                    description=f"Vote on the final map: **{self.session.final_map}**",
                    color=0x3498db
                )
                
                # Add rejected maps progress
                if self.session.rejected_maps:
                    rejected_text = ", ".join(self.session.rejected_maps)
                    embed.add_field(
                        name="❌ Rejected Maps",
                        value=rejected_text,
                        inline=False
                    )
                
                embed.add_field(
                    name="📊 Rejection Info",
                    value=f"**{old_map}** was rejected with {percentage_yes:.1f}% yes votes",
                    inline=False
                )
                
                embed.add_field(
                    name="Progress",
                    value=f"Votes cast: 0/{total_players}\n"
                          f"Votes for map: 0",
                    inline=False
                )
                
                embed.add_field(
                    name="Instructions",
                    value="Click the buttons below to vote!\n"
                          "🟢 **Yes** - Accept this map\n"
                          "🔴 **No** - Reject this map",
                    inline=False
                )
                
                # Log map rejection
                log_embed = discord.Embed(
                    title="❌ Map Rejected",
                    description=f"**{old_map}** rejected with {percentage_yes:.1f}% yes votes",
                    color=0xe74c3c
                )
                log_embed.add_field(
                    name="New Map Selected",
                    value=f"**{self.session.final_map}** chosen for next vote",
                    inline=False
                )
                if self.session.rejected_maps:
                    log_embed.add_field(
                        name="Total Rejected Maps",
                        value=", ".join(self.session.rejected_maps),
                        inline=False
                    )
                await log_event(self.channel_id, log_embed)
                
                # Reset voting for the new map and reuse the existing view
                self.map_name = self.session.final_map
                
                # Re-enable buttons for new vote
                for item in self.children:
                    item.disabled = False
                
            else:
                # Track the final rejected map
                self.session.rejected_maps.append(self.session.final_map)
                self.session.current_phase = "complete"
                embed = discord.Embed(
                    title="❌ No More Maps",
                    description=f"**{self.session.final_map}** was rejected and no more maps are available.\nPlaying Best of 2!",
                    color=0x95a5a6
                )
                
                # Show all rejected maps
                if self.session.rejected_maps:
                    embed.add_field(
                        name="❌ All Rejected Maps",
                        value=", ".join(self.session.rejected_maps),
                        inline=False
                    )
                
                # Log no more maps
                log_embed = discord.Embed(
                    title="❌ No More Maps Available",
                    description=f"**{self.session.final_map}** rejected, no maps remaining. Playing Best of 2!",
                    color=0x95a5a6
                )
                if self.session.rejected_maps:
                    log_embed.add_field(
                        name="All Rejected Maps",
                        value=", ".join(self.session.rejected_maps),
                        inline=False
                    )
                await log_event(self.channel_id, log_embed)
        
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass  # Message was deleted
    
    async def on_timeout(self):
        # Disable buttons when timeout occurs
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="⏰ Vote Timeout",
            description=f"Voting for **{self.map_name}** has timed out.",
            color=0x95a5a6
        )
        
        try:
            await self.message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass  # Message was deleted

# Game state storage
game_sessions = {}

class GameSession:
    def __init__(self, channel_id: int):
        self.channel_id = channel_id
        self.team_a = []
        self.team_b = []
        self.team_size = 5  # Default to 5 players per team
        self.available_maps = VALORANT_MAPS.copy()
        self.banned_maps = []
        self.picked_maps = []
        self.rejected_maps = []  # Track maps rejected during voting
        self.banned_by = []  # Track which team banned each map
        self.picked_by = []  # Track which team picked each map
        self.current_phase = "setup"  # setup, banning, picking, voting
        self.team_a_turn = True
        self.phase_count = 0
        self.final_map = None
        self.voting_users = []
        self.votes_for_map = 0
        self.team_a_role_id = DEFAULT_TEAM_A_ROLE_ID  # Auto-load from .env
        self.team_b_role_id = DEFAULT_TEAM_B_ROLE_ID  # Auto-load from .env
        self.logging_channel_id = self._get_default_logging_channel()  # Auto-load from .env
        
        # Tournament system
        self.tournament_mode = False
        self.tournament_size = 0  # 10, 16, or 20 players
        self.tournament_phase = "setup"  # setup, small_matches, finals
        self.small_match_current = 0  # 0 or 1 (for 16/20 player tournaments)
        self.team_1 = []  # Tournament teams
        self.team_2 = []
        self.team_3 = []
        self.team_4 = []
        self.team_1_role_id = DEFAULT_TEAM_1_ROLE_ID
        self.team_2_role_id = DEFAULT_TEAM_2_ROLE_ID
        self.team_3_role_id = DEFAULT_TEAM_3_ROLE_ID
        self.team_4_role_id = DEFAULT_TEAM_4_ROLE_ID
        self.match_1_winner = None  # Winner of small match 1 (team 1 or 2)
        self.match_2_winner = None  # Winner of small match 2 (team 3 or 4)
    
    def _get_default_logging_channel(self):
        """Get the default logging channel ID, validating server access"""
        if DEFAULT_LOGGING_SERVER_ID and DEFAULT_LOGGING_CHANNEL_ID:
            # Check if bot has access to the server and channel
            try:
                server = bot.get_guild(DEFAULT_LOGGING_SERVER_ID)
                if server:
                    channel = server.get_channel(DEFAULT_LOGGING_CHANNEL_ID)
                    if channel:
                        return DEFAULT_LOGGING_CHANNEL_ID
            except:
                pass
        return None

    def reset(self):
        self.team_a = []
        self.team_b = []
        self.available_maps = VALORANT_MAPS.copy()
        self.banned_maps = []
        self.picked_maps = []
        self.rejected_maps = []  # Reset rejected tracking
        self.banned_by = []  # Reset ban tracking
        self.picked_by = []  # Reset pick tracking
        self.current_phase = "setup"
        self.team_a_turn = True
        self.phase_count = 0
        self.final_map = None
        self.voting_users = []
        self.votes_for_map = 0
        
        # Reset tournament variables
        self.tournament_mode = False
        self.tournament_size = 0
        self.tournament_phase = "setup"
        self.small_match_current = 0
        self.team_1 = []
        self.team_2 = []
        self.team_3 = []
        self.team_4 = []
        self.match_1_winner = None
        self.match_2_winner = None
        # Keep the role IDs and logging channel when resetting (preserve .env settings)
        # self.team_a_role_id = None
        # self.team_b_role_id = None
        # self.logging_channel_id = None

def is_admin():
    def predicate(ctx):
        return ctx.author.id in ADMIN_USERS
    return commands.check(predicate)

def get_game_session(channel_id: int) -> GameSession:
    if channel_id not in game_sessions:
        game_sessions[channel_id] = GameSession(channel_id)
    return game_sessions[channel_id]

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    
    # Print loaded configurations
    print("=== Auto-loaded Configurations ===")
    if DEFAULT_TEAM_A_ROLE_ID:
        print(f"Team A Role ID: {DEFAULT_TEAM_A_ROLE_ID}")
    if DEFAULT_TEAM_B_ROLE_ID:
        print(f"Team B Role ID: {DEFAULT_TEAM_B_ROLE_ID}")
    if DEFAULT_LOGGING_SERVER_ID:
        print(f"Logging Server ID: {DEFAULT_LOGGING_SERVER_ID}")
    if DEFAULT_LOGGING_CHANNEL_ID:
        print(f"Logging Channel ID: {DEFAULT_LOGGING_CHANNEL_ID}")
    
    if not any([DEFAULT_TEAM_A_ROLE_ID, DEFAULT_TEAM_B_ROLE_ID, DEFAULT_LOGGING_CHANNEL_ID]):
        print("No default configurations loaded from .env")
    print("===================================")
    
    await bot.change_presence(activity=discord.Game(name="Valorant Map Picks"))

@bot.command(name='help_valo', help='Shows all available commands for the ValoPickBot')
async def help_valo(ctx):
    embed = discord.Embed(
        title="🎯 ValoPickBot Commands",
        description="Bot for managing Valorant map picks in Best of 3 matches",
        color=0xff6b6b
    )
    
    embed.add_field(
        name="**Setup Commands**",
        value="`!setup_teams <4|5>` - Setup teams with 4 or 5 players per team\n"
              "`!join_team <a|b>` - Join team A or B\n"
              "`!teams` - Show current teams\n"
              "`!reset` - Reset the current session",
        inline=False
    )
    
    embed.add_field(
        name="**Game Commands**",
        value="`!start_picks` - Start the interactive map selection phase\n"
              "`!start_picks force` - Force start with incomplete teams\n"
              "Interactive buttons will appear for map bans, picks, and voting",
        inline=False
    )
    
    embed.add_field(
        name="**Info Commands**",
        value="`!maps` - Show all available maps\n"
              "`!status` - Show current game status\n"
              "`!phase` - Show current phase info",
        inline=False
    )
    
    embed.add_field(
        name="**Admin Commands** (Admins only)",
        value="`!force_team <user> <a|b>` - Force assign user to team\n"
              "`!force_reset` - Force reset the session\n"
              "`!set_team_roles <team_a_role_id> <team_b_role_id>` - Set Discord roles for teams\n"
              "`!assign_by_roles` - Assign users to teams based on their roles\n"
              "`!assign_default_roles` - Use role IDs from .env file\n"
              "`!set_logging_channel <channel>` - Set channel for game event logging\n"
              "`!reload_config` - Reload configurations from .env file\n"
              "`!show_config` - Show current auto-loaded configurations\n"
              "`!debug_roles` - Debug role assignment issues",
        inline=False
    )
    
    embed.add_field(
        name="**Tournament Commands** (Admins only)",
        value="`!setup_tournament <10|16|20>` - Setup tournament with player count\n"
              "`!assign_tournament_teams` - Assign players to tournament teams\n"
              "`!start_small_match <1|2>` - Start small bracket match (16/20 tournaments)\n"
              "`!set_match_winner <match> <team>` - Set winner and advance tournament",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='setup_teams', help='Setup teams with specified size (4 or 5 players)')
@is_admin()
async def setup_teams(ctx, team_size: int = 5):
    if team_size not in [4, 5]:
        await ctx.send("❌ Team size must be 4 or 5 players!")
        return
    
    session = get_game_session(ctx.channel.id)
    session.reset()
    session.team_size = team_size
    
    embed = discord.Embed(
        title="🚀 Teams Setup Complete!",
        description=f"Teams configured for {team_size}v{team_size} match",
        color=0x00ff00
    )
    
    next_steps = "Players can now join teams using:\n`!join_team a` or `!join_team b`"
    
    # Check if auto-assignment is available
    if session.team_a_role_id and session.team_b_role_id:
        guild = ctx.guild
        role_a = guild.get_role(session.team_a_role_id)
        role_b = guild.get_role(session.team_b_role_id)
        
        if role_a and role_b:
            embed.add_field(
                name="🎭 Auto-Assignment Available",
                value=f"Team roles configured:\n"
                      f"🔴 Team A: {role_a.mention}\n"
                      f"🔵 Team B: {role_b.mention}\n"
                      f"Use `!assign_by_roles` to auto-assign players",
                inline=False
            )
    
    if session.logging_channel_id:
        # Try to find the logging channel
        logging_channel = bot.get_channel(session.logging_channel_id)
        if not logging_channel and DEFAULT_LOGGING_SERVER_ID:
            server = bot.get_guild(DEFAULT_LOGGING_SERVER_ID)
            if server:
                logging_channel = server.get_channel(session.logging_channel_id)
        
        if logging_channel:
            server_info = f" ({logging_channel.guild.name})" if logging_channel.guild != ctx.guild else ""
            embed.add_field(
                name="📋 Logging Active",
                value=f"Events will be logged to #{logging_channel.name}{server_info}",
                inline=False
            )
    
    embed.add_field(
        name="Next Steps",
        value=next_steps,
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='join_team', help='Join team A or B')
async def join_team(ctx, team: str):
    team = team.lower()
    if team not in ['a', 'b']:
        await ctx.send("❌ Please specify team 'a' or 'b'!")
        return
    
    session = get_game_session(ctx.channel.id)
    user_id = ctx.author.id
    
    # Remove user from both teams first
    if user_id in session.team_a:
        session.team_a.remove(user_id)
    if user_id in session.team_b:
        session.team_b.remove(user_id)
    
    # Add to specified team
    target_team = session.team_a if team == 'a' else session.team_b
    team_name = "Team A" if team == 'a' else "Team B"
    
    if len(target_team) >= session.team_size:
        await ctx.send(f"❌ {team_name} is already full ({session.team_size}/{session.team_size})!")
        return
    
    target_team.append(user_id)
    await ctx.send(f"✅ {ctx.author.mention} joined {team_name}!")
    
    # Log team join
    log_embed = discord.Embed(
        title="👥 Player Joined Team",
        description=f"{ctx.author.mention} joined **{team_name}**",
        color=0x3498db
    )
    await log_event(ctx.channel.id, log_embed)
    
    # Check if teams are full
    if len(session.team_a) == session.team_size and len(session.team_b) == session.team_size:
        embed = discord.Embed(
            title="🎉 Teams are full!",
            description="Both teams are ready. Use `!start_picks` to begin the map selection process.",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

@bot.command(name='teams', help='Show current teams')
async def show_teams(ctx):
    session = get_game_session(ctx.channel.id)
    
    embed = discord.Embed(
        title="👥 Current Teams",
        color=0x3498db
    )
    
    team_a_mentions = []
    for user_id in session.team_a:
        team_a_mentions.append(f"<@{user_id}>")
    
    team_b_mentions = []
    for user_id in session.team_b:
        team_b_mentions.append(f"<@{user_id}>")
    
    embed.add_field(
        name=f"🔴 Team A ({len(session.team_a)}/{session.team_size})",
        value="\n".join(team_a_mentions) if team_a_mentions else "Empty",
        inline=True
    )
    
    embed.add_field(
        name=f"🔵 Team B ({len(session.team_b)}/{session.team_size})",
        value="\n".join(team_b_mentions) if team_b_mentions else "Empty",
        inline=True
    )
    
    await ctx.send(embed=embed)

@bot.command(name='maps', help='Show all available Valorant maps')
async def show_maps(ctx):
    embed = discord.Embed(
        title="🗺️ Valorant Maps",
        description="\n".join([f"• {map_name}" for map_name in VALORANT_MAPS]),
        color=0x9b59b6
    )
    await ctx.send(embed=embed)

@bot.command(name='start_picks', help='Start the map pick/ban phase')
async def start_picks(ctx, force: str = None):
    session = get_game_session(ctx.channel.id)
    
    # Check if teams are properly filled
    team_a_count = len(session.team_a)
    team_b_count = len(session.team_b)
    teams_full = team_a_count == session.team_size and team_b_count == session.team_size
    
    if not teams_full:
        if force != "force":
            embed = discord.Embed(
                title="⚠️ Teams Not Full",
                description=f"Teams are not completely filled:\n"
                           f"🔴 Team A: {team_a_count}/{session.team_size}\n"
                           f"🔵 Team B: {team_b_count}/{session.team_size}",
                color=0xffa500
            )
            embed.add_field(
                name="Continue anyway?",
                value="Use `!start_picks force` to start with incomplete teams\n"
                      "or fill the teams first using `!join_team` or `!assign_by_roles`",
                inline=False
            )
            await ctx.send(embed=embed)
            return
        
        # Check if we have at least one player per team
        if team_a_count == 0 or team_b_count == 0:
            await ctx.send("❌ Each team needs at least 1 player to start!")
            return
    
    # Randomly choose which team starts
    session.team_a_turn = random.choice([True, False])
    session.current_phase = "banning"
    session.phase_count = 0
    
    starting_team = "Team A" if session.team_a_turn else "Team B"
    
    # Log game start
    log_embed = discord.Embed(
        title="🎯 Match Started",
        description=f"Map selection phase started - **{starting_team}** goes first",
        color=0xe74c3c
    )
    log_embed.add_field(
        name="Team Setup",
        value=f"🔴 Team A: {team_a_count}/{session.team_size} players\n"
              f"🔵 Team B: {team_b_count}/{session.team_size} players",
        inline=False
    )
    await log_event(ctx.channel.id, log_embed)
    
    # Create interactive map selection interface
    selection_view = MapSelectionView(session, ctx.channel.id, "banning", starting_team)
    
    # Create status embed
    status_embed = selection_view.create_status_embed()
    status_embed.title = "🎯 Map Selection Started!"
    status_embed.description = f"**{starting_team}** was randomly selected to start!\n\n**{starting_team}**'s turn to ban"
    
    if not teams_full:
        status_embed.add_field(
            name="⚠️ Note",
            value=f"Started with incomplete teams:\n"
                  f"🔴 Team A: {team_a_count}/{session.team_size}\n"
                  f"🔵 Team B: {team_b_count}/{session.team_size}",
            inline=False
        )
    
    status_embed.add_field(
        name="📋 Process",
        value="1. Team A ban → Team B ban → Team A ban → Team B ban\n"
              "2. Team A pick → Team B pick\n"
              "3. Random final map + voting",
        inline=False
    )
    
    # Create maps embed
    maps_embed = selection_view.create_maps_embed()
    
    # Send the interactive interface
    maps_message = await ctx.send(embed=maps_embed)
    status_message = await ctx.send(embed=status_embed, view=selection_view)
    
    # Store message references in the view
    selection_view.status_message = status_message
    selection_view.maps_message = maps_message

@bot.command(name='status', help='Show current game status')
async def show_status(ctx):
    session = get_game_session(ctx.channel.id)
    
    embed = discord.Embed(
        title="📊 Game Status",
        color=0x3498db
    )
    
    embed.add_field(
        name="Phase",
        value=session.current_phase.title(),
        inline=True
    )
    
    embed.add_field(
        name="Team Size",
        value=f"{session.team_size}v{session.team_size}",
        inline=True
    )
    
    if session.current_phase in ["banning", "picking"]:
        current_team = "Team A" if session.team_a_turn else "Team B"
        embed.add_field(
            name="Current Turn",
            value=current_team,
            inline=True
        )
    
    if session.banned_maps:
        embed.add_field(
            name="🚫 Banned Maps",
            value=", ".join(session.banned_maps),
            inline=False
        )
    
    if session.picked_maps:
        embed.add_field(
            name="✅ Picked Maps",
            value=", ".join(session.picked_maps),
            inline=False
        )
    
    if session.current_phase == "voting" and session.final_map:
        embed.add_field(
            name="🗳️ Voting on",
            value=session.final_map,
            inline=False
        )
    
    if session.available_maps:
        embed.add_field(
            name="Available Maps",
            value=", ".join(session.available_maps),
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='phase', help='Show current phase information')
async def show_phase(ctx):
    session = get_game_session(ctx.channel.id)
    
    phase_info = {
        "setup": "Setting up teams. Use `!join_team a` or `!join_team b`",
        "banning": f"Ban phase - {'Team A' if session.team_a_turn else 'Team B'}'s turn",
        "picking": f"Pick phase - {'Team A' if session.team_a_turn else 'Team B'}'s turn", 
        "voting": f"Voting on final map: {session.final_map}",
        "complete": "Map selection complete!"
    }
    
    embed = discord.Embed(
        title="🎯 Current Phase",
        description=phase_info.get(session.current_phase, "Unknown phase"),
        color=0xf39c12
    )
    
    await ctx.send(embed=embed)

@bot.command(name='reset', help='Reset the current session')
async def reset_session(ctx):
    session = get_game_session(ctx.channel.id)
    
    # Check if user is admin or part of the current game
    user_id = ctx.author.id
    if user_id not in ADMIN_USERS and user_id not in (session.team_a + session.team_b):
        await ctx.send("❌ Only admins or players in the current game can reset!")
        return
    
    session.reset()
    
    embed = discord.Embed(
        title="🔄 Session Reset",
        description="Game session has been reset. Use `!setup_teams` to start again.",
        color=0x95a5a6
    )
    
    await ctx.send(embed=embed)

@bot.command(name='force_team', help='Force assign a user to a team (Admin only)')
@is_admin()
async def force_team(ctx, user: discord.Member, team: str):
    team = team.lower()
    if team not in ['a', 'b']:
        await ctx.send("❌ Please specify team 'a' or 'b'!")
        return
    
    session = get_game_session(ctx.channel.id)
    user_id = user.id
    
    # Remove user from both teams first
    if user_id in session.team_a:
        session.team_a.remove(user_id)
    if user_id in session.team_b:
        session.team_b.remove(user_id)
    
    # Add to specified team
    target_team = session.team_a if team == 'a' else session.team_b
    team_name = "Team A" if team == 'a' else "Team B"
    
    if len(target_team) >= session.team_size:
        await ctx.send(f"❌ {team_name} is already full ({session.team_size}/{session.team_size})!")
        return
    
    target_team.append(user_id)
    await ctx.send(f"✅ {user.mention} was assigned to {team_name} by admin!")

@bot.command(name='force_reset', help='Force reset the session (Admin only)')
@is_admin()
async def force_reset(ctx):
    session = get_game_session(ctx.channel.id)
    session.reset()
    
    embed = discord.Embed(
        title="🔧 Force Reset",
        description="Game session has been force reset by admin.",
        color=0xe74c3c
    )
    
    await ctx.send(embed=embed)

@bot.command(name='set_team_roles', help='Set Discord roles for teams (Admin only)')
@is_admin()
async def set_team_roles(ctx, team_a_role_id: int, team_b_role_id: int):
    session = get_game_session(ctx.channel.id)
    
    # Verify roles exist
    guild = ctx.guild
    team_a_role = guild.get_role(team_a_role_id)
    team_b_role = guild.get_role(team_b_role_id)
    
    if not team_a_role:
        await ctx.send(f"❌ Role with ID {team_a_role_id} not found!")
        return
    
    if not team_b_role:
        await ctx.send(f"❌ Role with ID {team_b_role_id} not found!")
        return
    
    session.team_a_role_id = team_a_role_id
    session.team_b_role_id = team_b_role_id
    
    embed = discord.Embed(
        title="✅ Team Roles Set",
        description="Discord roles have been assigned to teams",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🔴 Team A",
        value=f"Role: {team_a_role.mention}",
        inline=True
    )
    
    embed.add_field(
        name="🔵 Team B", 
        value=f"Role: {team_b_role.mention}",
        inline=True
    )
    
    embed.add_field(
        name="Next Step",
        value="Use `!assign_by_roles` to automatically assign users based on their roles",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='assign_by_roles', help='Assign users to teams based on their Discord roles (Admin only)')
@is_admin()
async def assign_by_roles(ctx):
    session = get_game_session(ctx.channel.id)
    
    if not session.team_a_role_id or not session.team_b_role_id:
        await ctx.send("❌ Team roles not set! Use `!set_team_roles <team_a_role_id> <team_b_role_id>` first!")
        return
    
    guild = ctx.guild
    team_a_role = guild.get_role(session.team_a_role_id)
    team_b_role = guild.get_role(session.team_b_role_id)
    
    if not team_a_role or not team_b_role:
        await ctx.send("❌ One or both team roles no longer exist!")
        return
    
    # Clear existing teams
    session.team_a = []
    session.team_b = []
    
    # Assign users based on roles
    team_a_assigned = []
    team_b_assigned = []
    team_a_overflow = []
    team_b_overflow = []
    
    for member in guild.members:
        # Skip bots
        if member.bot:
            continue
        
        # Check for Team A role
        if team_a_role in member.roles:
            if len(session.team_a) < session.team_size:
                session.team_a.append(member.id)
                team_a_assigned.append(f"<@{member.id}>")
            else:
                team_a_overflow.append(f"<@{member.id}>")
        
        # Check for Team B role (separate check, not elif, in case someone has both roles)
        if team_b_role in member.roles:
            if len(session.team_b) < session.team_size and member.id not in session.team_a:
                session.team_b.append(member.id)
                team_b_assigned.append(f"<@{member.id}>")
            elif member.id not in session.team_a:  # Don't add to overflow if already in team A
                team_b_overflow.append(f"<@{member.id}>")
    
    embed = discord.Embed(
        title="✅ Teams Assigned by Roles",
        description="Users have been automatically assigned to teams based on their Discord roles",
        color=0x00ff00
    )
    
    embed.add_field(
        name=f"🔴 Team A ({len(session.team_a)}/{session.team_size})",
        value="\n".join(team_a_assigned) if team_a_assigned else "No members assigned",
        inline=True
    )
    
    embed.add_field(
        name=f"🔵 Team B ({len(session.team_b)}/{session.team_size})",
        value="\n".join(team_b_assigned) if team_b_assigned else "No members assigned",
        inline=True
    )
    
    # Show overflow users if any
    if team_a_overflow or team_b_overflow:
        overflow_text = ""
        if team_a_overflow:
            overflow_text += f"**Team A overflow:** {', '.join(team_a_overflow)}\n"
        if team_b_overflow:
            overflow_text += f"**Team B overflow:** {', '.join(team_b_overflow)}"
        
        embed.add_field(
            name="⚠️ Overflow Users",
            value=overflow_text,
            inline=False
        )
    
    # Check if teams are full
    if len(session.team_a) == session.team_size and len(session.team_b) == session.team_size:
        embed.add_field(
            name="🎉 Ready to Start",
            value="Both teams are full! Use `!start_picks` to begin map selection.",
            inline=False
        )
    
    await ctx.send(embed=embed)
    
    # Log role-based team assignment with user mentions
    log_embed = discord.Embed(
        title="🎭 Teams Assigned by Roles",
        description="Users automatically assigned to teams based on Discord roles",
        color=0x00ff00
    )
    
    # Add Team A players
    team_a_log_mentions = []
    for user_id in session.team_a:
        team_a_log_mentions.append(f"<@{user_id}>")
    
    log_embed.add_field(
        name=f"🔴 Team A ({len(session.team_a)} players)",
        value="\n".join(team_a_log_mentions) if team_a_log_mentions else "No players assigned",
        inline=True
    )
    
    # Add Team B players
    team_b_log_mentions = []
    for user_id in session.team_b:
        team_b_log_mentions.append(f"<@{user_id}>")
    
    log_embed.add_field(
        name=f"🔵 Team B ({len(session.team_b)} players)",
        value="\n".join(team_b_log_mentions) if team_b_log_mentions else "No players assigned",
        inline=True
    )
    
    # Add role information
    guild = ctx.guild
    team_a_role = guild.get_role(session.team_a_role_id)
    team_b_role = guild.get_role(session.team_b_role_id)
    
    log_embed.add_field(
        name="Roles Used",
        value=f"🔴 {team_a_role.name if team_a_role else 'Unknown Role'}\n"
              f"🔵 {team_b_role.name if team_b_role else 'Unknown Role'}",
        inline=False
    )
    
    await log_event(ctx.channel.id, log_embed)

@bot.command(name='assign_default_roles', help='Assign teams using role IDs from .env file (Admin only)')
@is_admin()
async def assign_default_roles(ctx):
    if not DEFAULT_TEAM_A_ROLE_ID or not DEFAULT_TEAM_B_ROLE_ID:
        await ctx.send("❌ Default team role IDs not configured in .env file!\n"
                      "Add `TEAM_A_ROLE_ID` and `TEAM_B_ROLE_ID` to your .env file.")
        return
    
    session = get_game_session(ctx.channel.id)
    session.team_a_role_id = DEFAULT_TEAM_A_ROLE_ID
    session.team_b_role_id = DEFAULT_TEAM_B_ROLE_ID
    
    guild = ctx.guild
    team_a_role = guild.get_role(DEFAULT_TEAM_A_ROLE_ID)
    team_b_role = guild.get_role(DEFAULT_TEAM_B_ROLE_ID)
    
    if not team_a_role or not team_b_role:
        await ctx.send("❌ One or both default role IDs from .env file are invalid!")
        return
    
    embed = discord.Embed(
        title="✅ Default Roles Applied",
        description="Using role IDs from .env file",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🔴 Team A",
        value=f"Role: {team_a_role.mention} (ID: {DEFAULT_TEAM_A_ROLE_ID})",
        inline=True
    )
    
    embed.add_field(
        name="🔵 Team B", 
        value=f"Role: {team_b_role.mention} (ID: {DEFAULT_TEAM_B_ROLE_ID})",
        inline=True
    )
    
    embed.add_field(
        name="Next Step",
        value="Use `!assign_by_roles` to automatically assign users based on their roles",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='set_logging_channel', help='Set channel for game event logging (Admin only)')
@is_admin()
async def set_logging_channel(ctx, channel: discord.TextChannel = None):
    session = get_game_session(ctx.channel.id)
    
    if channel is None:
        # If no channel provided, use current channel
        channel = ctx.channel
    
    session.logging_channel_id = channel.id
    
    embed = discord.Embed(
        title="✅ Logging Channel Set",
        description=f"Game events will be logged to {channel.mention}",
        color=0x00ff00
    )
    
    embed.add_field(
        name="Logged Events",
        value="• Map bans and picks\n• Vote results\n• Team assignments\n• Game phase changes\n• Match completion",
        inline=False
    )
    
    await ctx.send(embed=embed)
    
    # Log the logging channel setup
    log_embed = discord.Embed(
        title="📋 Logging Channel Configured",
        description=f"Game events will now be logged to {channel.mention}",
        color=0x3498db
    )
    await log_event(ctx.channel.id, log_embed)

@bot.command(name='debug_roles', help='Debug role assignment (Admin only)')
@is_admin()
async def debug_roles(ctx):
    session = get_game_session(ctx.channel.id)
    guild = ctx.guild
    
    embed = discord.Embed(
        title="🔍 Role Assignment Debug",
        description="Debugging role assignment setup",
        color=0xffa500
    )
    
    # Check if roles are set
    if session.team_a_role_id and session.team_b_role_id:
        team_a_role = guild.get_role(session.team_a_role_id)
        team_b_role = guild.get_role(session.team_b_role_id)
        
        embed.add_field(
            name="Set Roles",
            value=f"Team A: {team_a_role.name if team_a_role else 'Role not found!'} (ID: {session.team_a_role_id})\n"
                  f"Team B: {team_b_role.name if team_b_role else 'Role not found!'} (ID: {session.team_b_role_id})",
            inline=False
        )
        
        # List members with these roles
        if team_a_role:
            team_a_members = [member.display_name for member in guild.members if team_a_role in member.roles and not member.bot]
            embed.add_field(
                name=f"Members with {team_a_role.name}",
                value="\n".join(team_a_members) if team_a_members else "No members found",
                inline=True
            )
        
        if team_b_role:
            team_b_members = [member.display_name for member in guild.members if team_b_role in member.roles and not member.bot]
            embed.add_field(
                name=f"Members with {team_b_role.name}",
                value="\n".join(team_b_members) if team_b_members else "No members found",
                inline=True
            )
    else:
        embed.add_field(
            name="❌ No Roles Set",
            value="Use `!set_team_roles <team_a_role_id> <team_b_role_id>` first!",
            inline=False
        )
    
    # Bot permissions check
    bot_member = guild.get_member(bot.user.id)
    if bot_member:
        embed.add_field(
            name="Bot Permissions",
            value=f"Can read message history: {bot_member.guild_permissions.read_message_history}\n"
                  f"Can view channel: {bot_member.guild_permissions.view_channel}\n"
                  f"Can manage roles: {bot_member.guild_permissions.manage_roles}",
            inline=False
        )
    
    embed.add_field(
        name="Guild Info",
        value=f"Total members: {guild.member_count}\n"
              f"Members cached: {len(guild.members)}",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='reload_config', help='Reload configurations from .env file (Admin only)')
@is_admin()
async def reload_config(ctx):
    """Reload all configurations from .env file for all sessions"""
    global DEFAULT_TEAM_A_ROLE_ID, DEFAULT_TEAM_B_ROLE_ID, DEFAULT_LOGGING_SERVER_ID, DEFAULT_LOGGING_CHANNEL_ID
    
    # Reload environment variables
    load_dotenv()
    
    # Update global defaults
    DEFAULT_TEAM_A_ROLE_ID = int(os.getenv('TEAM_A_ROLE_ID', 0)) or None
    DEFAULT_TEAM_B_ROLE_ID = int(os.getenv('TEAM_B_ROLE_ID', 0)) or None
    DEFAULT_LOGGING_SERVER_ID = int(os.getenv('LOGGING_SERVER_ID', 0)) or None
    DEFAULT_LOGGING_CHANNEL_ID = int(os.getenv('LOGGING_CHANNEL_ID', 0)) or None
    
    # Update existing sessions
    updated_sessions = 0
    for session in game_sessions.values():
        # Only update if they don't have custom settings
        if session.team_a_role_id == session.team_b_role_id == session.logging_channel_id == None:
            session.team_a_role_id = DEFAULT_TEAM_A_ROLE_ID
            session.team_b_role_id = DEFAULT_TEAM_B_ROLE_ID
            session.logging_channel_id = session._get_default_logging_channel()
            updated_sessions += 1
    
    embed = discord.Embed(
        title="✅ Configuration Reloaded",
        description="Configurations have been reloaded from .env file",
        color=0x00ff00
    )
    
    config_text = ""
    if DEFAULT_TEAM_A_ROLE_ID:
        config_text += f"Team A Role ID: {DEFAULT_TEAM_A_ROLE_ID}\n"
    if DEFAULT_TEAM_B_ROLE_ID:
        config_text += f"Team B Role ID: {DEFAULT_TEAM_B_ROLE_ID}\n"
    if DEFAULT_LOGGING_SERVER_ID:
        config_text += f"Logging Server ID: {DEFAULT_LOGGING_SERVER_ID}\n"
    if DEFAULT_LOGGING_CHANNEL_ID:
        config_text += f"Logging Channel ID: {DEFAULT_LOGGING_CHANNEL_ID}\n"
    
    if config_text:
        embed.add_field(
            name="Loaded Configurations",
            value=config_text.strip(),
            inline=False
        )
    else:
        embed.add_field(
            name="No Configurations",
            value="No default configurations found in .env file",
            inline=False
        )
    
    embed.add_field(
        name="Sessions Updated",
        value=f"{updated_sessions} session(s) updated with new defaults",
        inline=False
    )
    
    await ctx.send(embed=embed)

@bot.command(name='show_config', help='Show current auto-loaded configurations (Admin only)')
@is_admin()
async def show_config(ctx):
    """Show current configurations loaded from .env"""
    session = get_game_session(ctx.channel.id)
    
    embed = discord.Embed(
        title="🔧 Current Configuration",
        description="Auto-loaded settings from .env file and current session",
        color=0x3498db
    )
    
    # Global defaults
    global_config = ""
    if DEFAULT_TEAM_A_ROLE_ID:
        guild = ctx.guild
        role_a = guild.get_role(DEFAULT_TEAM_A_ROLE_ID) if guild else None
        global_config += f"Team A Role: {role_a.name if role_a else 'Not found'} (ID: {DEFAULT_TEAM_A_ROLE_ID})\n"
    if DEFAULT_TEAM_B_ROLE_ID:
        guild = ctx.guild
        role_b = guild.get_role(DEFAULT_TEAM_B_ROLE_ID) if guild else None
        global_config += f"Team B Role: {role_b.name if role_b else 'Not found'} (ID: {DEFAULT_TEAM_B_ROLE_ID})\n"
    if DEFAULT_LOGGING_SERVER_ID:
        global_config += f"Logging Server ID: {DEFAULT_LOGGING_SERVER_ID}\n"
    if DEFAULT_LOGGING_CHANNEL_ID:
        global_config += f"Logging Channel ID: {DEFAULT_LOGGING_CHANNEL_ID}\n"
    
    if global_config:
        embed.add_field(
            name="Global Defaults (.env)",
            value=global_config.strip(),
            inline=False
        )
    else:
        embed.add_field(
            name="Global Defaults (.env)",
            value="No default configurations loaded",
            inline=False
        )
    
    # Current session settings
    session_config = ""
    if session.team_a_role_id:
        guild = ctx.guild
        role_a = guild.get_role(session.team_a_role_id) if guild else None
        session_config += f"Team A Role: {role_a.name if role_a else 'Not found'} (ID: {session.team_a_role_id})\n"
    if session.team_b_role_id:
        guild = ctx.guild
        role_b = guild.get_role(session.team_b_role_id) if guild else None
        session_config += f"Team B Role: {role_b.name if role_b else 'Not found'} (ID: {session.team_b_role_id})\n"
    if session.logging_channel_id:
        # Try to find the logging channel
        logging_channel = bot.get_channel(session.logging_channel_id)
        if not logging_channel and DEFAULT_LOGGING_SERVER_ID:
            server = bot.get_guild(DEFAULT_LOGGING_SERVER_ID)
            if server:
                logging_channel = server.get_channel(session.logging_channel_id)
        
        channel_info = f"{logging_channel.name}" if logging_channel else "Not found/accessible"
        server_info = f" ({logging_channel.guild.name})" if logging_channel and logging_channel.guild != ctx.guild else ""
        session_config += f"Logging Channel: #{channel_info}{server_info} (ID: {session.logging_channel_id})\n"
    
    if session_config:
        embed.add_field(
            name="Current Session Settings",
            value=session_config.strip(),
            inline=False
        )
    else:
        embed.add_field(
            name="Current Session Settings",
            value="No session-specific settings configured",
            inline=False
        )
    
    # Auto-assignment status
    if session.team_a_role_id and session.team_b_role_id:
        embed.add_field(
            name="🎭 Auto-Assignment Ready",
            value="Team roles are configured. Use `!assign_by_roles` to auto-assign players.",
            inline=False
        )
    
    if session.logging_channel_id:
        embed.add_field(
            name="📋 Logging Active",
            value="Game events will be automatically logged.",
            inline=False
        )
    
    await ctx.send(embed=embed)

# Tournament Commands
@bot.command(name='setup_tournament', help='Setup tournament with specified player count (10, 16, or 20) (Admin only)')
@is_admin()
async def setup_tournament(ctx, player_count: int):
    if player_count not in [10, 16, 20]:
        await ctx.send("❌ Tournament size must be 10, 16, or 20 players!")
        return
    
    session = get_game_session(ctx.channel.id)
    session.reset()
    session.tournament_mode = True
    session.tournament_size = player_count
    
    if player_count == 10:
        session.team_size = 5
        embed = discord.Embed(
            title="🏆 Tournament Setup - 10 Players",
            description="Standard 5v5 tournament match",
            color=0x00ff00
        )
        embed.add_field(
            name="Format",
            value="Direct 5v5 match with full ban/pick system",
            inline=False
        )
        embed.add_field(
            name="Next Steps",
            value="Use `!assign_tournament_teams` to assign players to teams",
            inline=False
        )
    
    elif player_count in [16, 20]:
        session.team_size = 4 if player_count == 16 else 5
        session.tournament_phase = "small_matches"
        
        embed = discord.Embed(
            title=f"🏆 Tournament Setup - {player_count} Players",
            description=f"Bracket tournament with {session.team_size}v{session.team_size} matches",
            color=0x00ff00
        )
        embed.add_field(
            name="Format",
            value=f"• 2 small matches ({session.team_size}v{session.team_size}) - ban until 1 map remains\n"
                  f"• Winners advance to final match with full ban/pick system",
            inline=False
        )
        embed.add_field(
            name="Tournament Structure",
            value=f"**Small Match 1:** Team 1 vs Team 2\n"
                  f"**Small Match 2:** Team 3 vs Team 4\n"
                  f"**Final:** Winners from both small matches",
            inline=False
        )
        embed.add_field(
            name="Next Steps",
            value="Use `!assign_tournament_teams` to assign players to all 4 teams",
            inline=False
        )
    
    # Log tournament setup
    log_embed = discord.Embed(
        title="🏆 Tournament Configured",
        description=f"Tournament setup for {player_count} players",
        color=0x00ff00
    )
    log_embed.add_field(
        name="Tournament Size",
        value=f"{player_count} players",
        inline=True
    )
    log_embed.add_field(
        name="Match Format",
        value=f"{session.team_size}v{session.team_size}",
        inline=True
    )
    await log_event(ctx.channel.id, log_embed)
    
    await ctx.send(embed=embed)

@bot.command(name='assign_tournament_teams', help='Assign players to tournament teams based on roles (Admin only)')
@is_admin()
async def assign_tournament_teams(ctx):
    session = get_game_session(ctx.channel.id)
    
    if not session.tournament_mode:
        await ctx.send("❌ Tournament mode not active! Use `!setup_tournament` first!")
        return
    
    guild = ctx.guild
    
    if session.tournament_size == 10:
        # Use regular team A/B roles for 10 player tournament
        if not session.team_a_role_id or not session.team_b_role_id:
            await ctx.send("❌ Team A/B roles not configured! Use `!set_team_roles` first!")
            return
        
        team_a_role = guild.get_role(session.team_a_role_id)
        team_b_role = guild.get_role(session.team_b_role_id)
        
        if not team_a_role or not team_b_role:
            await ctx.send("❌ One or both team roles not found!")
            return
        
        # Assign teams
        session.team_a = []
        session.team_b = []
        
        for member in guild.members:
            if member.bot:
                continue
            
            if team_a_role in member.roles and len(session.team_a) < 5:
                session.team_a.append(member.id)
            elif team_b_role in member.roles and len(session.team_b) < 5:
                session.team_b.append(member.id)
        
        embed = discord.Embed(
            title="✅ Tournament Teams Assigned",
            description="10-player tournament teams configured",
            color=0x00ff00
        )
        
        team_a_mentions = [f"<@{uid}>" for uid in session.team_a]
        team_b_mentions = [f"<@{uid}>" for uid in session.team_b]
        
        embed.add_field(
            name=f"🔴 Team A ({len(session.team_a)}/5)",
            value="\n".join(team_a_mentions) if team_a_mentions else "No players assigned",
            inline=True
        )
        embed.add_field(
            name=f"🔵 Team B ({len(session.team_b)}/5)",
            value="\n".join(team_b_mentions) if team_b_mentions else "No players assigned",
            inline=True
        )
        
        if len(session.team_a) == 5 and len(session.team_b) == 5:
            embed.add_field(
                name="🎉 Ready to Start",
                value="Use `!start_picks` to begin the tournament match!",
                inline=False
            )
    
    else:  # 16 or 20 player tournament
        # Check all 4 team roles
        if not all([session.team_1_role_id, session.team_2_role_id, session.team_3_role_id, session.team_4_role_id]):
            await ctx.send("❌ All 4 tournament team roles not configured! Set TEAM_1_ROLE_ID through TEAM_4_ROLE_ID in .env!")
            return
        
        team_roles = [
            guild.get_role(session.team_1_role_id),
            guild.get_role(session.team_2_role_id),
            guild.get_role(session.team_3_role_id),
            guild.get_role(session.team_4_role_id)
        ]
        
        if not all(team_roles):
            await ctx.send("❌ One or more tournament team roles not found!")
            return
        
        # Clear all teams
        session.team_1 = []
        session.team_2 = []
        session.team_3 = []
        session.team_4 = []
        
        teams = [session.team_1, session.team_2, session.team_3, session.team_4]
        
        # Assign players to teams
        for member in guild.members:
            if member.bot:
                continue
            
            for i, role in enumerate(team_roles):
                if role in member.roles and len(teams[i]) < session.team_size:
                    teams[i].append(member.id)
                    break
        
        embed = discord.Embed(
            title="✅ Tournament Teams Assigned",
            description=f"{session.tournament_size}-player bracket tournament configured",
            color=0x00ff00
        )
        
        team_names = ["🟡 Team 1", "🔵 Team 2", "🟢 Team 3", "🔴 Team 4"]
        for i, team in enumerate(teams):
            team_mentions = [f"<@{uid}>" for uid in team]
            embed.add_field(
                name=f"{team_names[i]} ({len(team)}/{session.team_size})",
                value="\n".join(team_mentions) if team_mentions else "No players assigned",
                inline=True
            )
        
        total_assigned = sum(len(team) for team in teams)
        if total_assigned == session.tournament_size:
            embed.add_field(
                name="🎉 Ready for Small Matches",
                value="Use `!start_small_match 1` to begin the first bracket match!",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.command(name='start_small_match', help='Start a small tournament match (1 or 2) (Admin only)')
@is_admin()
async def start_small_match(ctx, match_number: int):
    if match_number not in [1, 2]:
        await ctx.send("❌ Match number must be 1 or 2!")
        return
    
    session = get_game_session(ctx.channel.id)
    
    if not session.tournament_mode or session.tournament_size == 10:
        await ctx.send("❌ This command is only for 16/20 player tournaments!")
        return
    
    if session.tournament_phase != "small_matches":
        await ctx.send("❌ Tournament is not in small matches phase!")
        return
    
    # Set up teams for the match
    if match_number == 1:
        session.team_a = session.team_1.copy()
        session.team_b = session.team_2.copy()
        team_names = "Team 1 vs Team 2"
    else:
        session.team_a = session.team_3.copy()
        session.team_b = session.team_4.copy()
        team_names = "Team 3 vs Team 4"
    
    session.small_match_current = match_number
    session.current_phase = "banning"
    session.phase_count = 0
    session.available_maps = VALORANT_MAPS.copy()
    session.banned_maps = []
    session.picked_maps = []
    session.banned_by = []
    session.picked_by = []
    
    # Randomly choose which team starts
    session.team_a_turn = random.choice([True, False])
    starting_team = "Team A" if session.team_a_turn else "Team B"
    
    embed = discord.Embed(
        title=f"🎯 Small Match {match_number} Started!",
        description=f"**{team_names}**\nBan until 1 map remains",
        color=0xe74c3c
    )
    
    embed.add_field(
        name="Match Format",
        value="Teams alternate banning maps until only 1 remains\nThat map will be played for this match",
        inline=False
    )
    
    embed.add_field(
        name="Starting Team",
        value=f"**{starting_team}** goes first",
        inline=False
    )
    
    # Log match start
    log_embed = discord.Embed(
        title=f"🎯 Small Match {match_number} Started",
        description=f"{team_names} - Ban phase initiated",
        color=0xe74c3c
    )
    await log_event(ctx.channel.id, log_embed)
    
    # Create small match view (ban only until 1 map left)
    selection_view = SmallMatchView(session, ctx.channel.id, starting_team, match_number)
    
    # Create maps embed
    maps_embed = selection_view.create_maps_embed()
    
    # Send the interactive interface
    maps_message = await ctx.send(embed=maps_embed)
    status_message = await ctx.send(embed=embed, view=selection_view)
    
    # Store message references in the view
    selection_view.status_message = status_message
    selection_view.maps_message = maps_message

@bot.command(name='set_match_winner', help='Set winner of small match and advance tournament (Admin only)')
@is_admin()
async def set_match_winner(ctx, match_number: int, winning_team: int):
    if match_number not in [1, 2]:
        await ctx.send("❌ Match number must be 1 or 2!")
        return
    
    if winning_team not in [1, 2, 3, 4]:
        await ctx.send("❌ Winning team must be 1, 2, 3, or 4!")
        return
    
    session = get_game_session(ctx.channel.id)
    
    if not session.tournament_mode or session.tournament_size == 10:
        await ctx.send("❌ This command is only for 16/20 player tournaments!")
        return
    
    # Validate the winning team matches the match
    if match_number == 1 and winning_team not in [1, 2]:
        await ctx.send("❌ Match 1 winner must be team 1 or 2!")
        return
    if match_number == 2 and winning_team not in [3, 4]:
        await ctx.send("❌ Match 2 winner must be team 3 or 4!")
        return
    
    # Set the winner
    if match_number == 1:
        session.match_1_winner = winning_team
    else:
        session.match_2_winner = winning_team
    
    embed = discord.Embed(
        title=f"✅ Match {match_number} Winner Set",
        description=f"**Team {winning_team}** wins small match {match_number}!",
        color=0x00ff00
    )
    
    # Check if we can start the final
    if session.match_1_winner and session.match_2_winner:
        session.tournament_phase = "finals"
        
        # Set up final teams
        if session.match_1_winner == 1:
            session.team_a = session.team_1.copy()
        else:
            session.team_a = session.team_2.copy()
        
        if session.match_2_winner == 3:
            session.team_b = session.team_3.copy()
        else:
            session.team_b = session.team_4.copy()
        
        embed.add_field(
            name="🏆 Finals Ready!",
            value=f"**Team {session.match_1_winner}** vs **Team {session.match_2_winner}**",
            inline=False
        )
        embed.add_field(
            name="Next Step",
            value="Use `!start_picks` to begin the tournament final!",
            inline=False
        )
    else:
        remaining_match = 2 if match_number == 1 else 1
        embed.add_field(
            name="Next Step",
            value=f"Use `!start_small_match {remaining_match}` to start the other bracket match",
            inline=False
        )
    
    # Log winner
    log_embed = discord.Embed(
        title=f"🏆 Match {match_number} Complete",
        description=f"Team {winning_team} wins small match {match_number}",
        color=0x00ff00
    )
    if session.match_1_winner and session.match_2_winner:
        log_embed.add_field(
            name="Finals Set",
            value=f"Team {session.match_1_winner} vs Team {session.match_2_winner}",
            inline=False
        )
    await log_event(ctx.channel.id, log_embed)
    
    await ctx.send(embed=embed)

# Custom View for small tournament matches (ban until 1 map remains)
class SmallMatchView(discord.ui.View):
    def __init__(self, session, channel_id, starting_team, match_number):
        super().__init__(timeout=600)  # 10 minute timeout for small matches
        self.session = session
        self.channel_id = channel_id
        self.starting_team = starting_team
        self.match_number = match_number
        self.status_message = None
        self.maps_message = None
        
        # Add buttons for each available map
        self.update_buttons()
    
    def update_buttons(self):
        # Clear existing buttons
        self.clear_items()
        
        # Add buttons for each available map (max 25 buttons per view)
        for i, map_name in enumerate(self.session.available_maps[:25]):
            button = discord.ui.Button(
                label=map_name,
                style=discord.ButtonStyle.secondary,
                custom_id=f"map_{i}",
                row=i // 5  # Distribute across 5 rows
            )
            button.callback = self.create_map_callback(map_name)
            self.add_item(button)
    
    def create_map_callback(self, map_name):
        async def map_callback(interaction: discord.Interaction):
            await self.handle_map_ban(interaction, map_name)
        return map_callback
    
    async def handle_map_ban(self, interaction: discord.Interaction, map_name: str):
        user_id = interaction.user.id
        
        # Check if user is in the correct team for their turn
        if self.session.team_a_turn and user_id not in self.session.team_a:
            await interaction.response.send_message(
                "❌ It's Team A's turn to ban!", 
                ephemeral=True
            )
            return
        elif not self.session.team_a_turn and user_id not in self.session.team_b:
            await interaction.response.send_message(
                "❌ It's Team B's turn to ban!", 
                ephemeral=True
            )
            return
        
        # Ban the map
        self.session.available_maps.remove(map_name)
        self.session.banned_maps.append(map_name)
        current_team = "Team A" if self.session.team_a_turn else "Team B"
        self.session.banned_by.append(current_team)
        
        await interaction.response.send_message(
            f"✅ **{current_team}** banned **{map_name}**!", 
            ephemeral=True
        )
        
        # Log the ban
        log_embed = discord.Embed(
            title=f"🚫 Map Banned - Small Match {self.match_number}",
            description=f"**{current_team}** banned **{map_name}**",
            color=0xe74c3c
        )
        log_embed.add_field(
            name="Player",
            value=interaction.user.mention,
            inline=True
        )
        await log_event(self.channel_id, log_embed)
        
        # Check if only 1 map remains
        if len(self.session.available_maps) == 1:
            await self.finish_small_match()
        else:
            # Switch turns and continue banning
            self.session.team_a_turn = not self.session.team_a_turn
            await self.update_embeds()
    
    async def finish_small_match(self):
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        final_map = self.session.available_maps[0]
        
        embed = discord.Embed(
            title=f"🎯 Small Match {self.match_number} Map Decided!",
            description=f"**{final_map}** will be played",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Banned Maps",
            value=", ".join(self.session.banned_maps),
            inline=False
        )
        
        embed.add_field(
            name="Next Step",
            value=f"Play the match on **{final_map}**\n"
                  f"When complete, admin should use:\n"
                  f"`!set_match_winner {self.match_number} <winning_team>`",
            inline=False
        )
        
        # Log match completion
        log_embed = discord.Embed(
            title=f"🎯 Small Match {self.match_number} Map Selected",
            description=f"Map decided: **{final_map}**",
            color=0x00ff00
        )
        log_embed.add_field(
            name="Banned Maps",
            value=", ".join(self.session.banned_maps),
            inline=False
        )
        await log_event(self.channel_id, log_embed)
        
        try:
            await self.status_message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass
    
    def create_maps_embed(self):
        embed = discord.Embed(
            title=f"🎯 Small Match {self.match_number} - Ban Phase",
            description="Ban maps until only 1 remains",
            color=0x9b59b6
        )
        
        # Show banned maps
        if self.session.banned_maps:
            banned_text = ""
            for i, map_name in enumerate(self.session.banned_maps):
                team_name = self.session.banned_by[i]
                banned_text += f"{i+1}. 🚫 **{map_name}** (banned by {team_name})\n"
            
            embed.add_field(
                name="🚫 Banned Maps",
                value=banned_text,
                inline=False
            )
        
        # Show remaining maps
        if len(self.session.available_maps) > 1:
            embed.add_field(
                name="📊 Progress",
                value=f"{len(self.session.available_maps)} maps remaining\n"
                      f"Ban until 1 map left",
                inline=True
            )
        
        return embed
    
    async def update_embeds(self):
        # Update buttons
        self.update_buttons()
        
        # Update status
        current_team = "Team A" if self.session.team_a_turn else "Team B"
        status_embed = discord.Embed(
            title=f"🎯 Small Match {self.match_number} - Ban Phase",
            description=f"**{current_team}**'s turn to ban",
            color=0xe74c3c
        )
        
        status_embed.add_field(
            name="📋 Progress", 
            value=f"Maps remaining: {len(self.session.available_maps)}",
            inline=True
        )
        
        # Update maps embed
        maps_embed = self.create_maps_embed()
        
        try:
            await self.status_message.edit(embed=status_embed, view=self)
            await self.maps_message.edit(embed=maps_embed)
        except discord.NotFound:
            pass
    
    async def on_timeout(self):
        # Disable buttons when timeout occurs
        for item in self.children:
            item.disabled = True
        
        embed = discord.Embed(
            title="⏰ Small Match Timeout",
            description=f"Small match {self.match_number} has timed out.",
            color=0x95a5a6
        )
        
        try:
            await self.status_message.edit(embed=embed, view=self)
        except discord.NotFound:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        # Don't respond to unknown commands to avoid spam
        return
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("❌ You don't have permission to use this command!")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument provided!")
    else:
        print(f"Unexpected error: {error}")
        await ctx.send("❌ An unexpected error occurred!")

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("Error: DISCORD_TOKEN not found in .env file!")
        print("Please create a .env file based on .env.example")
    else:
        bot.run(token)