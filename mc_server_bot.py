#!/usr/bin/env python

import logging
from typing import Tuple

from discord.ext import commands

from config import Config

extensions: Tuple[str, ...] = (
    'config',
    'util',
    'ext_reloader',
    'error_handler',
    'shutdown',
    'greeter',
    'ip',
    'mc_query',
    'mc_rcon',
    'mc_chat_relay',
    'quest_sync',
    'debug_message_logger'
)


def main():
    logging.basicConfig(level=logging.INFO)

    bot: commands.Bot = commands.Bot(commands.when_mentioned_or(Config.command_prefix))

    for ext in extensions:
        bot.load_extension(ext)

    bot.run(Config.token)


if __name__ == '__main__':
    main()
