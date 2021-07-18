import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext

from ORM.actions import get_user, update_description
from logg.logger import logger
from static.scripts.get_json import get_json_file


GUILD_IDS = get_json_file('static/json_files/guilds.json').get('guild_ids')


class BaseCommands(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.bot.remove_command('help')

    @cog_ext.cog_slash(name='help', guild_ids=GUILD_IDS, description='Получить помощь')
    async def _help(self, ctx: SlashContext) -> None:
        author = ctx.author

        help_embed = discord.Embed(title='Help', colour=0xffff00)
        help_embed.set_author(name=f'Использовал: {author}', icon_url=author.avatar_url)

        try:
            with open('static/other/help.txt', 'r', encoding='utf-8') as help_file:
                help_text = help_file.read()
        except FileNotFoundError:
            help_text = 'Произошла ошибка при использовании команды :/'
            logger.error('Файл help.txt не был найден')

        help_embed.add_field(name='** **', value=help_text)

        logger.info(f'Пользователь {ctx.author} использовал команду help')

        await ctx.send(embed=help_embed)

    @cog_ext.cog_slash(name='profile', guild_ids=GUILD_IDS, description='Получить профиль пользователя')
    async def profile(self, ctx: SlashContext, member: discord.Member = None) -> None:
        if member is None:
            member = ctx.author
        elif member.bot:
            await ctx.defer(hidden=True)
            await ctx.send('Нельзя указывать бота', hidden=True)
            return None

        user = get_user(member.id)

        profile_emb = discord.Embed(title=f'Профиль {member}', colour=0xffff00)
        profile_emb.set_author(name=f'Использовал {ctx.author}', icon_url=ctx.author.avatar_url)
        profile_emb.set_thumbnail(url=member.avatar_url)
        profile_emb.add_field(name='Никнейм:', value=f'{user.get("name")}', inline=False)
        profile_emb.add_field(name='Описание:', value=f'{user.get("description")}', inline=False)
        profile_emb.add_field(name='Предупреждения:', value=f'{user.get("warns")}')
        profile_emb.set_footer(text=f'id: {user.get("_id")}')

        logger.info(f'Пользователь {ctx.author} использовал команду profile')

        await ctx.send(embed=profile_emb)

    @cog_ext.cog_slash(name='avatar', guild_ids=GUILD_IDS, description='Получить аватар пользователя')
    async def avatar(self, ctx: SlashContext, member: discord.Member = None) -> None:
        if member is None:
            member = ctx.author
        avatar_embed = discord.Embed(title=f'Аватар {member}', colour=0xffff00)
        avatar_embed.set_author(name=f'Использовал {member}', icon_url=member.avatar_url)
        avatar_embed.set_image(url=member.avatar_url)

        logger.info(f'Пользователь {ctx.author} использовал команду avatar')

        await ctx.send(embed=avatar_embed)

    @cog_ext.cog_slash(name='report_bug', guild_ids=GUILD_IDS, description='Сообщить о баге')
    async def report_bug(self, ctx: SlashContext, bug: str) -> None:
        message = discord.Embed(title='Сообщение о баге', colour=0xffff00)
        message.set_author(name=f'Использовал {ctx.author}', icon_url=ctx.author.avatar_url)
        message.add_field(name='Баг:', value=bug)

        admins_list = get_json_file('static/json_files/admins.json').get('admins')

        for member_id in admins_list:
            member = ctx.guild.get_member(member_id)
            await member.send(embed=message)

        logger.info(f'Пользователь {ctx.author} использовал команду report_bug')
        
        await ctx.defer(hidden=True)
        await ctx.send('Ваше сообщение было успешно отправлено админам сервера', hidden=True)

    @cog_ext.cog_slash(name='set_description', guild_ids=GUILD_IDS, description='Изменить своё описание')
    async def set_description(self, ctx: SlashContext, new_description: str):
        update_description(ctx.author.id, new_description)

        logger.info(f'Пользователь {ctx.author} изменил своё описание на {new_description}')

        await ctx.defer(hidden=True)
        await ctx.send(f'Ваше описание было успешно изменено на: "{new_description}"', hidden=True)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(BaseCommands(bot))
