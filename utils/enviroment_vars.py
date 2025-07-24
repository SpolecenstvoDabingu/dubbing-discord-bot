import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
TESTING_GUILD_ID = os.getenv("TESTING_GUILD_ID", None)

DABING_ADDRESS = os.getenv("DABING_ADDRESS", None)
DABING_TOKEN = os.getenv("DABING_TOKEN", None)

MAIN_GUILD_ID = os.getenv("MAIN_GUILD_ID", None)