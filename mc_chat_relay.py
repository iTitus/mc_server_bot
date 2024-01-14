import io
import json
import logging
import os
import re
import time
import traceback
from multiprocessing import Process
from typing import Optional, Pattern, Match, Any, Generator

import discord
from discord import Webhook, RequestsWebhookAdapter
from discord.ext import commands
from mcipc.rcon import Client
from typing.io import TextIO

import util
from config import Config

log = logging.getLogger(__name__)
_mc_log_reader_process: Optional[Process] = None
_mc_log_pattern: Pattern = re.compile(
    r"^.*?(?:\[net\.minecraft\.server\.dedicated\.DedicatedServer\]):\s*"
    r"(?P<message>(?:(?:(?:(?P<me_opener>\* )|(?P<chat_opener><))(?P<name>.*?)(?(chat_opener)(?:> )|(?: ))"
    r"(?P<chat_message>.*?))|(?:.*?)))"
    r"\s*$"
)


def _create_chat_msg_obj(name: str, message: str) -> Any:
    return [
        {
            "color": "white",
            "text": "[{name}] {message}".format(name=name, message=message),
        }
    ]


def _follow(log_file_path: str) -> Generator[str, None, None]:
    class FileWrapper:
        __log_file: Optional[TextIO] = None
        __first: bool = True

        @property
        def file(self):
            if not self.__log_file or self.__log_file.closed:
                self.__log_file = open(file=log_file_path, mode="rt", buffering=1)
                if self.__first:
                    self.__log_file.seek(0, io.SEEK_END)
                    self.__first = False
                else:
                    self.__log_file.seek(0)

            return self.__log_file

        def close(self):
            if self.__log_file and not self.__log_file.closed:
                self.__log_file.close()

    w: FileWrapper = FileWrapper()

    while True:
        line: str = w.file.readline()
        if not line:
            pos: int = w.file.tell()
            size: int = os.path.getsize(log_file_path)
            if (
                pos != size
            ):  # log file size changed without reading -> new server instance started
                w.close()  # acquire new filehandle
            else:
                try:
                    time.sleep(0.1)
                except KeyboardInterrupt:
                    w.close()
                    break
            continue
        yield line


def _read_log(server_dir: str, webhook_id, webhook_token):
    webhook = Webhook.partial(
        webhook_id, webhook_token, adapter=RequestsWebhookAdapter()
    )
    for line in _follow(os.path.join(server_dir, "logs", "latest.log")):
        match: Optional[Match] = re.fullmatch(_mc_log_pattern, line)
        if match:
            msg: str = match.group("message")
            chat_msg: str = match.group("chat_message")
            me_opener: str = match.group("me_opener")
            chat_opener: str = match.group("chat_opener")
            name: str = match.group("name")
            log.info("Found relevant log line: {}".format(line[:-1]))
            try:
                if me_opener and chat_msg:
                    webhook.send(
                        "*{}*".format(util.escape_all(chat_msg)),
                        username=name,
                        avatar_url="https://minotar.net/helm/{}/256.png".format(name),
                    )
                elif chat_opener and chat_msg:
                    webhook.send(
                        util.escape_all(chat_msg),
                        username=name,
                        avatar_url="https://minotar.net/helm/{}/256.png".format(name),
                    )
                elif msg:
                    webhook.send(util.escape_all(msg))
                else:
                    log.error("Unknown message type, did not send: {}".format(msg))
            except Exception as e:
                log.error("Error while sending webhook message: {}".format(msg))
                for tb_line in "".join(
                    traceback.format_exception(type(e), e, e.__traceback__)
                ).splitlines():
                    log.error(tb_line)
        else:
            log.info("Ignoring line: {}".format(line[:-1]))


class McChatRelay(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        await self.__send_to_mc(message)

    def __should_not_send_to_mc(self, message: discord.Message) -> bool:
        return (
            not message.content
            or message.webhook_id == Config.webhook_id
            or message.channel.id != Config.mc_chat_relay_channel
        )

    async def __send_to_mc(self, message: discord.Message):
        if self.__should_not_send_to_mc(message):
            return

        try:
            with Client(Config.mc_server_host, Config.rcon_port) as rcon:
                rcon.login(Config.rcon_password)
                msg_obj: Any = _create_chat_msg_obj(
                    message.author, message.clean_content
                )
                msg: str = json.dumps(msg_obj)
                log.info("Sending RCON tellraw message: {}".format(msg))
                resp: str = rcon.run("tellraw", "@a", msg)
                if resp:
                    log.info("Response from RCON: {}".format(resp))
        except Exception as e:
            log.error(
                "Error while sending RCON message: {}: {}".format(
                    message.author, message.clean_content
                )
            )
            for tb_line in "".join(
                traceback.format_exception(type(e), e, e.__traceback__)
            ).splitlines():
                log.error(tb_line)


def setup(bot: commands.Bot):
    if Config.enable_mc_chat_relay and Config.enable_rcon:
        bot.add_cog(McChatRelay(bot))
        global _mc_log_reader_process
        _mc_log_reader_process = Process(
            target=_read_log,
            name="minecraft_log_reader",
            args=(Config.server_dir, Config.webhook_id, Config.webhook_token),
        )
        _mc_log_reader_process.start()


def teardown(bot: commands.Bot):
    if _mc_log_reader_process:
        _mc_log_reader_process.kill()
