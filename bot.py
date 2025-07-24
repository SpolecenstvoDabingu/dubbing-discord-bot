import discord, os, asyncio
from utils.load_cogs import load_cogs
from utils.load_events import load_events
from utils.bot import bot
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("DISCORD_TOKEN")
TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID", None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} ({bot.user.id})")

    try:
        if TESTING_GUILD_ID is not None:
            print(f"Syncing guild '{TESTING_GUILD_ID}'")
            guild = discord.Object(id=TESTING_GUILD_ID)
            synced = await bot.tree.sync(guild=guild)
        else:
            synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global commands")
    except Exception as e:
        print(f"Slash-command sync failed: {e}")


async def main():
    async with bot:
        await load_events(bot)
        await load_cogs(bot)
        await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())