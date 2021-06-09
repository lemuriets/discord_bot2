import discord
from discord.ext import commands

from static.scripts.get_json import get_json_file


class VoiceEvents(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after) -> None:
        guild = self.bot.get_guild(member.guild.id)
        channel_id = get_json_file('static/json_files/channels.json').get('create_voice_channel')
        category_id = get_json_file('static/json_files/categories.json').get('voice')
        category = discord.utils.get(guild.categories, id=category_id)

        if after.channel is not None:
            if after.channel.id == channel_id:
                author = str(member)[:-5:]
                private_channel = await guild.create_voice_channel(name=f'{author}\'s channel', category=category)
                await member.move_to(private_channel)

                def check(*args):
                    return len(private_channel.members) == 0

                await self.bot.wait_for('voice_state_update', check=check)
                await private_channel.delete()


def setup(bot: commands.Bot) -> None:
    bot.add_cog(VoiceEvents(bot))
