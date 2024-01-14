import logging
import traceback
from typing import List, Type

from discord.ext import commands

log = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, e: commands.CommandError):
        etype: Type[commands.CommandError] = type(e)
        stype: str = etype.__qualname__
        smod: str = etype.__module__
        if smod not in ("__main__", "builtins"):
            stype = smod + "." + stype
        first: str = "Error in command '{ctx.command}': [{type}] {e}\n".format(
            ctx=ctx, type=stype, e=e
        )
        lines: List[str, ...] = [first]
        lines.extend(traceback.format_exception(type(e), e, e.__traceback__))
        joined: str = "".join(lines)
        for line in joined.splitlines():
            log.error(line)
        await ctx.send(first)


def setup(bot: commands.Bot):
    bot.add_cog(ErrorHandler(bot))


def teardown(bot: commands.Bot):
    pass
