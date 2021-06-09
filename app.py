from os import getenv, listdir

import discord
from discord.ext import commands
from discord_slash import SlashCommand
from dotenv import load_dotenv

from static.scripts.get_json import get_json_file
from logg.logger import logger


load_dotenv('.env')

PREFIX = get_json_file('static/json_files/config.json')['prefix']
TOKEN = getenv('TOKEN')

bot = commands.Bot(PREFIX, intents=discord.Intents().all())
slash = SlashCommand(bot, sync_commands=True)


def load_cogs(bot: commands.Bot) -> None:
    for folder in listdir('cogs/'):
        if not folder.endswith('.py'):
            for filename in listdir(f'cogs/{folder}'):
                if not filename.startswith('__'):
                    bot.load_extension(f'cogs.{folder}.{filename[:-3]}')


def run_bot() -> None:
    try:
        load_cogs(bot)
        bot.run(TOKEN)
    except Exception:
        logger.error('праизашов какой та капэц в функции run_bot, иди чинить ._.')
