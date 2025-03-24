import discord
from discord.ext import commands
import os
import nmap
import requests
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime  # To add a timestamp for the logs

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

# Google Sheets API setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
# Google Sheets authentication
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)

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
        critical_ports_found = False  # Flag to track if any critical ports are found

        for host in nm.all_hosts():
            result += f"**Host:** {host} ({nm[host].hostname()})\n"
            for proto in nm[host].all_protocols():
                result += f"**Protocol:** {proto}\n"
                for port in nm[host][proto].keys():
                    result += f"Port: `{port}` - **State:** {nm[host][proto][port]['state']}\n"

                    # Send alerts for critical ports (SSH, RDP)
                    if port in [22, 3389]:  # SSH (22) and RDP (3389) are high-risk ports
                        send_alert(host, port)
                        critical_ports_found = True  # Mark that critical port was found

        if result:
            await ctx.send(f"```{result}```")
            status = "Critical Ports Found" if critical_ports_found else "Scan Completed"
            # Log the results to Google Sheets with a new "Status" column
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sheet.append_row([timestamp, ip, status, result])  # Add status in the third column
        else:
            await ctx.send("✅ No open ports found.")
            status = "No Open Ports Found"
            # Log the "No open ports" to Google Sheets with a new "Status" column
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sheet.append_row([timestamp, ip, status, "No open ports found."])

    except Exception as e:
        await ctx.send(f"⚠️ Error scanning {ip}: {e}")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # Log the error to Google Sheets with a new "Status" column
        sheet.append_row([timestamp, ip, "Scan Failed", str(e)])

# Run the bot with the provided token
bot.run(TOKEN)
