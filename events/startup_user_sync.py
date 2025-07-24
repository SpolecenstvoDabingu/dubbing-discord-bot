import discord, os
from utils.bot import bot
from utils.send_to_server import send_to_server
import os
import asyncio
from utils.enviroment_vars import DABING_ADDRESS, DABING_TOKEN, MAIN_GUILD_ID

async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    bot.loop.create_task(sync_users())

async def sync_users():
    if MAIN_GUILD_ID is None:
        return
    guild = bot.get_guild(int(MAIN_GUILD_ID))
    if guild is None:
        print(f"❌ Guild {int(MAIN_GUILD_ID)} not found in cache, trying to fetch…")
        try:
            # Will give you guild metadata, but NOT .members
            guild = await bot.fetch_guild(int(MAIN_GUILD_ID))
            print(f"ℹ️  Fetched guild '{guild.name}' via API, but it has no .members.")
        except discord.NotFound:
            print(f"❌ Bot is not in guild {int(MAIN_GUILD_ID)}")
            return
        except discord.HTTPException as e:
            print(f"❌ Failed to fetch guild: {e}")
            return
        
    cached_guild = bot.get_guild(int(MAIN_GUILD_ID))
    if not cached_guild:
        print("❌ Guild is still not cached, cannot fetch members.")
        return
    
    members = [member async for member in cached_guild.fetch_members(limit=None)]

    output_users = []

    for member in members:
        if member.bot:
            continue
        output_users.append({
            "id": str(member.id),
            "avatar": member.avatar.url if member.avatar else "https://cdn.discordapp.com/embed/avatars/0.png",
            "name": str(member.nick or member.name)
        })

    url = f"{DABING_ADDRESS}/discord/users/sync?token={DABING_TOKEN}"
    await asyncio.to_thread(send_to_server, url, output_users)