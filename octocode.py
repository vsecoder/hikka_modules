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
# meta pic: https://img.icons8.com/cotton/344/code.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/cotton/344/code.png&title=OctoCode&description=OctoCode%20is%20a%20module%20for%20octopussed%20code%20in%20Telegram

__version__ = (3, 0, 0)

import logging
import asyncio
from .. import loader, utils  # type: ignore


logger = logging.getLogger(__name__)


@loader.tds
class OctoCodeMod(loader.Module):
    """
    Module for octopussed code

    https://github.com/charmbracelet/freeze based

    To use, run this in .terminal:

    wget https://github.com/charmbracelet/freeze/releases/download/v0.1.6/freeze_0.1.6_amd64.deb
    sudo dpkg -i freeze_0.1.6_amd64.deb

    """

    strings = {
        "name": "OctoCode",
        "answer": "🐙 <b>Code</b> <i>octopussed</i>: ",
        "loading": "🐙 <b>Loading</b>...",
        "cfg_theme": "🦎 Change theme",
        "cfg_line_numbers": "🦎 Type True/False to manage a number of line numbers",
        "cfg_default_lang": "🦎 Enter the programming language to use by default",
        "error": "❗️ Error: {0}",
    }

    strings_ru = {
        "answer": "🐙 <b>Код</b> <i>осьмоножен</i>: ",
        "loading": "🐙 <b>Загрузка</b>...",
        "cfg_theme": "🦎 Выбери тему",
        "cfg_line_numbers": "🦎 Введите True/False для управления ряда номеров строк",
        "cfg_default_lang": (
            "🦎 Введите язык программирования для использования по умолчанию"
        ),
        "error": "❗️ Ошибка: {0}",
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "theme",
                "monokai",
                self.strings["cfg_theme"],
                validator=loader.validators.Choice(
                    ["charm", "dracula", "github-dark", "monokai", "nord", "onedark"]
                ),
            ),
        )
        self.name = self.strings["name"]

    async def get_code(self, message):
        reply = await message.get_reply_message()

        if message.media:
            await self._client.download_file(message.media, "file.txt")
            return "file.txt"

        if reply:
            if reply.media:
                await self._client.download_file(reply.media, "file.txt")
                return "file.txt"

        return

    @loader.unrestricted
    @loader.ratelimit
    async def octocmd(self, message):
        """
         "reply file" or "send file"
        Octopussed your code
        """
        await utils.answer(message, self.strings["loading"])

        path = await self.get_code(message)

        if not path:
            return await utils.answer(
                message, self.strings["error"].format("not file changed")
            )

        try:
            process = await asyncio.create_subprocess_exec(
                "freeze",
                path,
                "-t",
                self.config["theme"],
                "-l",
                "py",
            )
            await process.wait()
        except Exception as e:
            logger.exception(e)
            await utils.answer(message, self.strings["error"].format(e))
            return

        await self._client.send_file(
            utils.get_chat_id(message),
            file=open("freeze.png", "rb"),
            reply_to=getattr(message, "reply_to_msg_id", None),
        )

        await utils.answer(message, self.strings["answer"])
