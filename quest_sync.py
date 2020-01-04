import json
import logging
import os
from collections import defaultdict
from typing import Tuple, Mapping, Dict, Set

from discord.ext import commands
from mcipc.rcon import Client

from config import config

log = logging.getLogger(__name__)


class BetterQuestingData:
    name_cache = {}
    quest_progress = {}
    life_database = {}
    quest_database = {}
    questing_parties = {}

    def __init__(self, path: str):
        self.__load(path)

    def __load(self, path: str):
        with open(os.path.join(path, 'NameCache.json')) as f:
            self.name_cache.update(json.load(f))

        with open(os.path.join(path, 'QuestProgress.json')) as f:
            self.quest_progress.update(json.load(f))

        with open(os.path.join(path, 'LifeDatabase.json')) as f:
            self.life_database.update(json.load(f))

        with open(os.path.join(path, 'QuestDatabase.json')) as f:
            self.quest_database.update(json.load(f))

        with open(os.path.join(path, 'QuestingParties.json')) as f:
            self.questing_parties.update(json.load(f))

    def get_parties(self):
        return self.questing_parties['parties:9'].values()

    def get_quest_database(self):
        return self.quest_database['questDatabase:9'].values()

    def get_quest(self, quest_id: int):
        for quest in self.get_quest_database():
            if quest['questID:3'] == quest_id:
                return quest

        raise KeyError

    def get_name_cache(self):
        return self.name_cache['nameCache:9'].values()

    def get_quest_progress(self):
        return self.quest_progress['questProgress:9'].values()

    def get_name_from_cache(self, uuid: str) -> str:
        for cache_entry in self.get_name_cache():
            if cache_entry['uuid:8'] == uuid:
                return cache_entry['name:8']

        raise KeyError

    def get_members(self, party: Mapping) -> Tuple[str, ...]:
        uuids = map(lambda m: m['uuid:8'], party['members:9'].values())
        return tuple(map(self.get_name_from_cache, uuids))

    def is_normal_quest(self, quest_id: int):
        quest = self.get_quest(quest_id)
        properties = quest['properties:10']
        return properties['repeattime:3'] == -1 and properties['globalshare:1'] == 0


class QuestSync(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def quest_sync(self, ctx: commands.Context):
        log.info('Syncing quests...')

        quests: Dict[int, Set[str]] = defaultdict(set)

        data_path = os.path.join(config.server_dir, config.server_world, 'betterquesting')
        data = BetterQuestingData(data_path)

        parties = tuple(map(data.get_members, data.get_parties()))

        for quest_progress in data.get_quest_progress():
            quest_id: int = quest_progress['questID:3']
            if not data.is_normal_quest(quest_id):
                continue

            completed = tuple(
                map(
                    data.get_name_from_cache,
                    map(
                        lambda m: m['uuid:8'],
                        quest_progress['completed:9'].values()
                    )
                )
            )

            for completed_user in completed:
                for party_members in parties:
                    if completed_user in party_members:
                        to_add = tuple(filter(lambda u: u not in completed, party_members))
                        if len(to_add) > 0:
                            quests[quest_id].update(to_add)

        log.info('To sync:')
        log.info(json.dumps(quests, sort_keys=True, indent=4, default=_convert_to_serializable))

        unlock_quests(quests)

        await ctx.send('Synced {} quests.'.format(len(quests)))


def _convert_to_serializable(o):
    if isinstance(o, set):
        return list(o)

    raise TypeError


def unlock_quests(quests: Dict[int, Set[str]]):
    with Client(config.mc_server_host, config.rcon_port) as c:
        c.login(config.rcon_password)
        for quest_id, players in quests.items():
            for player in players:
                c.run('bq_admin', 'complete', str(quest_id), player)


def setup(bot: commands.Bot):
    if config.server_dir and config.enable_rcon:
        bot.add_cog(QuestSync(bot))


def teardown(bot: commands.Bot):
    pass
