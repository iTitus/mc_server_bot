import json
import os

from discord.ext import commands

_config_file: str = 'config.json'


class ConfigCog(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.dm_only()
    async def config(self, ctx: commands.Context):
        await ctx.send('```json\n{}\n```'.format(json.dumps(config.__dict__, indent=4)))


class Config:

    def __init__(self, **kwargs):
        self.__load(**kwargs)

    def __load(self, *,
               token: str = None,
               command_prefix: str = '$',
               mc_server_host: str = None,
               enable_query: bool = False,
               query_port: int = -1,
               enable_mc_chat_relay: bool = False,
               webhook_id: int = -1,
               webhook_token: str = None,
               server_dir: str = None,
               server_world: str = 'world',
               mc_chat_relay_channel: int = -1,
               enable_rcon: bool = False,
               rcon_port: int = -1,
               rcon_password: str = None
               ):
        self.token: str = token
        self.command_prefix: str = command_prefix
        self.mc_server_host: str = mc_server_host
        self.enable_query: bool = enable_query
        self.query_port: int = query_port
        self.enable_mc_chat_relay: bool = enable_mc_chat_relay
        self.mc_chat_relay_channel: int = mc_chat_relay_channel
        self.webhook_id: int = webhook_id
        self.webhook_token: str = webhook_token
        self.server_dir: str = server_dir
        self.server_world: str = server_world
        self.enable_rcon: bool = enable_rcon
        self.rcon_port: int = rcon_port
        self.rcon_password: str = rcon_password

    def load_config(self):
        if not os.path.exists(_config_file):
            self.__load()
            self.save_config()
        else:
            with open(_config_file, 'r') as fp:
                self.__load(**json.load(fp))
            self.save_config()

    def save_config(self):
        with open(_config_file, 'w') as fp:
            json.dump(self.__dict__, fp, indent=4)


config: Config = Config()


def setup(bot: commands.Bot):
    config.load_config()

    bot.command_prefix = commands.when_mentioned_or(config.command_prefix)

    bot.add_cog(ConfigCog(bot))


def teardown(bot: commands.Bot):
    pass
