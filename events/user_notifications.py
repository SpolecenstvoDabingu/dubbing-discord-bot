import discord, os
from utils.bot import bot
from utils.send_to_server import send_to_server
from utils.request_get import request_get
import os
import asyncio
from utils.enviroment_vars import DABING_ADDRESS, DABING_TOKEN
from utils.scheduler import scheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

async def on_ready():
    scheduler.start()

    scheduler.add_job(
        create_notification,
        trigger=CronTrigger(hour=12, minute=0),
        id="Noon dubbing notification"
    )

    scheduler.add_job(
        create_notification,
        trigger=CronTrigger(hour=20, minute=0),
        id="Evening dubbing notification"
    )

async def create_notification():
    bot.loop.create_task(notify_users())

def build_dubber_notification_embed(data: dict, is_episode: bool) -> discord.Embed:
    embed_title = f"📢 Máš {'epizodu' if is_episode else 'scénku'} k nadabování!"
    embed = discord.Embed(
        title=embed_title,
        description=data["name_full"],
        color=discord.Color.orange(),
        url=data.get("full_info")
    )

    embed.add_field(name="📺 Dabing", value=data["dubbing"], inline=True)

    if is_episode:
        embed.add_field(name="📚 Série", value=str(data["season"]), inline=True)
        embed.add_field(name="🎞️ Epizoda", value=str(data["episode"]), inline=True)
        embed.add_field(name="🔢 Kód", value=data["sxex"], inline=True)

    embed.add_field(name="🧑‍🎤 Tvoje postava", value=f"`{data['character_name']}`", inline=False)
    embed.add_field(name="📜 Scénář", value=f"[Klikni zde]({data['script']})", inline=False)

    if deadline := data.get("deadline"):
        discord_timestamp = f"<t:{int(deadline)}:R>"
        embed.add_field(name="⏰ Deadline", value=discord_timestamp, inline=False)

    embed.set_footer(text="Prosím, co nejdříve nahraj svou repliku. Díky!")

    return embed

async def notify_users():
    url_notifications = f"{DABING_ADDRESS}/discord/commands/notification/users?token={DABING_TOKEN}"

    response_notifications = await asyncio.to_thread(request_get, url_notifications)
    if not response_notifications.ok:
        print("❌ Failed to parse response from server.")
        return

    try:
        notification_datas = response_notifications.json()["data"]
    except Exception as e:
        print("❌ Failed to parse response from server.")
        return
    
    user_notifications = {notification_data["id"]:notification_data["notification"] for notification_data in notification_datas if "id" in notification_data and "notification" in notification_data}

    url_dubbings_characters = f"{DABING_ADDRESS}/discord/dubbings/characters?token={DABING_TOKEN}"

    response_dubbings_characters = await asyncio.to_thread(request_get, url_dubbings_characters)
    if not response_dubbings_characters.ok:
        print("❌ Failed to parse response from server.")
        return

    try:
        dubbing_characters_datas = response_dubbings_characters.json()["data"]
    except Exception as e:
        print("❌ Failed to parse response from server.")
        return
    
    for dubbing_characters_data in dubbing_characters_datas:
        user_id = dubbing_characters_data.get("user_id")
        if user_id is None:
            continue
        if not user_notifications.get(user_id, False):
            continue
        user = await bot.fetch_user(user_id)

        dt = datetime.now() + timedelta(days=1)
        deadline = datetime.fromtimestamp(dubbing_characters_data["deadline"])
        if dt < deadline:
            continue

        embed = build_dubber_notification_embed(dubbing_characters_data, is_episode=dubbing_characters_data.get("episode") is not None)
        await user.send(embed=embed)