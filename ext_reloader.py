import logging

from discord.ext import commands

import mc_server_bot
import util

log = logging.getLogger(__name__)


class ExtReloader(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx: commands.Context, *extensions: str):
        log.info('Reloading extensions:')

        for ext in mc_server_bot.extensions:
            if not extensions or ext in extensions:
                log.info('\tReloading \'{}\''.format(ext))
                if ext in self.bot.extensions:
                    self.bot.reload_extension(ext)
                else:
                    self.bot.load_extension(ext)

        log.info('Done reloading extensions!')

        await ctx.message.add_reaction(util.THUMBS_UP)


def setup(bot: commands.Bot):
    bot.add_cog(ExtReloader(bot))


def teardown(bot: commands.Bot):
    pass
