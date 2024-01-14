import re

from discord import utils
from discord.ext import commands

THUMBS_UP: str = "\U0001F44D"
WAVE: str = "\U0001F44B"


def escape_all(msg: str) -> str:
    return utils.escape_markdown(escape_mentions(msg))


def escape_mentions(msg: str) -> str:
    msg = re.sub(r"@(everyone|here)", "@\u200b\\1", msg)
    msg = re.sub(r"<@([!&][0-9]{17,21})>", "<@\u200b\\1>", msg)
    return re.sub(r"<#([0-9]{17,21})>", "<#\u200b\\1>", msg)


def setup(bot: commands.Bot):
    pass


def teardown(bot: commands.Bot):
    pass
