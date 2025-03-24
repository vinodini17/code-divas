import discord
import nmap
from discord.ext import commands
import os
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables from .env file
load_dotenv()

# Get the Discord bot token from environment variables
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable intents, including message content
intents = discord.Intents.default()
intents.message_content = True  # Required for commands to work

# Initialize the bot with a command prefix
bot = commands.Bot(command_prefix="!", intents=intents)

# Event that triggers when the bot is successfully logged in
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NmapScanLogs").sheet1  # Open the spreadsheet by name, change this to your sheet name

# Command to scan a given IP address using Nmap
@bot.command()
async def scan(ctx, ip: str):
    """Scans a given IP address using Nmap and returns open ports."""
    nm = nmap.PortScanner()  # Initialize Nmap scanner
    await ctx.send(f"🔍 Scanning {ip}... Please wait.")  # Send an initial scanning message to Discord

    try:
        # Perform a fast scan on the provided IP address
        nm.scan(ip, arguments='-F')  # Fast scan option (-F)
        result = []  # Initialize an empty list to store scan results

        # Iterate through the scan results for each host
        for host in nm.all_hosts():
            for proto in nm[host].all_protocols():
                for port in nm[host][proto].keys():
                    # Collect host, protocol, port, and state
                    result.append([host, proto, port, nm[host][proto][port]['state']])

        # Append the scan results to Google Sheets
        if result:
            sheet.append_rows(result)  # Append rows to the Google Sheet

        # Send the scan results to Discord or notify if no open ports were found
        if result:
            await ctx.send("Scan results logged successfully!")
        else:
            await ctx.send("✅ No open ports found.")

    except Exception as e:
        # Handle any errors during the scan (e.g., invalid IP address, Nmap issues)
        await ctx.send(f"⚠️ Error scanning {ip}: {e}")

# Run the bot using the Discord token loaded from the .env file
bot.run(TOKEN)
