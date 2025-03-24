import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable intents, including message content
intents = discord.Intents.default()
intents.message_content = True  # Required for commands to work

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.command()
async def scan(ctx, ip: str):
    await ctx.send(f"🔍 Scanning {ip}... (Functionality will be added here)")

bot.run(TOKEN)
