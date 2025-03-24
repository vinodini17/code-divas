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
    """Scans a given IP address using Nmap and returns open ports."""
    nm = nmap.PortScanner()  # Initialize Nmap
    await ctx.send(f"🔍 Scanning {ip}... Please wait.")

    try:
        nm.scan(ip, arguments='-F')  # Fast scan
        result = ""

        for host in nm.all_hosts():
            result += f"**Host:** {host} ({nm[host].hostname()})\n"
            for proto in nm[host].all_protocols():
                result += f"**Protocol:** {proto}\n"
                for port in nm[host][proto].keys():
                    result += f"Port: `{port}` - **State:** {nm[host][proto][port]['state']}\n"

        if result:
            await ctx.send(f"```{result}```")
        else:
            await ctx.send("✅ No open ports found.")

    except Exception as e:
        await ctx.send(f"⚠️ Error scanning {ip}: {e}")

bot.run(TOKEN)
