import os
import requests
import base64
import re
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

# ItemTypeIDs from docs
ITEM_TYPE_IDS = {
	"Cards": "3f296c07-64c3-494c-923b-fe692a4fa1bd",
	"Titles": "de7caa6b-adf7-4588-bbd1-143831e786c6",
}

# Fetch public item data for name resolution
titles_data = requests.get("https://valorant-api.com/v1/playertitles").json()["data"]
playercards_data = requests.get("https://valorant-api.com/v1/playercards").json()["data"]



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

def resolve_item_name(item_type, item_id):
	if item_type == "Titles":
		return get_title_name(item_id)
	elif item_type == "Cards":
		return get_playercard_name(item_id)

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




def main():
	card_id = "41244f42-43f5-f795-9be8-d2b9edba458a"
	title_id = "6b4e1d0c-410e-878b-f151-9b8a8abc83a3"

	# Get display names
	card_name = get_playercard_name(card_id)
	title_name = get_title_name(title_id)

	# Check card
	cards_data = get_owned_items(ITEM_TYPE_IDS["Cards"])
	has_card = False
	if cards_data:
		for item in cards_data.get("Entitlements", []):
			if item.get("ItemID") == card_id:
				has_card = True
				break
	print(f"Has card '{card_name}' ({card_id}): {has_card}")

	# Check title
	titles_data = get_owned_items(ITEM_TYPE_IDS["Titles"])
	has_title = False
	if titles_data:
		for item in titles_data.get("Entitlements", []):
			if item.get("ItemID") == title_id:
				has_title = True
				break
	print(f"Has title '{title_name}' ({title_id}): {has_title}")

if __name__ == "__main__":
	main()
