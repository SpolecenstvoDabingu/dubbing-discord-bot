import discord
from discord import app_commands
from discord.ext import commands
from utils.base_cog import BaseCog

class Clear(BaseCog):
    COG_LABEL = "Utilities"

    @app_commands.command(name="clear", description="Delete messages.")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, user: discord.User = None, user_id: int = None, amount: int | None = None):
        await interaction.response.defer(ephemeral=True)

        channel = interaction.channel

        if not isinstance(channel, discord.TextChannel | discord.Thread):
            await  self.reply_ephemeral(interaction=interaction, content="This command can only be used in text channels.")
            return
        
        def check(msg: discord.Message):
            if user:
                    return msg.author.id == user.id
            elif user_id:
                    return msg.author.id == user_id
            return True

        try:
            deleted = await channel.purge(limit=amount or None, check=check)
            await  self.reply_ephemeral(
                interaction=interaction,
                content=f"Deleted {len(deleted)} message{'s' if len(deleted) > 1 else ''}{f'from {user.mention if user else user_id}' if user or user_id else ''}.",
            )
        except discord.Forbidden:
            await  self.reply_ephemeral(interaction=interaction, content="I don't have permission to delete messages here.")
        except discord.HTTPException as e:
            await  self.reply_ephemeral(interaction=interaction, content=f"Failed to delete messages: {e}")

setup = Clear.setup