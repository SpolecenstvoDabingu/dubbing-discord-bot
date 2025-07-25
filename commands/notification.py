import discord, asyncio
from discord import app_commands
from discord.ext import commands
from utils.base_cog import BaseCog
from typing import Literal
from utils.enviroment_vars import DABING_ADDRESS, DABING_TOKEN
from utils.request_get import request_get
from utils.request_post import request_post
from utils.bot import bot

class Notification(BaseCog):
    COG_LABEL = "Dubbing"

    @app_commands.command(name="notification", description="Let's you view and configure notifications about dubbing.")
    @app_commands.describe(state="Enable or disable notifications")
    async def notification(self, interaction: discord.Interaction, state: Literal["on", "off"] = None):
        url = f"{DABING_ADDRESS}/discord/commands/notification/{interaction.user.id}?token={DABING_TOKEN}"
        if state is None:
            response = await asyncio.to_thread(request_get, url)

            if not response.ok:
                await interaction.response.send_message(
                    "❌ Failed to parse response from server.",
                    ephemeral=True
                )
                return

            try:
                data = response.json()
            except Exception as e:
                await interaction.response.send_message(
                    f"❌ Failed to parse response from server.\nError: `{e}`",
                    ephemeral=True
                )
                return
            
            
            await interaction.response.send_message(
                f"You have notification {'enabled' if data.get('notification', False) else 'disabled'}.",
                ephemeral=True
            )
            return


        response_get = await asyncio.to_thread(request_get, url)

        if not response_get.ok:
            await interaction.response_get.send_message(
                "❌ Failed to parse response from server.",
                ephemeral=True
            )
            return

        try:
            data_get = response_get.json()
        except Exception as e:
            await interaction.response_get.send_message(
                f"❌ Failed to parse response from server.\nError: `{e}`",
                ephemeral=True
            )
            return
        
        response_post = await asyncio.to_thread(request_post, url, {"state": state})

        if not response_post.ok:
            await interaction.response_post.send_message(
                "❌ Failed to parse response from server.",
                ephemeral=True
            )
            return

        try:
            data_post = response_post.json()
        except Exception as e:
            await interaction.response_post.send_message(
                f"❌ Failed to parse response from server.\nError: `{e}`",
                ephemeral=True
            )
            return
        
        if data_get.get('notification', False) == data_post.get('notification', False):
            await interaction.response.send_message(
                f"Your notification has been unchanged: {'enabled' if data_get.get('notification', False) else 'disabled'} -> {'enabled' if data_post.get('notification', False) else 'disabled'}.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"Your notification has been modified: {'enabled' if data_get.get('notification', False) else 'disabled'} -> {'enabled' if data_post.get('notification', False) else 'disabled'}. {"You should be receiving message in your DM's, if not contact any Admin" if data_post.get('notification', False) else ""}",
            ephemeral=True
        )

        if data_post.get('notification', False):
            user = await bot.fetch_user(interaction.user.id)
            await user.send("This is testing message so you know if you will receive the notifications.")

        return

setup = Notification.setup