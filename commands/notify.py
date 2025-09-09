import discord, asyncio
from math import ceil
from discord import app_commands, Object
from typing import Literal
from utils import BaseCog, DABING_ADDRESS, DABING_TOKEN, request_get

# ---------------- Embed Helper ----------------
def build_notify_embed(data: dict, is_episode: bool) -> tuple[discord.Embed, list]:
    embed_title = f"🔔 Připomenutí o {'epizodě' if is_episode else 'scéně'}!"
    embed = discord.Embed(
        title=embed_title,
        description=data["name_full"],
        color=discord.Color.orange(),
        url=data.get("full_info")
    )

    embed.add_field(name="📺 Dabing", value=data["dubbing"], inline=True)

    dubbers_ids = []
    if "manager" in data and data["manager"]:
        embed.add_field(name="👨‍💼 Manažer", value=f"<@{data['manager']}>", inline=True)

    if is_episode:
        embed.add_field(name="📚 Série", value=str(data["season"]), inline=True)
        embed.add_field(name="🎞️ Epizoda", value=str(data["episode"]), inline=True)
        embed.add_field(name="🔢 Kód", value=data["sxex"], inline=True)

    embed.add_field(name="📜 Scénář", value=f"[Klikni zde]({data['script']})", inline=False)

    if "urls" in data and data["urls"]:
        embed.add_field(name="🔗 Odkazy", value=data["urls"][:512], inline=False)

    if deadline := data.get("deadline"):
        discord_timestamp = f"<t:{int(deadline)}:R>"
        embed.add_field(name="⏰ Deadline", value=discord_timestamp, inline=False)

    # Dubbers that haven't provided their dubbings
    if data.get("dubbers"):
        pending_list = []
        for d in data["dubbers"]:
            if d.get("user_id") is not None:
                dubbers_ids.append(d["user_id"])
                user_mention = f"<@{d['user_id']}>"
            else:
                user_mention = "❓"
            pending_list.append(f"• `{d['character_name']}` — {user_mention}")

        threshold = 10
        if len(pending_list) > threshold:
            for i in range(ceil(len(pending_list) / threshold)):
                embed.add_field(
                    name=f"🎙️ Nedodané dabingy (část {i + 1})",
                    value="\n".join(pending_list[i * threshold:(i + 1) * threshold]),
                    inline=True
                )
        else:
            embed.add_field(name="🎙️ Nedodané dabingy", value="\n".join(pending_list), inline=True)

    embed.set_footer(text="Zkontrolujte prosím své repliky a nahrajte je co nejdříve!")
    return embed, dubbers_ids

# ---------------- Send Notify ----------------
async def send_notify(interaction: discord.Interaction, parent_cog, type_: str, id_: int):
    await interaction.response.defer(ephemeral=True)
    url = f"{DABING_ADDRESS}/discord/commands/notify/{type_}/{id_}?token={DABING_TOKEN}"
    response = await asyncio.to_thread(request_get, url)

    if not response.ok:
        await parent_cog.reply_defer_checked(interaction, "❌ Failed to fetch data.", ephemeral=True)
        return

    try:
        data = response.json()
    except Exception as e:
        await parent_cog.reply_defer_checked(interaction, f"❌ JSON parse error: `{e}`", ephemeral=True)
        return

    embed, dubbers_ids = build_notify_embed(data, is_episode=(type_ == "episode"))
    target_channel = interaction.channel

    try:
        mentions = " ".join(f"<@{uid}>" for uid in set(dubbers_ids))
        await target_channel.send(content=mentions, embed=embed)
        msg = f"✅ Notification sent to <#{target_channel.id}>!"
        if dubbers_ids:
            msg += f"\nMembers notified: {mentions}"
            
        await interaction.followup.send(msg, ephemeral=True)
    except Exception as e:
        await parent_cog.reply_defer_checked(interaction, f"❌ Failed to send embed: {e}", ephemeral=True)

# ---------------- Cog ----------------
class Notify(BaseCog):
    COG_LABEL = "Dubbing"

    @app_commands.command(name="notify", description="Notify members who haven't provided their dubbings")
    @app_commands.checks.has_permissions(administrator=True)
    async def notify(
        self,
        interaction: discord.Interaction,
        type: Literal["episode", "scene"],
        id: int
    ):
        await send_notify(interaction, self, type, id)

setup = Notify.setup
