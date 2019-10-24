import logging
import urllib.request

from discord.ext import commands

log = logging.getLogger(__name__)


def get_ip():
    log.info('Requesting public ip:')
    with urllib.request.urlopen('https://v4.ident.me/') as f:
        ip: str = f.read().decode('utf-8')
        log.info('\tGot {}'.format(ip))
        return ip


class Ip(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def ip(self, ctx: commands.Context):
        await ctx.send('IP is {}!'.format(get_ip()))


def setup(bot: commands.Bot):
    bot.add_cog(Ip(bot))


def teardown(bot: commands.Bot):
    pass
