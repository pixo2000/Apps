import os
import requests
import base64
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

ITEM_TYPE_IDS = {
    "Cards": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
    "Titles": "de7caa6b-adf7-4588-bbd1-143831e786c6",
}

# IDs to check and equip
card_id = "41244f42-43f5-f795-9be8-d2b9edba458a"
title_id = "6b4e1d0c-410e-878b-f151-9b8a8abc83a3"

# Fetch public item data for name resolution
playercards_data = requests.get("https://valorant-api.com/v1/playercards").json()["data"]
titles_data = requests.get("https://valorant-api.com/v1/playertitles").json()["data"]

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

def get_owned_items(item_type_id):
    url = f"https://pd.{shard}.a.pvp.net/store/v1/entitlements/{puuid}/{item_type_id}"
    headers = {
        "X-Riot-ClientPlatform": client_platform,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch items for {item_type_id}: {response.status_code}")
        return None

def has_item(item_type, item_id):
    data = get_owned_items(ITEM_TYPE_IDS[item_type])
    if data:
        for item in data.get("Entitlements", []):
            if item.get("ItemID") == item_id:
                return True
    return False

def get_current_identity(verbose=True):
    loadout_url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
    headers = {
        "X-Riot-ClientPlatform": client_platform,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
    }
    resp = requests.get(loadout_url, headers=headers)
    if resp.status_code != 200:
        print(f"Error fetching current loadout: {resp.status_code}")
        return None
    loadout = resp.json()
    identity = loadout.get("Identity", {})
    if verbose:
        card = get_playercard_name(identity.get("PlayerCardID", ""))
        title = get_title_name(identity.get("PlayerTitleID", ""))
        hide_level = identity.get("HideAccountLevel", False)
        print("Current Card:", card)
        print("Current Title:", title)
        print("Hide Account Level:", hide_level)
    return identity, loadout

def equip_items(card_id, title_id, save_old=True):
    identity, loadout = get_current_identity()
    if identity is None:
        return False
    # Save old identity before changing
    if save_old:
        old_identity_path = os.path.join(os.path.dirname(__file__), "old_identity.json")
        with open(old_identity_path, "w", encoding="utf-8") as f:
            json.dump({
                "PlayerCardID": identity.get("PlayerCardID", ""),
                "PlayerTitleID": identity.get("PlayerTitleID", ""),
                "HideAccountLevel": identity.get("HideAccountLevel", False)
            }, f)
    identity["PlayerCardID"] = card_id
    identity["PlayerTitleID"] = title_id
    identity["HideAccountLevel"] = True
    new_loadout = {
        "Guns": loadout.get("Guns", []),
        "Sprays": loadout.get("Sprays", []),
        "Identity": identity,
        "Incognito": loadout.get("Incognito", False)
    }
    loadout_url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
    headers = {
        "X-Riot-ClientPlatform": client_platform,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    put_resp = requests.put(loadout_url, headers=headers, data=json.dumps(new_loadout))
    if put_resp.status_code == 200:
        print("Successfully equipped the specified card and title, and hid account level!")
        return True
    else:
        print(f"Failed to equip items: {put_resp.status_code} - {put_resp.text}")
        return False

def restore_old_identity():
    old_identity_path = os.path.join(os.path.dirname(__file__), "old_identity.json")
    if not os.path.exists(old_identity_path):
        print("No saved identity to restore.")
        return False
    with open(old_identity_path, "r", encoding="utf-8") as f:
        old_identity = json.load(f)
    identity, loadout = get_current_identity(verbose=False)
    if identity is None:
        return False
    identity["PlayerCardID"] = old_identity.get("PlayerCardID", "")
    identity["PlayerTitleID"] = old_identity.get("PlayerTitleID", "")
    identity["HideAccountLevel"] = old_identity.get("HideAccountLevel", False)
    new_loadout = {
        "Guns": loadout.get("Guns", []),
        "Sprays": loadout.get("Sprays", []),
        "Identity": identity,
        "Incognito": loadout.get("Incognito", False)
    }
    loadout_url = f"https://pd.{shard}.a.pvp.net/personalization/v2/players/{puuid}/playerloadout"
    headers = {
        "X-Riot-ClientPlatform": client_platform,
        "X-Riot-ClientVersion": client_version,
        "X-Riot-Entitlements-JWT": entitlement_token,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    put_resp = requests.put(loadout_url, headers=headers, data=json.dumps(new_loadout))
    if put_resp.status_code == 200:
        print("Successfully restored old identity!")
        return True
    else:
        print(f"Failed to restore old identity: {put_resp.status_code} - {put_resp.text}")
        return False

import time
import sys
import signal

def main():
    def on_exit(signum=None, frame=None):
        print("\nRestoring old identity before exit...")
        restore_old_identity()
        print("Exiting.")
        sys.exit(0)

    if len(sys.argv) > 1 and sys.argv[1].lower() == "restore":
        restore_old_identity()
        return

    # Register signal handler for graceful exit
    signal.signal(signal.SIGINT, on_exit)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, on_exit)

    # Initial setup and equip
    owns_card = has_item("Cards", card_id)
    owns_title = has_item("Titles", title_id)
    if not owns_card:
        print(f"You do not own the required card ({card_id})!")
    if not owns_title:
        print(f"You do not own the required title ({title_id})!")
    if owns_card and owns_title:
        equip_items(card_id, title_id, save_old=True)
    else:
        print("Cannot equip: missing required items.")
        return

    print("Program is now running. Press Ctrl+C to stop and restore old identity.")
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        on_exit()

if __name__ == "__main__":
    main()
