
import os
import requests
import base64
import re

# Get lockfile info from Riot Client
LOCKFILE_PATH = os.path.expandvars(r'%LOCALAPPDATA%/Riot Games/Riot Client/Config/lockfile')
if not os.path.exists(LOCKFILE_PATH):
    print("Valorant is not running or lockfile not found!")
    exit(1)
with open(LOCKFILE_PATH) as f:
    lock = f.read().split(':')
    lock_info = dict(zip(['name', 'PID', 'port', 'password', 'protocol'], lock))

# Get entitlement and access tokens
local_headers = {
    'Authorization': 'Basic ' + base64.b64encode(f"riot:{lock_info['password']}".encode()).decode()
}
url = f"https://127.0.0.1:{lock_info['port']}/entitlements/v1/token"
resp = requests.get(url, headers=local_headers, verify=False)
if resp.status_code != 200:
    print("Failed to get entitlement token!")
    exit(1)
tokens = resp.json()
access_token = tokens['accessToken']
entitlement_token = tokens['token']
puuid = tokens['subject']

# Get region/shard and client version from ShooterGame.log
LOG_PATH = os.path.expandvars(r'%LOCALAPPDATA%/VALORANT/Saved/Logs/ShooterGame.log')
shard = None
client_version = None
with open(LOG_PATH, encoding='utf8') as f:
    for line in f:
        if '.a.pvp.net/account-xp/v1/' in line:
            shard = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
        if 'CI server version:' in line:
            client_version = line.split('CI server version: ')[1].strip().split('-')[0]
        if shard and client_version:
            break
if not shard:
    print("Could not determine region/shard from log!")
    exit(1)
if not client_version:
    print("Could not determine client version from log!")
    exit(1)

# Provided client platform string (base64 encoded JSON)
client_platform = "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9"

# Build request to Valorant API
loadout_url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
headers = {
    "X-Riot-ClientPlatform": client_platform,
    "X-Riot-ClientVersion": client_version,
    "X-Riot-Entitlements-JWT": entitlement_token,
    "Authorization": f"Bearer {access_token}",
}

resp = requests.get(loadout_url, headers=headers)
if resp.status_code != 200:
    print(f"Error: {resp.status_code} - {resp.text}")
    exit(1)
loadout = resp.json()



# Fetch skin, chroma, buddy, spray, title, and playercard data from Valorant public API
skins_data = requests.get("https://valorant-api.com/v1/weapons/skins").json()["data"]
charms_data = requests.get("https://valorant-api.com/v1/buddies").json()["data"]
sprays_data = requests.get("https://valorant-api.com/v1/sprays").json()["data"]
titles_data = requests.get("https://valorant-api.com/v1/playertitles").json()["data"]
playercards_data = requests.get("https://valorant-api.com/v1/playercards").json()["data"]


def get_chroma_name(skin_id, chroma_id):
    for skin in skins_data:
        if skin["uuid"] == skin_id:
            for chroma in skin.get("chromas", []):
                if chroma["uuid"] == chroma_id:
                    return chroma["displayName"]
    return chroma_id

def get_buddy_name(buddy_id):
    for buddy in charms_data:
        if buddy["uuid"] == buddy_id:
            return buddy["displayName"]
    return buddy_id

def get_spray_name(spray_id):
    for spray in sprays_data:
        if spray["uuid"] == spray_id:
            return spray["displayName"]
    return spray_id

def get_title_name(title_id):
    for title in titles_data:
        if title["uuid"] == title_id:
            return title["titleText"]
    return title_id

def get_playercard_name(card_id):
    for card in playercards_data:
        if card["uuid"] == card_id:
            return card["displayName"]
    return card_id


print("\nYour Valorant Loadout:")

def get_gun_name(gun_id):
    for skin in skins_data:
        if skin["uuid"] == gun_id:
            return skin.get("weapon", gun_id)
    # fallback: try weapon API
    weapon_data = requests.get("https://valorant-api.com/v1/weapons").json()["data"]
    for weapon in weapon_data:
        if weapon["uuid"] == gun_id:
            return weapon["displayName"]
    return gun_id


def get_skin_base_name(skin_id):
    for skin in skins_data:
        if skin["uuid"] == skin_id:
            name = skin["displayName"]
            # Remove weapon name and level info from skin name
            # Example: "RGX 11z Pro Sheriff Level 5" -> "RGX 11z Pro"
            weapon_names = ["Classic", "Shorty", "Frenzy", "Ghost", "Sheriff", "Stinger", "Spectre", "Bucky", "Judge", "Bulldog", "Guardian", "Phantom", "Vandal", "Marshal", "Outlaw", "Operator", "Ares", "Odin", "Melee"]
            for w in weapon_names:
                if name.endswith(f" {w}"):
                    name = name[:-(len(w)+1)]
            # Remove trailing " Level X" if present
            import re
            name = re.sub(r" Level \d+$", "", name)
            return name
    return skin_id

