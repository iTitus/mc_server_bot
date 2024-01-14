import json
import logging
from typing import Union

from discord.ext import commands
from discord.ext.commands import BadArgument
from mcipc.query import Client
from mcipc.query.proto.basic_stats import BasicStats
from mcipc.query.proto.full_stats import FullStats

from config import Config

log = logging.getLogger(__name__)


class Query(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    async def query(self, ctx: commands.Context, mode: str = "basic"):
        log.info("Query: '{}'".format(mode))

        if mode not in ("basic", "full"):
            raise BadArgument(
                "Mode '{}' is invalid. Valid modes are 'basic' or 'full'.".format(mode)
            )

        with Client(Config.mc_server_host, Config.query_port) as query:
            resp: Union[BasicStats, FullStats] = (
                query.basic_stats if mode == "basic" else query.full_stats
            )
            log.info("Response from Query: '{}'".format(resp))
            await ctx.send(
                "```json\n{}\n```".format(json.dumps(resp.to_json(), indent=4))
            )


def setup(bot: commands.Bot):
    if Config.enable_query:
        bot.add_cog(Query(bot))


def teardown(bot: commands.Bot):
    pass
