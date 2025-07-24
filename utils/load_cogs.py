import os
from discord.ext import commands

async def load_cogs(bot: commands.Bot):
    for package in ["commands"]:
        for filename in os.listdir(f"./{package}"):
            if filename.endswith(".py"):
                ext = f"{package}.{filename[:-3]}"
                try:
                    await bot.load_extension(ext)
                    print(f"Loaded '{ext}'")
                except Exception as e:
                    print(f"Failed to load '{ext}': {e}")