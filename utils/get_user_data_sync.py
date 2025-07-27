import discord

def get_user_data_sync(user:discord.User) -> dict:
    data = {
        "id": str(user.id),
        "avatar": user.avatar.url if user.avatar else "https://cdn.discordapp.com/embed/avatars/0.png",
        "name": str(user.nick or user.name),
        "display_name": str(user.display_name),
    }
    return data