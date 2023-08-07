import os
# python3 -m pip install -U discord.py
import discord
# from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()
application_id = os.environ.get("APPLICATION_ID")
bot_token = os.environ.get("BOT_TOKEN")

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client)) #봇이 실행되면 콘솔창에 표시

client.run(bot_token)

