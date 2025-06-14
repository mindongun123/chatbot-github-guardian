import requests
import json
import discord
from flask import Flask, request
import asyncio
from threading import Thread
import os
from dotenv import load_dotenv

# Tải biến môi trường từ tệp .env
load_dotenv()

# Cấu hình Discord bot
TOKEN = os.getenv('DISCORD_TOKEN')  # Thay thế bằng token bot Discord của bạn
CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')  # Thay thế bằng ID của kênh Discord bạn muốn thông báo

# Tạo đối tượng intents
intents = discord.Intents.default()
intents.message_content = True  # Đảm bảo bot có thể đọc nội dung tin nhắn
client = discord.Client(intents=intents)

# Flask app để nhận Webhook từ GitHub
app = Flask(__name__)

# Lấy danh sách repository từ GitHub
def get_repositories():
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {os.getenv('GITHUB_TOKEN')}"  # Thay YOUR_GITHUB_TOKEN bằng token của bạn
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Lưu danh sách repository vào tệp
def save_repositories(repositories):
    with open("repositories.json", "w") as file:
        json.dump(repositories, file)

loop = None  # Lưu event loop của Discord bot

@client.event
async def on_ready():
    global loop
    loop = asyncio.get_event_loop()
    print(f'Logged in as {client.user}')

# Gửi thông báo đến Discord (không đổi)
async def send_to_discord(message):
    channel = client.get_channel(int(CHANNEL_ID))
    await channel.send(message)

@app.route('/check-repos', methods=['GET'])
def check_for_changes():
    message = "Có request mới đến endpoint /check-repos!"
    # Gửi task vào event loop của Discord bot
    global loop
    if loop:
        asyncio.run_coroutine_threadsafe(send_to_discord(message), loop)
        return "Đã gửi thông báo lên Discord!"
    else:
        return "Discord bot chưa sẵn sàng!"

def run_discord_bot():
    client.run(TOKEN)

if __name__ == "__main__":
    # Chạy Discord bot ở thread riêng
    discord_thread = Thread(target=run_discord_bot)
    discord_thread.start()
    # Chạy Flask app
    app.run(port=5000)

# Đổi tên file này thành github_guardian.py để import được trong wsgi.py
