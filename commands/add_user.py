import discord, asyncio
from discord import app_commands
from discord.ext import commands
from utils import BaseCog, DABING_ADDRESS, DABING_TOKEN, request_post
from utils import bot

class AddUser(BaseCog):
    COG_LABEL = "Utilities"

    @app_commands.command(name="add_user", description="Creates new dubbing category.")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_user(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer(ephemeral=True)
        
        data = await self.create_custom_user(interaction, user)
        if data is None:
            await self.reply_defer_checked(interaction=interaction, content=f"Adding user to DB failed.", ephemeral=True)
            return
        await self.reply_defer_checked(interaction=interaction, content=f"Adding user to DB was succesfull.", ephemeral=True)

    async def create_custom_user(self, interaction: discord.Interaction, user: discord.User):
        url = f"{DABING_ADDRESS}/discord/user/custom/add?token={DABING_TOKEN}"
        data = {
            "data":{
                "id": user.id,
                "name": f"{user.name}",
                "display_name": f"{user.global_name or user.name}",
                "avatar": f"{user.display_avatar.url}"
            }
        }
        response = await asyncio.to_thread(request_post, url, json=data)

        if not response.ok:
            return None
        return data

setup = AddUser.setup