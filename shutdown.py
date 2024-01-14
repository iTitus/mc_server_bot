import logging

from discord.ext import commands

import util

log = logging.getLogger(__name__)


class Shutdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx: commands.Context):
        log.info("Initiating shutdown")
        await ctx.message.add_reaction(util.WAVE)
        self.bot.loop.stop()


def setup(bot: commands.Bot):
    bot.add_cog(Shutdown(bot))


def teardown(bot: commands.Bot):
    pass
