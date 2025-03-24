import discord
from discord.ext import commands

# Insert your bot token here
TOKEN = "YOUR_DISCORD_BOT_TOKEN"

# Set up bot with command prefix
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def scan(ctx, ip: str):
    await ctx.send(f"🔍 Scanning {ip}... (Functionality will be added here)")

# Run the bot
bot.run(TOKEN)
