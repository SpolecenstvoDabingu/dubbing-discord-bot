from utils.send_to_server import send_to_server
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()

DABING_ADDRESS = os.getenv("DABING_ADDRESS", None)
DABING_TOKEN = os.getenv("DABING_TOKEN", None)

MAIN_GUILD_ID = os.getenv("MAIN_GUILD_ID", None)

async def on_member_join(member):
    if MAIN_GUILD_ID is None or member.guild.id != int(MAIN_GUILD_ID):
        return
    output_users = [{
        "id": str(member.id),
        "avatar": member.avatar.url if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png",
        "name": str(member.nick or member.name)
    }]
    url = f"{DABING_ADDRESS}/discord/users/add?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)


async def on_member_remove(member):
    if MAIN_GUILD_ID is None or member.guild.id != int(MAIN_GUILD_ID):
        return
    output_users = [{
        "id": str(member.id),
        "avatar": member.avatar.url if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png",
        "name": str(member.nick or member.name)
    }]
    url = f"{DABING_ADDRESS}/discord/users/remove?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)