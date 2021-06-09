import discord
from discord.ext.commands import Bot

from static.scripts.get_json import get_json_file


def get_role(bot: Bot, role_name: str, guild_id: int) -> discord.Role:
    role_id = get_json_file('static/json_files/roles.json').get(role_name)
    role = bot.get_guild(guild_id).get_role(role_id)
    return role


def get_channel(bot: Bot, channel_name: str):
    channel_id = get_json_file('static/json_files/channels.json').get(channel_name)
    channel = bot.get_channel(channel_id)
    return channel
