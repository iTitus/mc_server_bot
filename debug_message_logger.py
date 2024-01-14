import logging
from typing import Union

import discord
from discord.ext import commands

log = logging.getLogger(__name__)


class DebugMessageLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        channel: Union[discord.abc.Messageable] = message.channel
        channel_str: str = str(channel)
        if isinstance(channel, discord.abc.GuildChannel):
            guild_channel: discord.abc.GuildChannel = channel
            channel_str = str(guild_channel.guild) + "#" + channel_str

        author: discord.abc.User = message.author
        log.info("[{}] {}: {}".format(channel_str, author, message.content))


def setup(bot: commands.Bot):
    bot.add_cog(DebugMessageLogger(bot))


def teardown(bot: commands.Bot):
    pass
