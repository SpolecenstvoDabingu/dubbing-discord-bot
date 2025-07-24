from utils.send_to_server import send_to_server
import os
from utils.enviroment_vars import DABING_ADDRESS, DABING_TOKEN, MAIN_GUILD_ID
import asyncio

async def on_member_join(member):
    if MAIN_GUILD_ID is None or member.guild.id != int(MAIN_GUILD_ID):
        return
    if member.bot:
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
    if member.bot:
        return
    output_users = [{
        "id": str(member.id),
        "avatar": member.avatar.url if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png",
        "name": str(member.nick or member.name)
    }]
    url = f"{DABING_ADDRESS}/discord/users/remove?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)