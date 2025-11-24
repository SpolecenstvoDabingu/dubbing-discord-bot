import discord
from utils.enviroment_vars import DABING_ADDRESS_EXTERNAL, TRAINING_CHANNEL_ID
from utils.exceptions import DabbingURLNotDefined, TrainingChannelNotDefined

async def send_welcome_message(member: discord.Member):
    try:
        if DABING_ADDRESS_EXTERNAL is None:
            raise DabbingURLNotDefined
        if TRAINING_CHANNEL_ID is None:
            raise TrainingChannelNotDefined

        embed = discord.Embed(
            title=f"Vítej na serveru, {member.name}! 🎉",
            description=(
                "Jsme rádi, že jsi se připojil/a k našemu serveru.\n\n"
                f"➡️ **Přihlas se na stránku projektů:** [Klikni zde]({DABING_ADDRESS_EXTERNAL})\n"
                f"➡️ **Nezapomeň si naplánovat školení na serveru:** <#{int(TRAINING_CHANNEL_ID)}>"
            ),
            color=0x00AE86
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
        embed.set_footer(text="Těšíme se na spolupráci!")
        embed.timestamp = discord.utils.utcnow()

        # Send DM
        await member.send(embed=embed)
    except discord.Forbidden:
        print(f"Nemohu poslat DM uživateli {member.name}.")
    except DabbingURLNotDefined:
        print(f"Není definovaná adresa stránky.")
    except TrainingChannelNotDefined:
        print(f"Není definován ID školícího channelu")
    except Exception as e:
        print(f"Nastala chyba při posílání uvítací zprávy: {e}")