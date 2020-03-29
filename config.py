import json
import logging
import os
from json import JSONDecodeError

log = logging.getLogger(__name__)
_config_file: str = 'config.json'

log.info('Loading config.py file')

class Config:
    token: str = ''
    command_prefix: str = '$'
    mc_server_host: str = ''
    enable_query: bool = False
    query_port: int = -1
    enable_mc_chat_relay: bool = False
    webhook_id: int = -1
    webhook_token: str = ''
    server_dir: str = ''
    server_world: str = 'world'
    mc_chat_relay_channel: int = -1
    enable_rcon: bool = False
    rcon_port: int = -1
    rcon_password: str = ''
    quest_sync: bool = False

    @staticmethod
    def __load(**kwargs):
        for k, v in kwargs.items():
            if Config.is_config_value(k):
                setattr(Config, k, v)
            else:
                log.error('Malicious config value {}={}'.format(k, v))

    @staticmethod
    def load_config():
        if os.path.exists(_config_file):
            with open(_config_file, 'r') as fp:
                try:
                    Config.__load(**json.load(fp))
                except JSONDecodeError as e:
                    log.error('Error while loading config:', exc_info=e)
        Config.save_config()

    @staticmethod
    def save_config():
        with open(_config_file, 'w') as fp:
            json.dump(Config.config_values(), fp, indent=4)

    @staticmethod
    def config_values():
        config_values = {}

        for k, v in Config.__dict__.items():
            if Config.is_config_value(k):
                config_values[k] = v

        return config_values

    @staticmethod
    def is_config_value(k: str) -> bool:
        if k.startswith('_'):
            return False
        elif k not in Config.__dict__:
            return True

        v = Config.__dict__[k]
        if isinstance(v, (str, bool, int, float)):
            return True
        return False
