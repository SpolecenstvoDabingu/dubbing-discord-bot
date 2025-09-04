# /announcement type:scene id:1
# http://localhost/discord/commands/announcement/scene/1?token=7252fc2f91fa2abfe212c38078146898ba2bf2c455a75fbbc15b99f9077a9377

import discord, asyncio
from math import ceil
from discord import app_commands, Object
from utils import BaseCog
from typing import Literal
from utils import DABING_ADDRESS, DABING_TOKEN
from utils import request_get

def build_announcement_embed(data: dict, is_episode: bool) -> tuple[discord.Embed, list]:
    embed_title = f"🎬 Nové oznámení o {'epizodě' if is_episode else 'scéně'}!"
    embed = discord.Embed(
        title=embed_title,
        description=data["name_full"],
        color=discord.Color.blue(),
        url=data.get("full_info")  # Přidání odkazu na detail
    )

    embed.add_field(name="📺 Dabing", value=data["dubbing"], inline=True)

    dubbers_ids = []
    if "manager" in data and data["manager"]:
        embed.add_field(name="👨‍💼 Manažer", value=f"<@{data["manager"]}>", inline=True)
        dubbers_ids.append(data["manager"])

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
        dubbers_list = []
        for d in data["dubbers"]:
            if d.get("user_id") is not None:
                dubbers_ids.append(d['user_id'])
                user_mention = f"<@{d['user_id']}>"
            else:
                user_mention = "❓"
            dubbers_list.append(f"• `{d['character_name']}` — {user_mention}")
        threshold = 10
        if len(dubbers_list) > threshold:
            for i in range(ceil(len(dubbers_list) / threshold)):
                embed.add_field(
                    name=f"🎙️ Dabéři (část {i + 1})",
                    value="\n".join(dubbers_list[i * threshold:(i + 1) * threshold]),
                    inline=True
                )
        else:
            embed.add_field(name="🎙️ Dabéři", value="\n".join(dubbers_list), inline=True)

    embed.set_footer(text="Zkontrolujte prosím scénář a nahrajte své repliky!")
    return embed, dubbers_ids

async def add_users_to_thread(thread: discord.Thread, dubbers_ids: list) -> list[str]:
    errors = []
    for dubber_id in dubbers_ids:
        try:
            await thread.add_user(Object(id=int(dubber_id)))
        except discord.Forbidden:
            errors.append(f"❌ I don’t have permission to add <@{dubber_id}>")
        except discord.HTTPException:
            errors.append(f"⚠️ Failed to add <@{dubber_id}>")
        except Exception as e:
            errors.append(f"⚠️ Failed to add <@{dubber_id}>. Error: {e}")
    return errors

class Announcement(BaseCog):
    COG_LABEL = "Dubbing"

    @app_commands.command(name="announcement", description="Send announcement embed of specified episode/scene")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(type="Select whether it's an episode or scene")
    async def announcement(self, interaction: discord.Interaction, type: Literal["episode", "scene"], id: int, channel: discord.ForumChannel = None):
        await interaction.response.defer(ephemeral=True)
        url = f"{DABING_ADDRESS}/discord/commands/announcement/{type}/{id}?token={DABING_TOKEN}"

        # Fetch data in background thread
        response = await asyncio.to_thread(request_get, url)

        if not response.ok:
            await self.reply_defer_checked(interaction=interaction, content="❌ Failed to parse response from server.", ephemeral=True)
            return

        try:
            data = response.json()
        except Exception as e:
            await self.reply_defer_checked(interaction=interaction, content=f"❌ Failed to parse response from server.\nError: `{e}`", ephemeral=True)
            return

        try:
            embed, dubbers_ids = build_announcement_embed(data, is_episode=(type == "episode"))
            if channel:
                if "name_full" not in data:
                    await self.reply_defer_checked(interaction=interaction, content="❌ Missing 'name_full' in data for announcement.", ephemeral=True)
                    return
                existing_thread = discord.utils.get(channel.threads, name=data["name_full"])
                if existing_thread:
                    await existing_thread.send(embed=embed)
                    errors = await add_users_to_thread(thread=existing_thread, dubbers_ids=dubbers_ids)
                    await self.reply_defer_checked(
                        interaction=interaction,
                        content=f"ℹ️ Oznámení bylo přidáno do existujícího vlákna!" + ((f"\nWith errors:\n" + ("\n".join(errors))) if len(errors) > 0 else ""),
                        ephemeral=True
                    )
                    res_text = f"ℹ️ Oznámení bylo přidáno do existujícího vlákna!"
                else:
                    new_thread = await channel.create_thread(name=data["name_full"][:100], embed=embed)
                    errors = await add_users_to_thread(thread=new_thread.thread, dubbers_ids=dubbers_ids)
                    await self.reply_defer_checked(
                        interaction=interaction,
                        content=f"✅ Oznámení bylo zveřejněno v novém vlákně!" + ((f"\nWith errors:\n" + ("\n".join(errors))) if len(errors) > 0 else ""),
                        ephemeral=True
                    )
                return
            
            errors = []
            if isinstance(interaction.channel, discord.Thread):
                await interaction.channel.send(embed=embed)
                errors = await add_users_to_thread(thread=interaction.channel, dubbers_ids=dubbers_ids)
            elif isinstance(interaction.channel, discord.TextChannel):
                await interaction.channel.send(embed=embed)
            else:
                await self.reply_defer_checked(interaction, content="This channel isn't text", ephemeral=True)
            await self.reply_defer_checked(
                interaction=interaction,
                content=f"ℹ️ Oznámení bylo odesláno!" + ((f"\nWith errors:\n" + ("\n".join(errors))) if len(errors) > 0 else ""),
                ephemeral=True
            )
                
        except Exception as e:
            await self.reply_defer_checked(interaction=interaction, content=f"❌ Failed to perform command.\nError: `{e}`", ephemeral=True)
            return

setup = Announcement.setup