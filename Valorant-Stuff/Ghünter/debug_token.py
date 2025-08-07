import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

bot_token = os.getenv('BOT_TOKEN')

print("🔍 Discord Bot Token Analysis")
print("=" * 40)
print(f"Token loaded: {bool(bot_token)}")
if bot_token:
    print(f"Token length: {len(bot_token)}")
    print(f"Token preview: {bot_token[:20]}...")
    
    # Check token format
    parts = bot_token.split('.')
    print(f"Token parts: {len(parts)} (should be 3)")
    
    if len(parts) == 3:
        print(f"Part 1 length: {len(parts[0])} (Bot ID)")
        print(f"Part 2 length: {len(parts[1])} (Creation timestamp)")
        print(f"Part 3 length: {len(parts[2])} (HMAC signature)")
        print("✅ Token format looks correct")
    else:
        print("❌ Invalid token format - should have 3 parts separated by dots")
        
print("\n📝 To fix this issue:")
print("1. Go to https://discord.com/developers/applications")
print("2. Select your bot application")
print("3. Go to 'Bot' section")
print("4. Click 'Reset Token' to generate a new token")
print("5. Copy the new token and update the .env file")
print("6. Make sure your bot has the required permissions and is invited to servers")
