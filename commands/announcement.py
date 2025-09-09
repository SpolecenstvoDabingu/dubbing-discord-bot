import discord, asyncio
from math import ceil
from discord import app_commands, Object
from typing import Literal
from utils import BaseCog, DABING_ADDRESS, DABING_TOKEN, request_get


# ---------------- Embed & Thread Helpers ----------------
def build_announcement_embed(data: dict, is_episode: bool) -> tuple[discord.Embed, list]:
    embed_title = f"🎬 Nové oznámení o {'epizodě' if is_episode else 'scéně'}!"
    embed = discord.Embed(
        title=embed_title,
        description=data["name_full"],
        color=discord.Color.blue(),
        url=data.get("full_info")
    )

    embed.add_field(name="📺 Dabing", value=data["dubbing"], inline=True)

    dubbers_ids = []
    if "manager" in data and data["manager"]:
        embed.add_field(name="👨‍💼 Manažer", value=f"<@{data['manager']}>", inline=True)
        dubbers_ids.append(data["manager"])

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


# ---------------- Step 1: Modal for Category ----------------
class CategoryModal(discord.ui.Modal, title="Select Category"):
    category_name = discord.ui.TextInput(
        label="Category Name",
        placeholder="Type part of the category name (leave empty to use current channel)",
        required=False
    )

    def __init__(self, parent_cog, type_, id_):
        super().__init__()
        self.parent_cog = parent_cog
        self.type_ = type_
        self.id_ = id_

    async def on_submit(self, interaction: discord.Interaction):
        name = self.category_name.value.strip()
        if not name:
            await send_announcement(interaction, self.parent_cog, self.type_, self.id_, None)
            return

        # Find matching categories
        categories = [
            cat for cat in interaction.guild.categories
            if name.lower() in cat.name.lower()
        ]

        if not categories:
            # No match → ask again
            await interaction.response.send_modal(CategoryModal(self.parent_cog, self.type_, self.id_))
            return

        # Collect channels from all matched categories
        channels = []
        for cat in categories:
            channels.extend(
                ch for ch in cat.channels if isinstance(ch, discord.ForumChannel)
            )

        if not channels:
            await send_announcement(interaction, self.parent_cog, self.type_, self.id_, None)
            return

        # Limit to 25
        view = ChannelSelectView(self.parent_cog, self.type_, self.id_, channels[:25])
        cats_str = ", ".join(f"<#{cat.id}>" for cat in categories)

        if interaction.response.is_done():
            await interaction.followup.send(f"Select a channel from categories: **{cats_str}**", view=view, ephemeral=True)
        else:
            await interaction.response.send_message(f"Select a channel from categories: **{cats_str}**", view=view, ephemeral=True)


# ---------------- Step 2: Dropdown for Channels ----------------
class ChannelSelect(discord.ui.Select):
    def __init__(self, parent_cog, type_, id_, channels):
        self.parent_cog = parent_cog
        self.type_ = type_
        self.id_ = id_
        options = [discord.SelectOption(label=ch.name[:100], value=str(ch.id), description=str(ch.category)) for ch in channels]
        super().__init__(placeholder="Choose a channel...", options=options)

    async def callback(self, interaction: discord.Interaction):
        target_channel = interaction.guild.get_channel(int(self.values[0]))
        if not target_channel:
            await interaction.response.send_message("❌ Channel not found.", ephemeral=True)
            return
        await send_announcement(interaction, self.parent_cog, self.type_, self.id_, target_channel)


class ChannelSelectView(discord.ui.View):
    def __init__(self, parent_cog, type_, id_, channels):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect(parent_cog, type_, id_, channels))


# ---------------- Send Announcement Function ----------------
async def send_announcement(interaction, parent_cog, type_, id_, target_channel):
    target_channel = target_channel or interaction.channel
    await interaction.response.defer(ephemeral=True)

    url = f"{DABING_ADDRESS}/discord/commands/announcement/{type_}/{id_}?token={DABING_TOKEN}"
    response = await asyncio.to_thread(request_get, url)
    if not response.ok:
        await parent_cog.reply_defer_checked(interaction, "❌ Failed to fetch data.", ephemeral=True)
        return

    try:
        data = response.json()
    except Exception as e:
        await parent_cog.reply_defer_checked(interaction, f"❌ JSON parse error: `{e}`", ephemeral=True)
        return

    embed, dubbers_ids = build_announcement_embed(data, is_episode=(type_ == "episode"))
    errors = []

    try:
        if isinstance(target_channel, discord.ForumChannel):
            existing_thread = discord.utils.get(target_channel.threads, name=data.get("name_full","announcement"))
            if existing_thread:
                await existing_thread.send(embed=embed)
                errors = await add_users_to_thread(existing_thread, dubbers_ids)
            else:
                new_thread = await target_channel.create_thread(name=data.get("name_full","announcement")[:100], embed=embed)
                errors = await add_users_to_thread(new_thread.thread, dubbers_ids)
        else:
            await target_channel.send(embed=embed)
    except Exception as e:
        await parent_cog.reply_defer_checked(interaction, f"❌ Failed to send embed: {e}", ephemeral=True)
        return

    msg = f"✅ Announcement sent to <#{target_channel.id}>!"
    if errors:
        msg += "\nWith errors:\n" + "\n".join(errors)
    await interaction.followup.send(msg, ephemeral=True)


# ---------------- Cog ----------------
class Announcement(BaseCog):
    COG_LABEL = "Dubbing"

    @app_commands.command(name="announcement", description="Send announcement embed of specified episode/scene")
    @app_commands.checks.has_permissions(administrator=True)
    async def announcement(
        self,
        interaction: discord.Interaction,
        type: Literal["episode", "scene"],
        id: int,
        channel: discord.ForumChannel | discord.TextChannel = None
    ):
        if channel is None and not interaction.response.is_done():
            await interaction.response.send_modal(CategoryModal(self, type, id))
        else:
            await send_announcement(interaction, self, type, id, channel)


setup = Announcement.setup
