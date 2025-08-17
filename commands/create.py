import discord
from discord import app_commands
from discord.ext import commands
from utils import BaseCog

class Create(BaseCog):
    COG_LABEL = "Utilities"

    @app_commands.command(name="create", description="Creates new dubbing category.")
    @app_commands.checks.has_permissions(administrator=True)
    async def create(self, interaction: discord.Interaction, full_name: str, short_name: str = None):
        await interaction.response.defer(ephemeral=True)
        if short_name is None:
            short_name = full_name
        full_name = full_name[:50]
        short_name = short_name[:50]

        guild = interaction.guild

        category = await guild.create_category(name=f'愛 ．．{full_name.title()}  ⸝ 🌩．．')

        text_channels = [
            f'╿・୨🔔୧・{short_name.lower()}-oznámení',
            '╿・୨🎙️୧・obsazení',
            '╿・୨📌୧・nástěnka˚₊'
        ]
        created_text_channels = []
        for name in text_channels:
            channel = await guild.create_text_channel(
                name=name,
                category=category
            )
            created_text_channels.append(channel)

        discussion_channel = await guild.create_forum(
            name='╰・୨🎭୧・projekty',
            category=category,
        )

        all_channels = created_text_channels + [discussion_channel]

        for i, ch in enumerate(all_channels):
            await ch.edit(position=i)
        
        await self.reply_defer_checked(interaction=interaction, content=f"Category '{full_name}' created with channels: {', '.join([c.name for c in all_channels])}", ephemeral=True)

setup = Create.setup