def get_skin_level(skin_id, skin_level_id):
    for skin in skins_data:
        if skin["uuid"] == skin_id:
            for level_idx, level in enumerate(skin.get("levels", [])):
                if level["uuid"] == skin_level_id:
                    # Level index is 0-based, add 1
                    return f"Level {level_idx+1}"
    return None

def get_variant(skin_id, chroma_id):
    for skin in skins_data:
        if skin["uuid"] == skin_id:
            for idx, chroma in enumerate(skin.get("chromas", [])):
                if chroma["uuid"] == chroma_id:
                    # Variant index is 0-based, add 1
                    variant_str = f"Variant {idx+1}: "
                    # Only add name if not "Base"
                    if chroma["displayName"] and chroma["displayName"].lower() != "base":
                        variant_str += chroma["displayName"]
                    else:
                        variant_str += "Base"
                    return variant_str
    return None



for gun in loadout.get("Guns", []):
    gun_name = get_gun_name(gun["ID"])
    print(f"{gun_name}:")
    # Skin: Skinname (strip gun name and level from skinname)
    skin_base = get_skin_base_name(gun["SkinID"])
    print(f"- Skin: {skin_base}")
    # Skinlevel: X
    skin_level = get_skin_level(gun["SkinID"], gun["SkinLevelID"])
    if skin_level:
        print(f"- Skinlevel: {skin_level.split(' ')[-1]}")
    # Variant: Color(Number)
    variant_name = None
    variant_num = None
    for skin in skins_data:
        if skin["uuid"] == gun["SkinID"]:
            skin_base = get_skin_base_name(gun["SkinID"])
            for idx, chroma in enumerate(skin.get("chromas", [])):
                if chroma["uuid"] == gun["ChromaID"]:
                    vname = chroma["displayName"]
                    # Extract color from parentheses if present
                    color = None
                    match = re.search(r"\(([^)]*)\)", vname)
                    if match:
                        parts = match.group(1).split()
                        if len(parts) >= 3:
                            color = parts[2]
                        elif len(parts) >= 1:
                            color = parts[-1]
                    # Remove gun name and level from variant name
                    for w in ["Classic", "Shorty", "Frenzy", "Ghost", "Sheriff", "Stinger", "Spectre", "Bucky", "Judge", "Bulldog", "Guardian", "Phantom", "Vandal", "Marshal", "Outlaw", "Operator", "Ares", "Odin", "Melee"]:
                        if vname.endswith(f" {w}"):
                            vname = vname[:-(len(w)+1)]
                    vname = re.sub(r" Level \d+$", "", vname)
                    # If variant name is empty or 'Base', use 'Base'
                    if not vname or vname.lower() == "base":
                        vname = "Base"
                    variant_num = idx + 1
                    # If color matches skin name or is empty, print Standart(1)
                    if (color and color == skin_base) or (not color) or (color.strip() == ""):
                        print(f"- Variant: Standart(1)")
                    else:
                        print(f"- Variant: {color}({variant_num})")
                    break
            break
    if gun.get('CharmID'):
        buddy_name = get_buddy_name(gun['CharmID'])
        buddy_stripped = ' '.join(buddy_name.split()[:-1]) if len(buddy_name.split()) > 1 else buddy_name
        print(f"- Buddy: {buddy_stripped}")
    print()



print("Sprays:")
for spray in loadout.get("Sprays", []):
    spray_name = get_spray_name(spray['SprayID'])
    spray_stripped = ' '.join(spray_name.split()[:-1]) if len(spray_name.split()) > 1 else spray_name
    if spray_stripped == "VALORANT":
        print(f"- {spray_stripped} (could also be a flex)")
    else:
        print(f"- {spray_stripped}")

print()
identity = loadout.get("Identity", {})
print("Title:")
print(f"- {get_title_name(identity.get('PlayerTitleID'))}")

print()
print("PlayerCard:")
playercard_name = get_playercard_name(identity.get('PlayerCardID'))
playercard_stripped = ' '.join(playercard_name.split()[:-1]) if len(playercard_name.split()) > 1 else playercard_name
print(f"- {playercard_stripped}")
if identity.get('HideAccountLevel'):
    print("- Account Level is hidden")
