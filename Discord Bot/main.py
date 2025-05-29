# Simple Tic Tac Toe Discord Bot
import discord
import os
import dotenv
from discord.ext import commands

dotenv.load_dotenv()
env = os.environ

intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent for commands
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

games = {}

class TicTacToe:
    def __init__(self, player1, player2):
        self.board = [":white_large_square:"] * 9
        self.players = [player1, player2]
        self.turn = 0
        self.winner = None

    def make_move(self, pos):
        if self.board[pos] != ":white_large_square:":
            return False
        self.board[pos] = ":x:" if self.turn == 0 else ":o:"
        self.turn = 1 - self.turn
        return True

    def check_winner(self):
        wins = [
            [0,1,2],[3,4,5],[6,7,8], # rows
            [0,3,6],[1,4,7],[2,5,8], # cols
            [0,4,8],[2,4,6] # diags
        ]
        for a,b,c in wins:
            if self.board[a] == self.board[b] == self.board[c] != ":white_large_square:":
                self.winner = self.board[a]
                return True
        if ":white_large_square:" not in self.board:
            self.winner = "Tie"
            return True
        return False

    def render(self):
        board_display = ""
        for i in range(9):
            if self.board[i] == ":white_large_square:":
                board_display += f":regional_indicator_{chr(97 + i)}:"
            else:
                board_display += self.board[i]
            if (i + 1) % 3 == 0:
                board_display += "\n"
        return board_display

@bot.event
async def on_ready():
    print(f"\n{'='*50}")
    print(f"🤖 Bot Name: {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print(f"🌐 Connected to {len(bot.guilds)} server(s):")
    for guild in bot.guilds:
        print(f"   - {guild.name} (ID: {guild.id}) - {guild.member_count} members")
    print(f"📡 Bot is ready and online!")
    print(f"{'='*50}\n")

@bot.event
async def on_command(ctx):
    print(f"[COMMAND] {ctx.author} ({ctx.author.id}) used '{ctx.command}' in #{ctx.channel} ({ctx.guild.name if ctx.guild else 'DM'})")

@bot.event
async def on_command_completion(ctx):
    print(f"[SUCCESS] Command '{ctx.command}' completed successfully for {ctx.author}")

@bot.event
async def on_command_error(ctx, error):
    print(f"[ERROR] Command '{ctx.command}' failed for {ctx.author}: {type(error).__name__}")
    if isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Unknown Command", description="I don't recognize that command. Use `!ttthelp` to see available commands.", color=discord.Color.red())
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(title="Missing Argument", description="You're missing a required argument. Use `!ttthelp` for command usage.", color=discord.Color.orange())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Error", description="An error occurred while processing your command.", color=discord.Color.red())
        await ctx.send(embed=embed)

@bot.command(name='ttthelp')
async def ttthelp(ctx):
    embed = discord.Embed(title="Tic Tac Toe Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!ttt @opponent", value="Start a new Tic Tac Toe game with the mentioned user", inline=False)
    embed.add_field(name="!move <position>", value="Make a move at the given position (a-i)", inline=False)
    embed.add_field(name="!tttend", value="End the current game in the channel", inline=False)
    embed.add_field(name="!ttthelp", value="Show this help message", inline=False)
    embed.add_field(name="Board Layout", value="```\na b c\nd e f\ng h i```", inline=False)
    embed.add_field(name="Example", value="!ttt @friend\n!move e", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Tic Tac Toe Bot Commands", color=discord.Color.blue())
    embed.add_field(name="!ttt @opponent", value="Start a new Tic Tac Toe game with the mentioned user", inline=False)
    embed.add_field(name="!move <position>", value="Make a move at the given position (a-i)", inline=False)
    embed.add_field(name="!tttend", value="End the current game in the channel", inline=False)
    embed.add_field(name="!help", value="Show this help message", inline=False)
    embed.add_field(name="Board Layout", value="```\na b c\nd e f\ng h i```", inline=False)
    embed.add_field(name="Example", value="!ttt @friend\n!move e", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def ttt(ctx, opponent: discord.Member = None):
    if opponent is None:
        embed = discord.Embed(title="Tic Tac Toe", description="You must mention an opponent! Usage: !ttt @opponent", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if ctx.author == opponent:
        embed = discord.Embed(title="Tic Tac Toe", description="You can't play against yourself!", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if ctx.channel.id in games:
        embed = discord.Embed(title="Tic Tac Toe", description="A game is already running in this channel.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return
    games[ctx.channel.id] = TicTacToe(ctx.author, opponent)
    embed = discord.Embed(title="Tic Tac Toe Started!", description=f"{ctx.author.mention} vs {opponent.mention}\n\n{games[ctx.channel.id].render()}\n\n{ctx.author.mention}'s turn (X)", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def move(ctx, pos):
    game = games.get(ctx.channel.id)
    if not game:
        embed = discord.Embed(title="Tic Tac Toe", description="No game running in this channel. Start one with !ttt @opponent", color=discord.Color.red())
        await ctx.send(embed=embed)
        return
    if ctx.author != game.players[game.turn]:
        embed = discord.Embed(title="Tic Tac Toe", description="It's not your turn!", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return
    
    # Convert letter position to number
    if isinstance(pos, str) and len(pos) == 1 and pos.lower() in 'abcdefghi':
        pos = ord(pos.lower()) - ord('a') + 1
    else:
        try:
            pos = int(pos)
        except ValueError:
            embed = discord.Embed(title="Tic Tac Toe", description="Position must be a-i or 1-9.", color=discord.Color.orange())
            await ctx.send(embed=embed)
            return
    
    if pos < 1 or pos > 9:
        embed = discord.Embed(title="Tic Tac Toe", description="Position must be a-i or 1-9.", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return
    if not game.make_move(pos-1):
        embed = discord.Embed(title="Tic Tac Toe", description="That spot is already taken!", color=discord.Color.orange())
        await ctx.send(embed=embed)
        return
    if game.check_winner():
        if game.winner == "Tie":
            embed = discord.Embed(title="Tic Tac Toe", description=game.render() + "\nIt's a tie!", color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            winner = game.players[0] if game.winner == ":x:" else game.players[1]
            embed = discord.Embed(title="Tic Tac Toe", description=game.render() + f"\n{winner.mention} wins!", color=discord.Color.gold())
            await ctx.send(embed=embed)
        del games[ctx.channel.id]
    else:
        embed = discord.Embed(title="Tic Tac Toe", description=game.render() + f"\n{game.players[game.turn].mention}'s turn ({'X' if game.turn == 0 else 'O'}).", color=discord.Color.green())
        await ctx.send(embed=embed)

@bot.command()
async def tttend(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="Tic Tac Toe", description="Game ended.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Tic Tac Toe", description="No game to end.", color=discord.Color.orange())
        await ctx.send(embed=embed)

@bot.command()
async def endgame(ctx):
    if ctx.channel.id in games:
        del games[ctx.channel.id]
        embed = discord.Embed(title="Tic Tac Toe", description="Game ended.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        embed = discord.Embed(title="Tic Tac Toe", description="No game to end.", color=discord.Color.orange())
        await ctx.send(embed=embed)

bot.run(env.get("DISCORD_TOKEN"))
