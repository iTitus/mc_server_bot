import logging

from discord.ext import commands

log = logging.getLogger(__name__)


class QuestSync(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def quest_sync(self, ctx: commands.Context):
        pass


def setup(bot: commands.Bot):
    bot.add_cog(QuestSync(bot))


def teardown(bot: commands.Bot):
    pass
