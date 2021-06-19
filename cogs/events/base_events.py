import discord
from discord.ext import commands

from static.scripts.get_json import get_json_file
from logg.logger import logger
from ORM.actions import add_to_db
from static.scripts.get_guild_objects import get_role
from static.scripts.update_admins import update_admins
from static.scripts.update_guilds import update_guilds


class BaseEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild) -> None:
        update_guilds('static/json_files/guilds.json', guild.id, 'append')

        logger.info(f'Бот присоединился к серверу {guild}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild) -> None:
        update_guilds('static/json_files/guilds.json', guild.id, 'remove')

        logger.info(f'Бот отключился от сервера {guild}')

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        logger.info('the bot was started')
        
        game = discord.Game(name='смотрит на /help')
        await self.bot.change_presence(activity=game, status=discord.Status.online)

    @commands.Cog.listener()
    async def on_member_join(self, member) -> None:
        logger.info(f'Пользователь {member} присоединился к серверу')

        if member.bot:
            bot_role = get_role(self.bot, 'bot', member.guild.id)
            await member.add_roles(bot_role)
        else:
            beginner_role = get_role(self.bot, 'beginner', member.guild.id)
            await member.add_roles(beginner_role)

        if not member.bot:
            add_to_db(member.id, member.name)
        logger.info(f'Пользователь {member} был успешно занесен в базу данных')

        channel = self.bot.get_channel(get_json_file('static/json_files/channels.json').get('gretting'))
        
        message = discord.Embed(title='Приветствие', colour=0xffff00)
        message.add_field(name='** **', value=f'Пользователь {member.mention} присоединился к серверу')
        message.set_thumbnail(url=member.avatar_url)

        await channel.send(embed=message)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        guild_id = before.guild.id
        admin_role = get_role(self.bot, 'admin', guild_id)
        moder_role = get_role(self.bot, 'moderator', guild_id)

        if (admin_role not in before.roles) and (admin_role in after.roles):
            update_admins('static/json_files/admins.json', 'admins', after.id, 'append')
            logger.info(f'Пользователь {before} получил роль {admin_role}')
        
        elif (moder_role not in before.roles) and (moder_role in after.roles):
            update_admins('static/json_files/admins.json', 'moderators', after.id, 'append')
            logger.info(f'Пользователь {before} получил роль {moder_role}')

        elif (admin_role in before.roles) and (admin_role not in after.roles):
            update_admins('static/json_files/admins.json', 'admins', after.id, 'remove')
            logger.info(f'Пользователь {before} лишился роли {admin_role}')
        
        elif (moder_role in before.roles) and (moder_role not in after.roles):
            update_admins('static/json_files/admins.json', 'moderators', after.id, 'remove')
            logger.info(f'Пользователь {before} лишился роли {moder_role}')


def setup(bot: commands.Bot) -> None:
    bot.add_cog(BaseEvents(bot))
