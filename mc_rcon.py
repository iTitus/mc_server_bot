import logging

from discord.ext import commands
from mcipc.rcon import Client

from config import Config

log = logging.getLogger(__name__)


class Rcon(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def rcon(self, ctx: commands.Context, *, command: str):
        log.info("RCON: '{}'".format(command))
        with Client(Config.mc_server_host, Config.rcon_port) as rcon:
            rcon.login(Config.rcon_password)
            resp: str = rcon.run(command)
            log.info("Response from RCON: '{}'".format(resp))
            if resp:
                await ctx.send(resp)


def setup(bot: commands.Bot):
    if Config.enable_rcon:
        bot.add_cog(Rcon(bot))


def teardown(bot: commands.Bot):
    pass
