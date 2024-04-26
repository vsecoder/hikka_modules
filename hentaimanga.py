# █▀ █░█ ▄▀█ █▀▄ █▀█ █░█░█
# ▄█ █▀█ █▀█ █▄▀ █▄█ ▀▄▀▄▀

# Copyright 2023 t.me/shadow_modules
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# meta developer: @shadow_modules, @toxicuse, @vsecoder
# meta banner: https://i.imgur.com/8UYznku.jpeg

from .. import loader, utils  # type: ignore
from telethon.tl.types import Message  # type: ignore
from ..inline.types import InlineCall  # type: ignore
import requests


async def request(url: str = "https://janda.sinkaroid.org/3hentai/random") -> dict:
    """Manga handler"""
    return (await utils.run_sync(requests.get, url)).json()["data"]


@loader.tds
class HentaiMangaMod(loader.Module):
    strings = {
        "name": "HentaiManga",
        "message": "<b>Title:</b> <code>{title}</code>\n<b>Pages:</b> {total}\n<b>Tags:</b> {tags}\n\n"
        "Command to get this manga: <code>.ghm {api} {id}</code>",
        "time": "<b>Wait...</b>",
        "warn-form": (
            "<b>⚠️ Attention!</b>\n<b>😰 This module is 18+\n"
            "✉️ In many chats it is prohibited</b>\n<b>✅ If you agree with what you can get"
            "ban - click on the button below</b>"
        ),
        "yes": "✅ Yes",
        "no": "❌ No",
        "args_error": "<b>Not enough arguments</b>",
        "not_found": "<b>Not found</b>",
    }
    strings_ru = {
        "message": "<b>Название:</b> <code>{title}</code>\n<b>Страниц:</b> {total}\n<b>Теги:</b> {tags}\n\n"
        "Команда для получения этой манги: <code>.ghm {api} {id}</code>",
        "time": "<b>Ожидайте...</b>",
        "warn-form": (
            "<b>⚠️ Внимание!</b>\n<b>😰 Данный модуль 18+\n"
            "✉️ Во многих чатах он запрещен</b>\n<b>✅ Если вы согласны с тем что можете получить"
            " бан - нажмите на кнопку ниже</b>"
        ),
        "yes": "✅ Да",
        "no": "❌ Нет",
        "args_error": "<b>Недостаточно аргументов</b>",
        "not_found": "<b>Не найдено</b>",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, _):
        self.apis = {
            "3hentai": {
                "random": "https://janda.sinkaroid.org/3hentai/random",
                "get": "https://janda.sinkaroid.org/3hentai/get?book={id}",
            },
            "asmhentai": {
                "random": "https://janda.sinkaroid.org/asmhentai/random",
                "get": "https://janda.sinkaroid.org/asmhentai/get?book={id}",
            },
            "hentaifox": {
                "random": "https://janda.sinkaroid.org/hentaifox/random",
                "get": "https://janda.sinkaroid.org/hentaifox/get?book={id}",
            },
        }

    async def gallery(self, message: Message, mang: dict, api: str = "3hentai"):
        await self.inline.gallery(
            caption=self.strings["message"].format(
                title=mang["title"].replace("[", "").replace("]", ""),
                total=mang["total"],
                tags=", ".join(mang["tags"]),
                api=api,
                id=mang["id"],
            ),
            message=message,
            next_handler=mang["image"],
        )

    async def warn(self, message: Message):
        await self.inline.form(
            message=message,
            text=self.strings["warn-form"],
            reply_markup=[
                [
                    {
                        "text": self.strings["yes"],
                        "callback": self.inline_call_answer,
                    },
                ],
                [
                    {
                        "text": self.strings["no"],
                        "callback": self.delete_module,
                        "args": (message,),
                    },
                ],
            ],
        )

    @loader.command(alias="rhm")
    async def rnd_hentai_mangacmd(self, message: Message):
        """
        {hentai_api_name: optional} - рандомная хентай-манга
        """

        args = utils.get_args_raw(message).split(" ")

        if not self.db.get(__name__, "warn", False):
            await self.warn(message)
            return

        await utils.answer(message, self.strings["time"])

        api = args[0] if args and args[0] in self.apis else "3hentai"

        mang = await request(self.apis[api]["random"])

        await self.gallery(message, mang, api)

    @loader.command(alias="ghm")
    async def get_hentai_mangacmd(self, message: Message):
        """
        {hentai_api_name} {id} - получить хентай-мангу
        """

        args = utils.get_args_raw(message).split(" ")

        if len(args) < 2:
            return await utils.answer(message, self.strings["args_error"])

        if not self.db.get(__name__, "warn", False):
            await self.warn(message)
            return

        await utils.answer(message, self.strings["time"])

        if args[0] not in self.apis:
            return await utils.answer(message, self.strings["args_error"])

        mang = await request(self.apis[args[0]]["get"].format(id=args[1]))

        if not mang:
            return await utils.answer(message, self.strings["not_found"])

        await self.gallery(message, mang, args[0])

    async def inline_call_answer(self, call: InlineCall):
        self.db.set(__name__, "warn", True)
        await call.delete()

    @loader.owner
    async def delete_module(self, call: InlineCall, message):
        await call.delete()
        await self.invoke("unloadmod", "HentaiManga", message.peer_id)
