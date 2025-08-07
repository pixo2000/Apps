# Ghünter - Valorant Premier League Discord Bot

A Discord bot that monitors Valorant Premier League matches for the "Carings Baes" team and provides real-time notifications and statistics.

## Features

- **Automatic Match Monitoring**: Checks for new Premier League matches every 30 seconds
- **Real-time Notifications**: Sends detailed match results to a designated Discord channel
- **Match Statistics**: Shows player performance, KDA, ACS, and team results
- **Match History**: View recent match history with points tracking
- **Current Points**: Check current Premier League points
- **Command Logging**: Logs all command usage to a designated channel for monitoring

## Commands

### User Commands

- `!latest` - Show the latest match result with detailed stats
- `!lookup <team_name> <team_tag>` - Look up the latest match for any Premier team
- `!history [limit]` - Show recent match history (max 10 matches)
- `!points` - Show current Premier League points
- `!status` - Show bot and API status information
- `!help_valorant` - Show all available commands

### Admin Commands

- `!setchannel` - Set current channel for automatic match notifications
- `!setlogchannel` - Set current channel for command logging
- `!disablelog` - Disable command logging

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Make sure your `.env` file contains:
   ```
   BOT-TOKEN=your_discord_bot_token
   HDEV_API_KEY=your_henrik_api_key
   ```

3. **Run the Bot**:
   ```bash
   python main.py
   ```

## Configuration

- **Team Name**: "Carings Baes"
- **Team Tag**: "CarBa"
- **Check Interval**: 30 seconds
- **API**: Henrik Dev Valorant API

## Command Logging

The bot includes a comprehensive logging system that tracks all command usage:

### Setting Up Logging
1. Use `!setlogchannel` in the channel where you want logs to appear
2. The bot will log every command execution with detailed information
3. Use `!disablelog` to turn off logging when needed

### What Gets Logged
- **User Information**: Who executed the command (name, mention, ID)
- **Location**: Server name and channel name
- **Command Details**: Exact command with parameters
- **Status**: Success (green), Error (red), or Warning (yellow)
- **Timestamps**: When the command was executed
- **Additional Context**: Match IDs, points, error messages, etc.
- **Reference IDs**: User ID and message ID for tracking

### Log Format
Each log entry appears as a colored embed with:
```
✅ Command Executed
👤 User: @Username (Username#1234)
📍 Location: Server Name / #channel-name
⚡ Command: !latest
ℹ️ Details: Match ID: abc123...
```

## Bot Permissions Required

- Send Messages
- Embed Links
- Read Message History
- Use Slash Commands (optional)

## Example Usage

The bot will automatically monitor for new matches and send notifications like this:

```
🎮 New Carings Baes Match Result!

📍 Map: Ascent
🎯 Final Score: 13 - 11
🏆 Result: VICTORY ✅
🔴 Enemy Team: Enemy Team#TAG
💰 Points (+25): 250 → 275

👥 Our Team (sorted by performance):
• Player1#TAG (Jett) - 25/15/3 | 280 ACS
• Player2#TAG (Sage) - 18/12/8 | 200 ACS
• Player3#TAG (Omen) - 15/14/12 | 180 ACS
• Player4#TAG (Sova) - 20/11/7 | 220 ACS
• Player5#TAG (Breach) - 12/16/15 | 150 ACS
```

## Troubleshooting

- Ensure your API key is valid and has proper permissions
- Check that the bot has necessary Discord permissions in your server
- Verify the team name and tag match exactly in the API
- Monitor console output for error messages

## API Credits

This bot uses the [Henrik Dev Valorant API](https://docs.henrikdev.xyz/valorant.html) for fetching match data.
