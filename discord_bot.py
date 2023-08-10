import datetime
import os
import discord
from dotenv import load_dotenv


# 디스코드로 에러 전송 (봇)
def send_error_to_discord(error_message):
    # 환경변수 가져오기
    load_dotenv()
    bot_token = os.environ.get("BOT_TOKEN")
    channel_id = os.environ.get("CHANNEL_ID")

    client = discord.Client(intents=discord.Intents.default())

    @client.event
    async def on_ready():
        channel = client.get_channel(int(channel_id))
        if channel:
            await channel.send(str(datetime.datetime.now()) + "\n" + str(error_message))
            await client.close()
        else:
            print("디스코드 채널을 찾을 수 없습니다")

    client.run(bot_token)
