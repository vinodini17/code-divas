import discord
from discord.ext import commands
import os
import nmap
import requests
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime  
import base64
from flask import Flask
import threading

# Flask app for health check
app = Flask(__name__)

@app.route("/health")
def health():
    return "OK", 200  # Railway checks this endpoint to restart if needed

def run_flask():
    app.run(host="0.0.0.0", port=8080)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Retrieve Google credentials
google_credentials = os.getenv('GOOGLE_CREDENTIALS')
if google_credentials:
    with open('credentials.json', 'wb') as f:
        f.write(base64.b64decode(google_credentials))
else:
    print("No Google credentials found!")

# Enable Discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK")  # Store webhook URL in env vars

def send_alert(ip, port):
    message = f"⚠️ Security Alert! Open port detected:\nIP: {ip}\nPort: {port}"
    requests.post(WEBHOOK_URL, json={"content": message})

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("NmapScanLogs").sheet1  

@bot.command()
async def scan(ctx, ip: str):
    nm = nmap.PortScanner()
    await ctx.send(f"🔍 Scanning {ip}...")

    try:
        nm.scan(ip, arguments='-F')
        result, critical_ports_found = "", False

        for host in nm.all_hosts():
            result += f"**Host:** {host} ({nm[host].hostname()})\n"
            for proto in nm[host].all_protocols():
                result += f"**Protocol:** {proto}\n"
                for port in nm[host][proto]:
                    result += f"Port: `{port}` - **State:** {nm[host][proto][port]['state']}\n"
                    if port in [22, 3389]:  
                        send_alert(host, port)
                        critical_ports_found = True

        await ctx.send(f"```{result}```" if result else "✅ No open ports found.")
        status = "Critical Ports Found" if critical_ports_found else "No Open Ports Found"
        sheet.append_row([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip, status, result or "No open ports"])

    except Exception as e:
        await ctx.send(f"⚠️ Error scanning {ip}: {e}")
        sheet.append_row([datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ip, "Scan Failed", str(e)])

# Start Flask in a separate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

bot.run(TOKEN)
