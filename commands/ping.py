import discord
from discord import app_commands
from discord.ext import commands
from utils import BaseCog

class Ping(BaseCog):
    COG_LABEL = "Utilities"

    @app_commands.command(name="ping", description="Get the bot's latency.")
    @app_commands.check(BaseCog._owner_only)
    async def ping(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await self.reply_ephemeral(interaction=interaction, content=f"Pong! '{latency_ms} ms'")

setup = Ping.setup