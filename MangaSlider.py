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
# meta pic: https://img.icons8.com/color/256/kakashi-hatake.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/color/256/kakashi-hatake.png&title=MangaSlider&description=Read%20manga%20in%20Telegram%20%F0%9F%91%8D

__version__ = (2, 0, 1)

import logging
from aiogram.types import Message as AiogramMessage
from .. import loader  # type: ignore
from ..inline.types import InlineCall  # type: ignore
import requests

logger = logging.getLogger(__name__)


@loader.tds
class MangaSliderMod(loader.Module):
    strings = {"name": "MangaSlider"}

    async def client_ready(self, client, db):
        self.client = client
        self.__doc__ = (
            "Модуль для чтения манги 👨‍💻[beta]\n\n🔗 Ссылка:"
            f" t.me/{self.inline.bot_username}?start=manga\n\n"
            "В будущем ожидается или перенос в бота, "
            "или добавление полноценного функционала."
        )

    async def requests(self, data):
        _api = "https://api.newmanga.org/"
        _storage = "https://storage.newmanga.org/"

        _all_chapters = _api + "v3/branches/{}/chapters/all"  # paste manga id
        _all_pages = _api + "v3/chapters/{}/pages"  # paste chapter id

        _image = (
            _storage + "origin_proxy/{}/{}/{}"
        )  # paste disk name, chapter id and file name

        chapters = requests.get(_all_chapters.format(data["name"])).json()
        charapter = chapters[data["chapter"]]
        charapter_id = charapter["id"]
        disk = charapter["origin"]
        tom = charapter["tom"]
        pages_count = charapter["pages"]

        if data["page"] > pages_count:
            return {"error": "❗️ Это последняя страница"}

        pages = requests.get(_all_pages.format(charapter_id)).json()
        page = pages["pages"][data["page"]]["slices"][0]["path"]

        return {
            "image": _image.format(disk, charapter_id, page),
            "page": f"{data['page'] + 1}/{pages_count}",
            "chapter": f"{data['chapter'] + 1}/{len(chapters)}",
            "tom": tom,
            "error": None,
        }

    async def _markup(self, data):
        return self.inline.generate_markup(
            [
                [
                    {
                        "text": "◀️",
                        "data": f"manga/undo/{data['name']}/{data['page']}/{data['chapter']}",
                    },
                    {
                        "text": "▶️",
                        "data": f"manga/next/{data['name']}/{data['page']}/{data['chapter']}",
                    },
                ],
                [
                    {
                        "text": "▶️ Следующая глава",
                        "data": f"manga/next_chapter/{data['name']}/{data['page']}/{data['chapter']}",
                    }
                ],
            ]
        )

    async def aiogram_watcher(self, message: AiogramMessage):
        if self._client._tg_id == message.chat.id and message.text:
            if message.text == "/start manga":
                await self.inline.bot.send_message(
                    self._tg_id,
                    """
👨‍💻 <b>Привет, чтобы продолжить введи <code>/read</code> с параметром - номером манги, который можно получить с сайта https://newmanga.org, пример:</b>

 ▪️ Клинок, рассекающий демонов - https://newmanga.org/p/blade-of-demon-destruction/<code>4774</code>/r/85016
 Для чтения манги введите команду <code>/read 4774</code> что бы начать с первой главы
""",
                )
            elif message.text.split(" ")[0] == "/read":
                args = message.text.split(" ")
                if len(args) != 2:
                    return await self.inline.bot.send_message(
                        self._tg_id, "❗️ Неправильно указан агрумент"
                    )

                page = 0
                data = {"name": args[1], "page": page, "chapter": 0}

                _markup = await self._markup(data)

                r = await self.requests(data)
                await self.inline.bot.send_photo(
                    self._tg_id,
                    r["image"],
                    r["page"],
                    reply_markup=_markup,
                )

    async def feedback_callback_handler(self, call: InlineCall):
        if not call.data.startswith("manga"):
            return

        args = call.data.replace("manga/", "").split("/")

        data = {
            "name": args[1],
            "page": int(args[2]),
            "chapter": int(args[3]),
        }

        if args[0] == "undo":
            if data["page"] == 0:
                return await self.inline.bot.answer_callback_query(
                    call.id, "❗️ Это первая страница"
                )
            data["page"] -= 1
        elif args[0] == "next":
            data["page"] += 1
        elif args[0] == "next_chapter":
            data["page"] = 0
            data["chapter"] += 1

        _markup = await self._markup(data)

        r = await self.requests(data)

        if r["error"]:
            return await self.inline.bot.answer_callback_query(call.id, r["error"])

        text = f"<b>📚 Том</b>: {r['tom']}\n<b>📙 Глава:</b> {r['chapter']}\n<b>📄 Страница:</b> {r['page']}"

        await self.inline.bot.send_photo(
            self._tg_id, r["image"], text, reply_markup=_markup
        )
        await self.inline.bot.delete_message(self._tg_id, call.message.message_id)
