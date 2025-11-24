from utils import send_to_server
import os
from utils import DABING_ADDRESS, DABING_TOKEN, MAIN_GUILD_ID, get_user_data_sync, send_welcome_message
import asyncio

async def on_member_join(member):
    if MAIN_GUILD_ID is None or member.guild.id != int(MAIN_GUILD_ID):
        return
    if member.bot:
        return
    output_users = [get_user_data_sync(member)]
    url = f"{DABING_ADDRESS}/discord/users/add?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)
    await send_welcome_message(member)


async def on_member_remove(member):
    if MAIN_GUILD_ID is None or member.guild.id != int(MAIN_GUILD_ID):
        return
    if member.bot:
        return
    output_users = [get_user_data_sync(member)]
    url = f"{DABING_ADDRESS}/discord/users/remove?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)