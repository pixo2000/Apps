# ValoPickBot 🎯

A Discord bot for managing Valorant map picks in Best of 3 matches, following competitive tournament format.

## Features

- **Team Setup**: Support for 4v4 and 5v5 matches
- **Map Ban/Pick Phase**: Automated tournament-style map selection
- **Voting System**: Final map selection with team voting
- **Admin Controls**: Admin users can manage teams and sessions
- **Real-time Status**: Track current phase, teams, and map pool

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create Discord Bot**
   - Go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application and bot
   - Copy the bot token

3. **Configure Environment**
   - Copy `.env.example` to `.env`
   - Fill in your Discord bot token and admin user IDs
   - Optionally configure team roles and logging channel for auto-loading
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ADMIN_USER_1=your_discord_user_id_1
   ADMIN_USER_2=your_discord_user_id_2  
   ADMIN_USER_3=your_discord_user_id_3
   
   # Optional: Auto-load team roles
   TEAM_A_ROLE_ID=your_team_a_role_id
   TEAM_B_ROLE_ID=your_team_b_role_id
   
   # Optional: Auto-load logging channel
   LOGGING_SERVER_ID=your_server_id
   LOGGING_CHANNEL_ID=your_logging_channel_id
   ```

4. **Run the Bot**
   ```bash
   python main.py
   ```

## How to Use

### 1. Setup Phase
- **Manual**: Admins use `!setup_teams 5` (or `!setup_teams 4` for 4v4), players join with `!join_team a/b`
- **Role-based**: Admins set team roles with `!set_team_roles <role_id_a> <role_id_b>`, then use `!assign_by_roles`
- Use `!teams` to check current teams

### 2. Map Selection Process
- When teams are full, use `!start_picks` to begin
- **Interactive Interface**: Map selection uses interactive buttons instead of commands
- **Ban Phase**: Each team alternates banning 2 maps (4 total bans) using buttons
- **Pick Phase**: Each team picks 1 map (2 total picks) using buttons  
- **Final Map**: Random map is selected, teams vote to accept/reject using buttons
- **No Chat Spam**: All interactions update existing embeds instead of creating new messages

### 3. Commands Reference

#### Basic Commands
- `!help_valo` - Show all commands
- `!join_team <a|b>` - Join team A or B
- `!teams` - Show current teams
- `!maps` - Show all available maps
- `!status` - Show current game status

#### Game Commands
- `!start_picks` - Start interactive map selection process
- `!start_picks force` - Force start with incomplete teams
- Interactive buttons appear automatically for bans, picks, and voting

#### Admin Commands
- `!setup_teams <4|5>` - Setup team size
- `!force_team <user> <a|b>` - Force assign user to team
- `!force_reset` - Reset session
- `!set_team_roles <team_a_role_id> <team_b_role_id>` - Set Discord roles for teams
- `!assign_by_roles` - Auto-assign users to teams based on roles
- `!assign_default_roles` - Use role IDs from .env file
- `!set_logging_channel <channel>` - Set logging channel for game events
- `!reload_config` - Reload configurations from .env file
- `!show_config` - Show current auto-loaded configurations

## Auto-Loading Features

The bot can automatically load configurations from the `.env` file:

### Team Role Auto-Assignment
- Set `TEAM_A_ROLE_ID` and `TEAM_B_ROLE_ID` in `.env`
- Bot will automatically configure team roles for new sessions
- Use `!assign_by_roles` to instantly assign all users with those roles

### Cross-Server Logging
- Set `LOGGING_SERVER_ID` and `LOGGING_CHANNEL_ID` in `.env`
- Bot will automatically log game events to the specified channel
- Supports logging to channels in different servers
- All bans, picks, votes, and team assignments are logged

### Configuration Management
- `!reload_config` - Reload settings from `.env` without restarting bot
- `!show_config` - View current auto-loaded configurations
- Settings persist across session resets

## Map Pool

The bot includes all current Valorant competitive maps:
- Bind, Haven, Split, Ascent
- Icebox, Breeze, Fracture, Pearl
- Lotus, Sunset, Abyss, Corrode

## Tournament Format

Following standard competitive format:
1. Random team selection for first action
2. Team A ban → Team B ban → Team A ban → Team B ban
3. Team A pick → Team B pick  
4. Random final map selection + team voting
5. If 50%+ vote yes, map is played; otherwise new random map

## Admin Features

- Only designated admin users can setup teams
- Admins can force assign players to teams
- Admins can force reset sessions
- Admin IDs are configured in the `.env` file

## Error Handling

The bot includes comprehensive error handling for:
- Invalid commands and arguments
- Permission checks
- Game state validation
- User input validation

## Support

For issues or questions, check the command help with `!help_valo` or refer to this README.
