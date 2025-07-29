import discord
from discord import app_commands
from discord.ext import commands
from utils import BaseCog

class Ping(BaseCog):
    COG_LABEL = "Utilities"

    @app_commands.command(name="ping", description="Get the bot's latency.")
    @app_commands.check(BaseCog._owner_only)
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        latency_ms = round(self.bot.latency * 1000)
        await self.reply_defer_checked(interaction=interaction, content=f"Pong! '{latency_ms} ms'", ephemeral=True)

setup = Ping.setup