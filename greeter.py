import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class Greeter(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        log.info("We have logged in as {}".format(self.bot.user))


def setup(bot: commands.Bot):
    bot.add_cog(Greeter(bot))


def teardown(bot: commands.Bot):
    pass
