# /announcement type:scene id:1
# http://localhost/discord/commands/announcement/scene/1?token=7252fc2f91fa2abfe212c38078146898ba2bf2c455a75fbbc15b99f9077a9377

import discord, asyncio
from discord import app_commands
from utils import BaseCog
from typing import Literal
from utils import DABING_ADDRESS, DABING_TOKEN
from utils import request_get

def build_announcement_embed(data: dict, is_episode: bool) -> discord.Embed:
    embed_title = f"🎬 Nové oznámení o {'epizodě' if is_episode else 'scéně'}!"
    embed = discord.Embed(
        title=embed_title,
        description=data["name_full"],
        color=discord.Color.blue(),
        url=data.get("full_info")  # Přidání odkazu na detail
    )

    embed.add_field(name="📺 Dabing", value=data["dubbing"], inline=True)

    if is_episode:
        embed.add_field(name="📚 Série", value=str(data["season"]), inline=True)
        embed.add_field(name="🎞️ Epizoda", value=str(data["episode"]), inline=True)
        embed.add_field(name="🔢 Kód", value=data["sxex"], inline=True)

    embed.add_field(name="📜 Scénář", value=f"[Klikni zde]({data['script']})", inline=False)
    
    if "urls" in data and data["urls"]:
        embed.add_field(name="🔗 Odkazy", value=data["urls"][:512], inline=False)

    if deadline := data.get("deadline"):
        # deadline je předpokládán jako unixový timestamp v sekundách
        discord_timestamp = f"<t:{int(deadline)}:R>"
        embed.add_field(name="⏰ Deadline", value=discord_timestamp, inline=False)

    if data.get("dubbers"):
        dubbers_list = ""
        for d in data["dubbers"]:
            user_mention = f"<@{d['user_id']}>"
            dubbers_list += f"• `{d['character_name']}` — {user_mention}\n"
        embed.add_field(name="🎙️ Dabéři", value=dubbers_list, inline=False)

    embed.set_footer(text="Zkontrolujte prosím scénář a nahrajte své repliky!")
    return embed

class Announcement(BaseCog):
    COG_LABEL = "Dubbing"

    @app_commands.command(name="announcement", description="Send announcement embed of specified episode/scene")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(type="Select whether it's an episode or scene")
    async def announcement(self, interaction: discord.Interaction, type: Literal["episode", "scene"], id: int):
        url = f"{DABING_ADDRESS}/discord/commands/announcement/{type}/{id}?token={DABING_TOKEN}"

        # Fetch data in background thread
        response = await asyncio.to_thread(request_get, url)

        try:
            data = response.json()
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Failed to parse response from server.\nError: `{e}`",
                ephemeral=True
            )
            return

        embed = build_announcement_embed(data, is_episode=(type == "episode"))
        await interaction.response.send_message(embed=embed)

setup = Announcement.setup