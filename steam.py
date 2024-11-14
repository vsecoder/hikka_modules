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
# meta pic: https://img.icons8.com/3d-fluency/94/steam.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/3d-fluency/94/steam.png&title=Steam&description=Module%20for%20get%20Steam%20account%20information

__version__ = (1, 0, 0)

import logging
import aiohttp
from datetime import datetime
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


def minutes_to_hours(minutes: int) -> str:
    hours, minutes = divmod(minutes, 60)
    return f'{hours}h {minutes}m'


def get_created_ago(timestamp: int) -> str:
    created_at = datetime.fromtimestamp(timestamp)
    now = datetime.now()
    ago = now - created_at

    return f"{ago.days // 365} years"


class SteamSDK:
    def __init__(self, apikey: str, steamid: str):
        self.apikey = apikey
        self.steamid = steamid

        self.api_url = "https://api.steampowered.com/{method}/"

        self.profile_method = "ISteamUser/GetPlayerSummaries/v0002"
        self.recent_games_method = "IPlayerService/GetRecentlyPlayedGames/v0001"
        self.owned_games_method = "IPlayerService/GetOwnedGames/v0001"

    async def _request(
        self,
        url: str,
        params: dict,
    ) -> dict:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request("GET", url, params=params) as response:
                    if response.status != 200:
                        return {"code": response.status, "detail": response.reason}
                    return await response.json()
            except aiohttp.ClientConnectorError:
                return {"detail": "Connection error", "code": 0}
            except Exception as e:
                return {"detail": f"Unknown error: {e}", "code": 0}

    async def get_profile(self) -> dict:
        url = self.api_url.format(method=self.profile_method)
        params = {"key": self.apikey, "steamids": self.steamid}
        return await self._request(url, params)

    async def get_recent_games(self) -> dict:
        url = self.api_url.format(method=self.recent_games_method)
        params = {"key": self.apikey, "steamid": self.steamid}
        return await self._request(url, params)

    async def get_owned_games(self) -> dict:
        url = self.api_url.format(method=self.owned_games_method)
        params = {"key": self.apikey, "steamid": self.steamid}
        return await self._request(url, params)


@loader.tds
class SteamMod(loader.Module):
    """
    Module for get Steam account information

    Later (TODO):
    - achivments list
    - {STEAM} widget
    """

    strings = {
        "name": "Steam",
        "profile": (
            '<a href="{avatar}"></a><emoji document_id=5328115953861408177>🎮</emoji> <b>{name}</b> <i>aka</i> '
            '<a href="https://steamcommunity.com/id/{username}/"><i>{username}</i></a> (created {created_ago} ago)\n'
            "<emoji document_id=5938413566624272793>🎮</emoji> Now {state}\n\n"
            "<emoji document_id=5879813604068298387>❗️</emoji> <b>More info:</b>\n"
            "   <emoji document_id=5274034223886389748>❤️</emoji><i>Level:</i> <code>{level}</code>\n"
            "   <emoji document_id=5274034223886389748>❤️</emoji><i>Total time spent:</i> <code>{time_spent}</code>\n"
            "   <emoji document_id=5274034223886389748>❤️</emoji><i>Owned games:</i> <code>{games_count}</code>\n\n"
            "<emoji document_id=5843799474362652262>🔄</emoji> <b>Recently played in:</b>\n"
            "{games}"
        ),
        "game": (
            '   <emoji document_id=5274034223886389748>❤️</emoji><a href="https://steamcommunity.com/app/{game_id}">'
            "<i>{game}</i></a> (<code>{time_spent}</code>)\n"
        ),
        "state_online": 'in "<i><a href="https://steamcommunity.com/app/{game_id}">{game}</a></i>"',
        "state_offline": "offline",
        "loading": "<emoji document_id=5323331656646407005>🎮</emoji> <b>Loading...</b>",
        "error_403": "<emoji document_id=5778527486270770928>❌</emoji> <b>Access denied, token is invalid or another error occurred</b>\nDEBUG INFO: <code>{error}</code>",
        "error_empty": "<emoji document_id=5778527486270770928>❌</emoji> <b>Empty API key or steamID64</b> (open <code> .config steam</code>)",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "apikey",
                "",
                "Get token from https://steamcommunity.com/dev/apikey",
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "steamid",
                "",
                "Get steamID64 from https://steamid.io/lookup/",
                validator=loader.validators.Hidden(),
            ),
        )

    async def client_ready(self, client, db):
        self._client = client
        self._db = db

    async def steamcmd(self, message):
        """
         - get steam profile
        """
        await utils.answer(message, self.strings["loading"])

        if not self.config["apikey"] or not self.config["steamid"]:
            return await utils.answer(message, self.strings["error_empty"])

        sdk = SteamSDK(self.config["apikey"], self.config["steamid"])

        profile = await sdk.get_profile()
        owned_games = await sdk.get_owned_games()
        recent_games = await sdk.get_recent_games()

        if "code" in profile:
            return await utils.answer(
                message, 
                self.strings["error_403"].format(error=str(profile))
            )

        profile = profile["response"]["players"][0]

        if "gameid" in profile:
            game_id = profile["gameid"]
            game = profile["gameextrainfo"]
            state = self.strings["state_online"].format(game=game, game_id=game_id)
        else:
            state = self.strings["state_offline"]

        games_count = owned_games["response"]["game_count"]
        created_ago = get_created_ago(profile["timecreated"])
        time_spent = sum(
            [game["playtime_forever"] for game in owned_games["response"]["games"]]
        )
        games = "".join(
            [
                self.strings["game"].format(
                    game=x["name"],
                    game_id=x["appid"],
                    time_spent=minutes_to_hours(x["playtime_forever"]),
                )
                for x in recent_games["response"]["games"]
            ]
        )

        await utils.answer(
            message,
            self.strings["profile"].format(
                avatar=profile["avatar"],
                name=profile["realname"] if "realname" in profile else "NoName",
                username=profile["personaname"],
                level=profile["communityvisibilitystate"],
                created_ago=created_ago,
                games_count=games_count,
                time_spent=minutes_to_hours(time_spent),
                state=state,
                games=games,
            ),
            link_preview=True,
        )
