import logging, discord, os
from discord.ext import commands
from discord import app_commands
from .enviroment_vars import TESTING_GUILD_ID

log = logging.getLogger("bot")

class BaseCog(commands.Cog):

    COG_LABEL: str | None = None
    GUILDS: list | None = None
    OWNER_BYPASS = True

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.log("loaded")

    def log(self, msg: str, level: int = logging.INFO):
        log.log(level, f"[{self.__class__.__name__}] {msg}")

    async def reply_ephemeral(
        self,
        interaction: discord.Interaction,
        content: str | None = None,
        embed: discord.Embed | None = None,
        **kwargs,
    ):
        """Send an ephemeral reply"""
        if interaction.response.is_done():
            await interaction.followup.send(
                content=content,
                embed=embed,
                ephemeral=True,
                **kwargs,
            )
        else:
            await interaction.response.send_message(
                content=content,
                embed=embed,
                ephemeral=True,
                **kwargs,
            )


    async def cog_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError,
    ):
        self.log(f"{type(error).__name__}: {error}", logging.ERROR)

        await self.reply_ephemeral(
            interaction,
            "Something went wrong while executing that command. "
            "The incident has been logged."
        )

    async def can_run(self, command: app_commands.Command, interaction: discord.Interaction) -> bool:
        if self.OWNER_BYPASS and await self._owner_only(interaction):
            return True
        try:
            await command._check_can_run(interaction)
        except:
            return False
        return True
    
    @classmethod
    async def setup(cls, bot: commands.Bot):
        if BaseCog.GUILDS:
            await bot.add_cog(cls(bot), guilds=[discord.Object(id=gid) for gid in BaseCog.GUILDS])
        elif TESTING_GUILD_ID is not None:
            await bot.add_cog(cls(bot), guild=discord.Object(id=TESTING_GUILD_ID))
        else:
            await bot.add_cog(cls(bot))

    @staticmethod
    async def _owner_only(interaction: discord.Interaction) -> bool:
        """Return True if the invoking user is a bot owner."""
        return await interaction.client.is_owner(interaction.user)