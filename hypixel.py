"""
                              _
__   _____  ___  ___ ___   __| | ___ _ __
\ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
 \ V /\__ \  __/ (_| (_) | (_| |  __/ |
  \_/ |___/\___|\___\___/ \__,_|\___|_|

  Copyleft 2022 t.me/vsecoder
  This program is free software; you can redistribute it and/or modify

"""


# meta developer: @vsecoder_m
# meta desc: Module for getting information about minecraft Hypixel player
# meta pic: https://img.icons8.com/cute-clipart/64/minecraft-logo.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/cute-clipart/64/minecraft-logo.png&title=Hypixel&description=Module%20for%20getting%20information%20about%20minecraft%20Hypixel%20player

__version__ = (1, 1, 1)

import logging
import aiohttp
from telethon import TelegramClient
from telethon.tl.types import Message
from .. import loader, utils  # type: ignore


logger = logging.getLogger(__name__)


class HypixelAPI:
    def __init__(self, token):
        self.token = token
        self.api = "https://api.hypixel.net"

        self.uuid_link = "https://api.mojang.com/users/profiles/minecraft/{}"

    async def _request(self, url: str, method: str = "GET") -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url) as response:
                return await response.json()

    async def get_uuid(self, nickname):
        link = self.uuid_link.format(nickname)
        return await self._request(link)

    async def get_player_data(self, uuid):
        link = f"{self.api}/player?key={self.token}&uuid={uuid}"
        return await self._request(link)

    async def recent_games(self, uuid):
        link = f"{self.api}/recentgames?key={self.token}&uuid={uuid}"
        return await self._request(link)

    async def player_status(self, uuid):
        link = f"{self.api}/status?key={self.token}&uuid={uuid}"
        return await self._request(link)

    def to_string(self, data: dict, last_games: dict, online: dict) -> str:
        nick = data["player"]["displayname"]
        data = data["player"]["stats"]
        last_game = last_games["games"][-1]
        return f"""{nick} {"🟢" if online["session"]["online"] else "🔴"}

🛌 Bedwars:
    Coins: {data["Bedwars"]["coins"]}
    Win Streak: {data["Bedwars"]["winstreak"]}
    Games: {data["Bedwars"]["wins_bedwars"]} wins, {data["Bedwars"]["losses_bedwars"]} losses

🏝 Skywars:
    Coins: {data["SkyWars"]["coins"]}
    Win Streak: {data["SkyWars"]["win_streak"]}
    Games: {data["SkyWars"]["wins"]} wins, {data["SkyWars"]["losses"]} losses
    Kills: {data["SkyWars"]["kills"]}

🔪 Murder Mystery:
    Coins: {data["MurderMystery"]["coins"]}
    Games: {data["MurderMystery"]["wins"]} wins in {data["MurderMystery"]["games"]} games
    Kills: {data["MurderMystery"]["kills"]}

👷 Build Battle:
    Wins: {data["BuildBattle"]["wins"]}
    Coins: {data["BuildBattle"]["coins"]}

⚔️ Duels:
    Wins: {data["Duels"]["wins"]} wins, {data["Duels"]["losses"]} losses
    Kills: {data["Duels"]["kills"]}
    Coins: {data["Duels"]["coins"]}

📄 Last game: {last_game['gameType']}
"""


@loader.tds
class HypixelMod(loader.Module):
    """
    Module for getting information about minecraft Hypixel player
    """

    strings = {
        "name": "Hypixel",
        "template": '<pre><code class="language-output">{}</code></pre>',
        "not_token": "Token not found in config!",
        "_cfg_token": "Yandex.Music account token",
        "_cfg_uuid": "Minecraft UUID",
        "_cfg_nickname": "Minecraft nickname",
        "guide": (
            "Получите токен и запишите в .config по "
            '<a href="https://developer.hypixel.net/dashboard">ссылке</a>!'
        ),
    }

    strings_ru = {
        "not_token": "Токен не найден в конфиге!",
        "_cfg_token": "Токен аккаунта Яндекс.Музыка",
        "_cfg_uuid": "Майнкрафт UUID",
        "_cfg_nickname": "Никнейм в игре",
        "guide": (
            "Get a token and write it in .config by "
            '<a href="https://developer.hypixel.net/dashboard">link</a>!'
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "HypixelToken",
                None,
                self.strings["_cfg_token"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "UUID",
                None,
                self.strings["_cfg_uuid"],
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "nickname",
                "Pain_4986",
                self.strings["_cfg_nickname"],
                validator=loader.validators.String(),
            ),
        )

    async def on_dlmod(self):
        if not self.get("guide_send", False):
            await self.inline.bot.send_message(
                self._tg_id,
                self.strings["guide"],
            )
            self.set("guide_send", True)

    async def client_ready(self, client: TelegramClient, db):
        self.client = client
        self.db = db

    @loader.command()
    async def statcmd(self, message: Message):
        """Get stats about Hypixel player"""

        token = self.config["HypixelToken"]
        if not token:
            return await utils.answer(message, self.strings["not_token"])

        hypixel = HypixelAPI(token)

        uuid = self.config["UUID"]

        if not self.config["UUID"]:
            uuid = (await hypixel.get_uuid(self.config["nickname"]))["id"]
            self.config["UUID"] = uuid

        try:
            data = await hypixel.get_player_data(uuid)
            last_games = await hypixel.recent_games(uuid)
            online = await hypixel.player_status(uuid)
        except Exception as e:
            return await utils.answer(message, str(e))

        answer = hypixel.to_string(data, last_games, online)
        return await utils.answer(message, self.strings["template"].format(answer))
