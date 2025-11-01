import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime, timedelta
import asyncio

# Environment-Variablen laden
load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD-TOKEN')
API_KEY = os.getenv('API-KEY')

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Datenpfade
DATA_FILE = 'cup_data.json'
PLAYERS_FILE = 'players.json'

# Channel IDs (müssen angepasst werden)
ANNOUNCEMENT_CHANNEL_ID = None  # Hier die Channel-ID für die Hauptankündigung eintragen
VOTE_CHANNEL_ID = None  # Hier die Channel-ID für die Votes eintragen
PLAYER_LIST_CHANNEL_ID = None  # Hier die Channel-ID für die Spielerliste eintragen

# Initialisiere Datendateien
def init_data():
    if not os.path.exists(DATA_FILE):
        data = {
            'current_cup': None,
            'current_vote': None,
            'announcement_message_id': None,
            'vote_message_id': None,
            'player_list_message_id': None,
            'winner_team': []
        }
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    if not os.path.exists(PLAYERS_FILE):
        players = {
            'players': [],
            'max_players': 10
        }
        with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(players, f, indent=4, ensure_ascii=False)

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_players():
    with open(PLAYERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_players(players):
    with open(PLAYERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(players, f, indent=4, ensure_ascii=False)

# Valorant Rank abrufen
async def get_valorant_rank(name, tag):
    try:
        url = f"https://api.henrikdev.xyz/valorant/v2/mmr/eu/{name}/{tag}"
        headers = {
            "Authorization": API_KEY,
            "Accept": "*/*"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 200:
                current_rank = data['data']['current_data']['currenttier_patched']
                highest_rank = data['data']['highest_rank']['patched_tier']
                return current_rank, highest_rank
        return None, None
    except Exception as e:
        print(f"Fehler beim Abrufen des Ranks: {e}")
        return None, None

# Regeln-Embed erstellen
def create_rules_embed():
    embed = discord.Embed(
        title="📋 Valorant Raph Cup - Regeln",
        description="Hier sind alle wichtigen Regeln für das Turnier:",
        color=discord.Color.red()
    )
    
    embed.add_field(
        name="🔫 Verbotene Waffen",
        value="• **Odin** - Verboten\n• **Operator** - Verboten\n\nBei Nutzung: Verwarnung + Rundenabzug + Gegner bekommt Rundenwin",
        inline=False
    )
    
    embed.add_field(
        name="⚠️ Verwarnungssystem",
        value="• 2-3 Verwarnungen = Disqualifikation\n• Hacken/Cheaten = Sofortige Disqualifikation\n• Alle Valorant-Meldegründe sind verboten",
        inline=False
    )
    
    embed.add_field(
        name="🔌 Disconnect",
        value="Bei Internetproblemen oder Launcher-Crash wird das Match pausiert bis der Spieler zurück ist.",
        inline=False
    )
    
    embed.add_field(
        name="🏆 Preis",
        value="**10 Euro Guthaben** pro Spieler des Gewinnerteams (Riot, Steam, etc.)",
        inline=False
    )
    
    embed.add_field(
        name="👥 Teamgrößen",
        value="• 10 Spieler: 2x5 Teams (Best of 3)\n• 16 Spieler: 4x4 Teams (Bo1 + Bo3)\n• 20 Spieler: 4x5 Teams (Bo1 + Bo3)",
        inline=False
    )
    
    embed.set_footer(text="Viel Erfolg beim Turnier! 🎮")
    return embed

# Cup-Ankündigungs-Embed erstellen
def create_announcement_embed(data):
    embed = discord.Embed(
        title="🏆 Valorant Raph Cup",
        color=discord.Color.gold()
    )
    
    if data['current_cup']:
        cup_date = datetime.fromisoformat(data['current_cup'])
        embed.description = f"**Nächstes Turnier:**\n📅 {cup_date.strftime('%d.%m.%Y')} um 20:30 Uhr"
        embed.add_field(
            name="📝 Anmeldung",
            value="Klicke auf den **Anmelden**-Button, um teilzunehmen!",
            inline=False
        )
    elif data['winner_team'] and len(data['winner_team']) > 0:
        winners = '\n'.join([f"🏅 {player['discord_name']}" for player in data['winner_team']])
        embed.description = f"**Letzte Gewinner:**\n{winners}"
        embed.add_field(
            name="⏳ Nächster Cup",
            value="Das Datum wird bald bekannt gegeben!",
            inline=False
        )
    else:
        embed.description = "**Willkommen zum Raph Cup!**\nDas nächste Turnier wird bald angekündigt."
    
    embed.set_footer(text="Klicke auf 'Regeln' für alle Details | Klicke auf 'Anmelden' zur Registrierung")
    embed.set_thumbnail(url="https://i.imgur.com/xk86Usx.png")  # Valorant Logo
    return embed

# Buttons für Ankündigung
class AnnouncementButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📋 Regeln", style=discord.ButtonStyle.primary, custom_id="rules_button")
    async def rules_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = create_rules_embed()
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(label="✅ Anmelden", style=discord.ButtonStyle.success, custom_id="register_button")
    async def register_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RegistrationModal()
        await interaction.response.send_modal(modal)

# Anmeldungs-Modal
class RegistrationModal(discord.ui.Modal, title="Turnier-Anmeldung"):
    valorant_name = discord.ui.TextInput(
        label="Valorant Name",
        placeholder="Dein Riot-Name (ohne #Tag)",
        required=True,
        max_length=16
    )
    
    valorant_tag = discord.ui.TextInput(
        label="Valorant Tag",
        placeholder="Dein Riot-Tag (ohne #)",
        required=True,
        max_length=5
    )
    
    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Lade Spielerdaten
        players_data = load_players()
        
        # Prüfe ob bereits angemeldet
        discord_id = str(interaction.user.id)
        if any(p['discord_id'] == discord_id for p in players_data['players']):
            await interaction.followup.send("❌ Du bist bereits angemeldet!", ephemeral=True)
            return
        
        # Hole Rank-Informationen
        current_rank, highest_rank = await get_valorant_rank(
            self.valorant_name.value, 
            self.valorant_tag.value
        )
        
        if not current_rank:
            await interaction.followup.send(
                "❌ Konnte deinen Valorant-Account nicht finden. Bitte überprüfe deinen Namen und Tag!",
                ephemeral=True
            )
            return
        
        # Spieler hinzufügen
        player = {
            'discord_id': discord_id,
            'discord_name': str(interaction.user),
            'valorant_name': self.valorant_name.value,
            'valorant_tag': self.valorant_tag.value,
            'current_rank': current_rank,
            'highest_rank': highest_rank,
            'timestamp': datetime.now().isoformat()
        }
        
        players_data['players'].append(player)
        save_players(players_data)
        
        # Bestimme Status
        player_count = len(players_data['players'])
        if player_count <= 10:
            status = "✅ Regulärer Spieler"
        elif 10 < player_count <= 16:
            if player_count <= 16:
                players_data['max_players'] = 16
                save_players(players_data)
                status = "✅ Regulärer Spieler (16er-Modus aktiviert)"
            else:
                status = "⏳ Ersatzspieler"
        elif 16 < player_count <= 20:
            if player_count <= 20:
                players_data['max_players'] = 20
                save_players(players_data)
                status = "✅ Regulärer Spieler (20er-Modus aktiviert)"
            else:
                status = "⏳ Ersatzspieler"
        else:
            status = "⏳ Ersatzspieler"
        
        # Erfolgsmeldung
        embed = discord.Embed(
            title="✅ Anmeldung erfolgreich!",
            color=discord.Color.green()
        )
        embed.add_field(name="Valorant Account", value=f"{self.valorant_name.value}#{self.valorant_tag.value}", inline=False)
        embed.add_field(name="Aktueller Rank", value=current_rank, inline=True)
        embed.add_field(name="Höchster Rank", value=highest_rank, inline=True)
        embed.add_field(name="Status", value=status, inline=False)
        embed.set_footer(text="Viel Erfolg beim Turnier! 🎮")
        
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Aktualisiere Spielerliste
        await update_player_list(interaction.client)

# Spielerliste aktualisieren
async def update_player_list(client):
    if not PLAYER_LIST_CHANNEL_ID:
        return
    
    channel = client.get_channel(PLAYER_LIST_CHANNEL_ID)
    if not channel:
        return
    
    players_data = load_players()
    data = load_data()
    
    embed = discord.Embed(
        title="📋 Turnier-Teilnehmerliste",
        description=f"**Angemeldete Spieler: {len(players_data['players'])}**",
        color=discord.Color.blue()
    )
    
    # Reguläre Spieler
    regular_players = players_data['players'][:players_data['max_players']]
    if regular_players:
        regular_text = ""
        for i, player in enumerate(regular_players, 1):
            regular_text += f"**{i}.** {player['discord_name']}\n"
            regular_text += f"├ Valorant: `{player['valorant_name']}#{player['valorant_tag']}`\n"
            regular_text += f"├ Aktuell: **{player['current_rank']}**\n"
            regular_text += f"└ Höchster: **{player['highest_rank']}**\n\n"
        
        embed.add_field(
            name=f"✅ Reguläre Spieler (Max: {players_data['max_players']})",
            value=regular_text or "Keine Spieler",
            inline=False
        )
    
    # Ersatzspieler
    reserve_players = players_data['players'][players_data['max_players']:]
    if reserve_players:
        reserve_text = ""
        for i, player in enumerate(reserve_players, 1):
            reserve_text += f"**{i}.** {player['discord_name']}\n"
            reserve_text += f"├ Valorant: `{player['valorant_name']}#{player['valorant_tag']}`\n"
            reserve_text += f"├ Aktuell: **{player['current_rank']}**\n"
            reserve_text += f"└ Höchster: **{player['highest_rank']}**\n\n"
        
        embed.add_field(
            name="⏳ Ersatzspieler",
            value=reserve_text,
            inline=False
        )
    
    if len(players_data['players']) == 0:
        embed.description = "Noch keine Anmeldungen vorhanden."
    
    embed.set_footer(text=f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')} Uhr")
    
    # Nachricht senden oder aktualisieren
    if data['player_list_message_id']:
        try:
            message = await channel.fetch_message(data['player_list_message_id'])
            await message.edit(embed=embed)
        except:
            message = await channel.send(embed=embed)
            data['player_list_message_id'] = message.id
            save_data(data)
    else:
        message = await channel.send(embed=embed)
        data['player_list_message_id'] = message.id
        save_data(data)

# /newcup Command
@bot.tree.command(name="newcup", description="Erstelle eine neue Cup-Abstimmung")
@app_commands.describe(
    datum1="Erstes Datum (Format: TT.MM.YYYY)",
    datum2="Zweites Datum (Format: TT.MM.YYYY)"
)
async def newcup(interaction: discord.Interaction, datum1: str, datum2: str):
    # Prüfe Admin-Rechte
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ Nur Admins können diesen Befehl nutzen!", ephemeral=True)
        return
    
    await interaction.response.defer()
    
    try:
        # Parse Daten
        date1 = datetime.strptime(datum1, "%d.%m.%Y")
        date2 = datetime.strptime(datum2, "%d.%m.%Y")
        
        # Erstelle Vote-Embed
        embed = discord.Embed(
            title="🗳️ Cup-Datum Abstimmung",
            description="Stimme ab, wann der nächste Raph Cup stattfinden soll!",
            color=discord.Color.purple()
        )
        embed.add_field(name="Option 1", value=f"📅 {date1.strftime('%d.%m.%Y')} um 20:30 Uhr", inline=False)
        embed.add_field(name="Option 2", value=f"📅 {date2.strftime('%d.%m.%Y')} um 20:30 Uhr", inline=False)
        embed.set_footer(text="Abstimmung endet am 1. des nächsten Monats um 00:00 Uhr")
        
        # Sende in Vote-Channel
        if not VOTE_CHANNEL_ID:
            await interaction.followup.send("❌ Vote-Channel nicht konfiguriert!")
            return
        
        vote_channel = bot.get_channel(VOTE_CHANNEL_ID)
        vote_message = await vote_channel.send(embed=embed)
        
        # Füge Reaktionen hinzu
        await vote_message.add_reaction("1️⃣")
        await vote_message.add_reaction("2️⃣")
        
        # Speichere Vote-Daten
        data = load_data()
        data['current_vote'] = {
            'message_id': vote_message.id,
            'date1': date1.isoformat(),
            'date2': date2.isoformat(),
            'end_date': get_next_month_first().isoformat()
        }
        save_data(data)
        
        await interaction.followup.send(f"✅ Abstimmung erstellt in {vote_channel.mention}!")
        
    except ValueError:
        await interaction.followup.send("❌ Ungültiges Datumsformat! Nutze TT.MM.YYYY (z.B. 18.10.2025)")

def get_next_month_first():
    now = datetime.now()
    if now.month == 12:
        return datetime(now.year + 1, 1, 1, 0, 0, 0)
    else:
        return datetime(now.year, now.month + 1, 1, 0, 0, 0)

# Background-Task für Vote-Ende
@tasks.loop(minutes=1)
async def check_vote_end():
    data = load_data()
    
    if not data['current_vote']:
        return
    
    end_date = datetime.fromisoformat(data['current_vote']['end_date'])
    
    if datetime.now() >= end_date:
        # Vote beenden
        await end_vote()

async def end_vote():
    data = load_data()
    
    if not data['current_vote'] or not VOTE_CHANNEL_ID:
        return
    
    try:
        vote_channel = bot.get_channel(VOTE_CHANNEL_ID)
        vote_message = await vote_channel.fetch_message(data['current_vote']['message_id'])
        
        # Zähle Stimmen
        votes1 = 0
        votes2 = 0
        
        for reaction in vote_message.reactions:
            if str(reaction.emoji) == "1️⃣":
                votes1 = reaction.count - 1  # -1 für Bot-Reaktion
            elif str(reaction.emoji) == "2️⃣":
                votes2 = reaction.count - 1
        
        # Bestimme Gewinner
        date1 = datetime.fromisoformat(data['current_vote']['date1'])
        date2 = datetime.fromisoformat(data['current_vote']['date2'])
        
        if votes1 > votes2:
            winner_date = date1
            winner_votes = votes1
        elif votes2 > votes1:
            winner_date = date2
            winner_votes = votes2
        else:
            winner_date = date1  # Bei Gleichstand erste Option
            winner_votes = votes1
        
        # Ergebnis-Embed
        result_embed = discord.Embed(
            title="🏆 Abstimmung beendet!",
            description=f"Das nächste Turnier findet statt am:",
            color=discord.Color.gold()
        )
        result_embed.add_field(
            name="Gewähltes Datum",
            value=f"📅 **{winner_date.strftime('%d.%m.%Y')} um 20:30 Uhr**",
            inline=False
        )
        result_embed.add_field(name="Stimmen Option 1", value=f"1️⃣ {votes1} Stimmen", inline=True)
        result_embed.add_field(name="Stimmen Option 2", value=f"2️⃣ {votes2} Stimmen", inline=True)
        
        await vote_channel.send(embed=result_embed)
        
        # Update Cup-Daten
        data['current_cup'] = winner_date.isoformat()
        data['current_vote'] = None
        save_data(data)
        
        # Aktualisiere Ankündigung
        await update_announcement()
        
        # Lösche alte Spielerliste
        players_data = load_players()
        players_data['players'] = []
        players_data['max_players'] = 10
        save_players(players_data)
        
        # Aktualisiere Spielerliste
        await update_player_list(bot)
        
    except Exception as e:
        print(f"Fehler beim Beenden des Votes: {e}")

# Ankündigung aktualisieren
async def update_announcement():
    data = load_data()
    
    if not ANNOUNCEMENT_CHANNEL_ID:
        return
    
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if not channel:
        return
    
    embed = create_announcement_embed(data)
    view = AnnouncementButtons()
    
    if data['announcement_message_id']:
        try:
            message = await channel.fetch_message(data['announcement_message_id'])
            await message.edit(embed=embed, view=view)
        except:
            message = await channel.send(embed=embed, view=view)
            data['announcement_message_id'] = message.id
            save_data(data)
    else:
        message = await channel.send(embed=embed, view=view)
        data['announcement_message_id'] = message.id
        save_data(data)

# Bot-Events
@bot.event
async def on_ready():
    print(f'Bot ist online als {bot.user}')
    init_data()
    
    # Sync Commands
    await bot.tree.sync()
    print("Commands synchronisiert!")
    
    # Starte Background-Tasks
    check_vote_end.start()
    
    # Initialisiere Ankündigung
    await update_announcement()
    await update_player_list(bot)
    
    # Registriere persistente Views
    bot.add_view(AnnouncementButtons())

# Bot starten
if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("❌ DISCORD-TOKEN nicht gefunden in .env!")
    elif not API_KEY:
        print("❌ API-KEY nicht gefunden in .env!")
    else:
        bot.run(DISCORD_TOKEN)
