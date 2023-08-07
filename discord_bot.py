import os
# python3 -m pip install -U discord.py
import discord
from dotenv import load_dotenv

load_dotenv()
application_id = os.environ.get("APPLICATION_ID")
bot_token = os.environ.get("BOT_TOKEN")
channel_id = os.environ.get("CHANNEL_ID")

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client)) #봇이 실행되면 콘솔창에 표시
    
    error_message = "An error occurred in the Flask server"
    channel = client.get_channel(int(channel_id))

    if channel:
        await channel.send(error_message)
    else:
        print("Error: Unable to find the specified Discord channel.")

client.run(bot_token)

