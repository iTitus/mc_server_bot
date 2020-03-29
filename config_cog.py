import json

from discord.ext import commands

from config import Config


class ConfigCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def config(self, ctx: commands.Context):
        await ctx.send('```json\n{}\n```'.format(json.dumps(Config.config_values(), indent=4)))


def setup(bot: commands.Bot):
    Config.load_config()

    bot.command_prefix = commands.when_mentioned_or(Config.command_prefix)

    bot.add_cog(ConfigCog(bot))


def teardown(bot: commands.Bot):
    pass
