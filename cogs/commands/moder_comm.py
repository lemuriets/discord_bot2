from asyncio import sleep

import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from logg.logger import logger
from ORM.actions import give_warn, get_user
from static.scripts.get_guild_objects import get_role, get_channel
from static.scripts.get_json import get_json_file


GUILD_IDS = get_json_file('static/json_files/guilds.json').get('guild_ids')


def send_messages(action: str):
    def decorator(func):
        async def wrapper(self, ctx: SlashContext, member: discord.Member, reason: str) -> None:
            message = discord.Embed(title=f'{action} пользователя', colour=0xffff00)
            if action.lower() == 'бан':
                message.add_field(name='** **', value=f'Вы успешно забанили пользователя {member} по причине: "{reason}"')

                logger.info(f'Пользователь {member} был успешно забанен на сервере {ctx.guild} пользователем {ctx.author}')

                await member.send(f'Вас забанили на сервере **{self.bot.get_guild(ctx.guild_id).name}** по причине: "{reason}"')
            elif action.lower() == 'кик':
                message.add_field(name='** **', value=f'Вы успешно кикнули пользователя {member} по причине: "{reason}"')

                logger.info(f'Пользователь {member} был успешно кикнут с сервера {ctx.guild} пользователем {ctx.author}')

                await member.send(f'Вас кикнули с сервера **{self.bot.get_guild(ctx.guild_id).name}** по причине: "{reason}"')

            await func(self, ctx, member, reason)

            await ctx.author.send(embed=message)
            await ctx.defer(hidden=True)
            await ctx.send('успешно', hidden=True)
        return wrapper
    return decorator


class ModerCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @cog_ext.cog_slash(name='ban', guild_ids=GUILD_IDS, description='Забанить указанного пользователя')
    @commands.has_permissions(ban_members=True)
    @send_messages('Бан')
    async def ban(self, ctx: SlashContext, member: discord.Member, reason: str) -> None:
        await member.ban(reason=reason)

    @cog_ext.cog_slash(name='unban', guild_ids=GUILD_IDS, description='Разбанить указанного пользователя')
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx: SlashContext, member: str) -> None:
        bans_list = await ctx.guild.bans()

        if len(bans_list) == 0:
            await ctx.defer(hidden=True)
            await ctx.send('На сервере нет забаненных пользователей')
            return None
        
        member_name_descriminator = member.split('#')

        for user in bans_list:
            if [user.user.name, user.user.discriminator] == member_name_descriminator:
                await ctx.guild.unban(user.user)
                logger.info(f'Пользователь {member} был разбанен {ctx.author}')

                message = discord.Embed(description=f'Пользователь {member} был разбанен {ctx.author.mention}', colour=0xffff00)

                await ctx.defer(hidden=True)
                await ctx.send('успешно', hidden=True)
                break
            else:
                await ctx.defer(hidden=True)
                await ctx.send(f'Пользователь {member} не забанен')
                return None

        channel = get_channel(self.bot, 'notifications')

        await channel.send(embed=message)
    
    @cog_ext.cog_slash(name='kick', guild_ids=GUILD_IDS, description='Кикнуть указанного пользователя')
    @commands.has_permissions(kick_members=True)
    @send_messages('Кик')
    async def kick(self, ctx: SlashContext, member: discord.Member, reason: str) -> None:
        await member.kick(reason=reason)

    @cog_ext.cog_slash(name='clear', guild_ids=GUILD_IDS, description='Очистка канала')
    @commands.has_permissions(ban_members=True)
    async def clear(self, ctx: SlashContext, value: int) -> None:
        if value > 200:
            await ctx.send(embed=discord.Embed(title='Указано слишком большое значение', colour=0xd00000))
            return None
        await ctx.channel.purge(limit=value + 1)

        logger.info(f'Пользователь {ctx.author} удалил {value} сообщений в канале "{ctx.channel}"')

        message = discord.Embed(title='Очистка чата', description=f'Было удалено {value} сообщений', colour=0xffff00)
        message.set_author(name=f'Использовал {ctx.author}', icon_url=ctx.author.avatar_url)

        await ctx.send(embed=message)
        
    @cog_ext.cog_slash(name='warn', guild_ids=GUILD_IDS, description='Выдать предупреждение указанному пользователю')
    @commands.has_permissions(kick_members=True)
    async def warn(self, ctx: SlashContext, member: discord.Member, reason: str) -> None:
        give_warn(member.id)

        user_warns = get_user(member.id).get('warns')

        logger.info(f'Пользователь {member} получил {user_warns} предупреждение')

        message = discord.Embed(description=f'Пользователь {member.mention} получил предупреждение по причине: {reason}')
        message.add_field(name=f'Кол-во предупреждений {member}:', value=user_warns)

        channel = get_channel(self.bot, 'notifications')

        await channel.send(embed=message)
        await ctx.defer(hidden=True)
        await ctx.send('успешно', hidden=True)

    @cog_ext.cog_slash(name='mute', guild_ids=GUILD_IDS, description='Замьютить указанного пользователя')
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx: SlashContext, member: discord.Member, reason: str, time: str = None) -> None:
        mute_role = get_role(self.bot, 'mute', ctx.guild_id)

        if mute_role in member.roles:
            await ctx.defer(hidden=True)
            await ctx.send('Указанный пользователь уже замьючен')
            return None


        def time_format(t: str) -> int:
            try:
                if len(t) > 1:
                    int(t[:-1:])
                else:
                    int(t)
            except ValueError:
                return None
                
            time_values = {
                's': lambda t: int(t),
                'm': lambda t: int(t) * 60,
                'h': lambda t: int(t) * 60 ** 2,
                'd': lambda t: int(t) * 60 ** 2 * 24
            }

            if not t[-1].isalpha():
                t = int(t)
            elif (t[-1] in time_values.keys()):
                t = time_values.get(t[-1])(t[:-1:])
            else:
                return None
            
            return t


        channel = get_channel(self.bot, 'notifications')

        message = discord.Embed(description='', colour=0xffff00)
        message.add_field(name='Причина:', value=f'```{reason}```')

        end_mute_message = discord.Embed(description=f'Закончился срок {mute_role.mention} у пользователя {member.mention}', colour=0xffff00)

        if time is not None:
            time_for_display = time
            time = time_format(time)

            if time is None:
                await ctx.defer(hidden=True)
                await ctx.send('Указан неверный формат времени. Пример записи времени: 10s', hidden=True)
                return None
            elif time == 0:
                await ctx.defer(hidden=True)
                await ctx.send('ну и зачем указывать 0?..', hidden=True)
                return None
            
            message.description = f'{ctx.author.mention} выдал {mute_role.mention} пользователю {member.mention} на срок: {time_for_display}'

            await member.add_roles(mute_role)
            await channel.send(embed=message)

            await ctx.defer(hidden=True)
            await ctx.send('успешно')

            await sleep(time)

            if mute_role in member.roles:
                await member.remove_roles(mute_role)
                await channel.send(embed=end_mute_message)
                logger.info(f'Закончился срок {mute_role} у пользователя {member}')

            return None
        
        await member.add_roles(mute_role)
        message.description = f'{ctx.author.mention} выдал {mute_role.mention} пользователю {member.mention} на срок: пока не снимут'
        logger.info(f'{ctx.author} выдал {mute_role} пользователю {member} на срок: пока не снимут')

        await channel.send(embed=message)
        await ctx.defer(hidden=True)
        await ctx.send('успешно')

    @cog_ext.cog_slash(name='unmute', guild_ids=GUILD_IDS, description='Размьютить мут указанному пользователю')
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx: SlashContext, member: discord.Member) -> None:
        mute_role = get_role(self.bot, 'mute', ctx.guild_id)
        channel = get_channel(self.bot, 'notifications')
        message = discord.Embed(colour=0xffff00)

        if mute_role in member.roles:
            message.description = f'{ctx.author.mention} снял {mute_role.mention} у пользователя {member.mention}'
            await member.remove_roles(mute_role)
            logger.info(f'{ctx.author} снял {mute_role.mention} у пользователя {member}')
        else:
            message.description = f'{ctx.author.mention}, пользователь {member.mention} не замьючен'
            logger.info(f'{ctx.author} пытался снять мьют с {member}')

        await channel.send(embed=message)
        await ctx.defer(hidden=True)
        await ctx.send('успешно', hidden=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ModerCommands(bot))
