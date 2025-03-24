import discord
from discord.ext import commands
import os
import nmap
import requests
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable intents, including message content
intents = discord.Intents.default()
intents.message_content = True  # Required for commands to work

bot = commands.Bot(command_prefix="!", intents=intents)

# Discord Webhook URL for sending alerts
WEBHOOK_URL = "https://discordapp.com/api/webhooks/1353672894500306976/nW2Zq8LSD_aW6nFd2aLSY9SHmCQjV6pvAmDShi0J3UaS3XHKPOc-wBie7Wu-_MmTOihP"  # Replace with your Discord webhook URL

# Function to send alerts for critical ports (SSH, RDP)
def send_alert(ip, port):
    message = f"⚠️ Security Alert! Open port detected:\nIP: {ip}\nPort: {port}"
    data = {"content": message}
    requests.post(WEBHOOK_URL, json=data)

# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Google Sheets API setup (removed merge conflict markers)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("your-credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NmapScanLogs").sheet1  # Open the spreadsheet by name, change this to your sheet name

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

                    # Send alerts for critical ports (SSH, RDP)
                    if port in [22, 3389]:  # SSH (22) and RDP (3389) are high-risk ports
                        send_alert(host, port)

        if result:
            await ctx.send(f"```{result}```")
        else:
            await ctx.send("✅ No open ports found.")

    except Exception as e:
        await ctx.send(f"⚠️ Error scanning {ip}: {e}")

# Run the bot with the provided token
bot.run(TOKEN)
