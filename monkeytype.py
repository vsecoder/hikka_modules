"""
                              _
__   _____  ___  ___ ___   __| | ___ _ __
\ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
 \ V /\__ \  __/ (_| (_) | (_| |  __/ |
  \_/ |___/\___|\___\___/ \__,_|\___|_|

  Copyleft 2022 t.me/vsecoder
  This program is free software; you can redistribute it and/or modify

  Thk @hikariatama
"""
# meta developer: @vsecoder_m
# meta desc: Module for getting information about monkeytype.com stats
# meta pic: https://img.icons8.com/stickers/100/keyboard.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/stickers/100/keyboard.png&title=MonkeyType&description=Module%20for%20getting%20information%20about%20monkeytype.com%20stats

__version__ = (1, 0, 1)

import logging
import aiohttp

from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class MonkeyTypeMod(loader.Module):
    """
    Module for getting information about monkeytype.com stats

    {15/30/60/120:times} - dividing tests by time (default: 15)
    Need only account username (not full link)!
    """

    strings = {
        "name": "MonkeyType",
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Error: \n{}",
        "loading": "<emoji document_id=5451732530048802485>⏳</emoji> Loading...",
        "template_message": (
            "<blockquote><emoji document_id=5879770735999717115>👤</emoji> <b>MonkeyType.com stats for {}:</b></blockquote>\n\n"
            "<emoji document_id=5877485980901971030>📊</emoji> Completed tests: <code>{}</code>\n"
            "<emoji document_id=5778202206922608769>🔄</emoji> All time typing: <code>{}s</code>\n\n"
            "<emoji document_id=5870684638195748414>🏆</emoji> <b>Personal bests:</b>\n"
            "{}"
            "<emoji document_id=5994378914636500516>📈</emoji> <b>XP</b>: <code>{}</code>"
        ),
        "time": "  <emoji document_id=5960751816084820359>⏲️</emoji> <i>{}s</i>: \n",
        "not_time": "  <emoji document_id=5960751816084820359>⏲️</emoji> <i>{}s</i>: -\n\n",
        "template_time": (
            "  <emoji document_id=5100434699503797219>🟠</emoji><code>{}</code>:\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> {}: <code>{}</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Accuracy: <code>{}%</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Consistency: <code>{}%</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Difficulty: <code>{}</code>\n\n"
        ),
    }

    strings_ru = {
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Ошибка: \n{}",
        "loading": "<emoji document_id=5451732530048802485>⏳</emoji> Загрузка...",
        "template_message": (
            "<blockquote><emoji document_id=5879770735999717115>👤</emoji> <b>Статистика MonkeyType.com для {}:</b></blockquote>\n\n"
            "<emoji document_id=5877485980901971030>📊</emoji> Пройденных тестов: <code>{}</code>\n"
            "<emoji document_id=5778202206922608769>🔄</emoji> Всего времени печати: <code>{}s</code>\n\n"
            "<emoji document_id=5870684638195748414>🏆</emoji> <b>Лучшие результаты:</b>\n"
            "{}"
            "<emoji document_id=5994378914636500516>📈</emoji> <b>XP</b>: <code>{}</code>"
        ),
        "time": "  <emoji document_id=5960751816084820359>⏲️</emoji> <i>{}s</i>: \n",
        "not_time": "  <emoji document_id=5960751816084820359>⏲️</emoji> <i>{}s</i>: -\n\n",
        "template_time": (
            "  <emoji document_id=5100434699503797219>🟠</emoji><code>{}</code>:\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> {}: <code>{}</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Точность: <code>{}%</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Согласованность: <code>{}%</code>\n"
            "    <emoji document_id=5098279308821005089>🔵</emoji> Сложность: <code>{}</code>\n\n"
        ),
    }

    def __init__(self):
        self.name = self.strings["name"]

        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_typing_speed",
                "wpm",
                "Which typing speed to use by default",
                validator=loader.validators.Choice(["cps", "wpm", "cpm", "wps"]),
            ),
        )

    async def request(self, username=""):
        url = "https://api.monkeytype.com/users/{}/profile"

        async with aiohttp.ClientSession() as session:
            async with session.get(url.format(username)) as response:
                if response.status != [500, 503]:
                    return await response.json()

                return {"message": "Server error"}

    async def client_ready(self, client, db):
        self._client = client

    @loader.command(alias="mts")
    async def monkeytypestatscmd(self, message):
        """
        {username} {15/30/60/120:times} - get monkeytype.com user stats
        """
        args = utils.get_args_raw(message).split(" ")

        if not args:
            return await utils.answer(
                message, self.strings["error"].format("Invalid args")
            )

        time = args[1] if len(args) > 1 else "15"

        await utils.answer(message, self.strings["loading"])

        data = await self.request(args[0])

        if data["message"] != "Profile retrieved":
            return await utils.answer(
                message, self.strings["error"].format(data["message"])
            )

        data = data["data"]

        best = ""

        if time in data["personalBests"]["time"]:
            best += self.strings["time"].format(time)
            for i in data["personalBests"]["time"][time]:
                typing_speeds = {
                    "wpm": 1,
                    "cpm": 5,
                    "wps": 1 / 60,
                    "cps": 5 / 60,
                }
                speed = round(
                    i["wpm"] * typing_speeds[self.config["default_typing_speed"]], 2
                )
                best += self.strings["template_time"].format(
                    i["language"],
                    self.config["default_typing_speed"].upper(),
                    speed,
                    i["acc"],
                    i["consistency"],
                    i["difficulty"],
                )
        else:
            best += self.strings["not_time"].format(time)

        answer = self.strings["template_message"].format(
            args[0],
            data["typingStats"]["completedTests"],
            round(data["typingStats"]["timeTyping"]),
            best,
            data["xp"],
        )

        return await utils.answer(message, answer)
