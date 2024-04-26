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
# meta pic: https://img.icons8.com/external-filled-outline-wichaiwi/344/external-page-uxui-design-filled-outline-wichaiwi.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/external-filled-outline-wichaiwi/344/external-page-uxui-design-filled-outline-wichaiwi.png&title=BioPage&description=Module%20for%20create%20bio%20page

__version__ = (2, 0, 0)

import logging
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class BioPageMod(loader.Module):
    """Module for create bio page"""

    strings = {
        "name": "Bio Page",
        "answer": (
            '📦 The configuration of the <b>BioPage</b> is set to <code>"{0}"</code>'
        ),
        "error": "❗️ Error, check logs!",
    }

    strings_ru = {
        "answer": '📦 Конфигурация <b>BioPage</b> установлена <code>"{0}"</code>',
        "error": "❗️ Ошибка, проверьте логи!",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "toggle",
                "off",
                "Toggle bio page on/off",
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "bio_url",
                "https://vsecoder.github.io/tg-web-app/",
                "Bio page url (restart required to apply)",
                validator=loader.validators.Link(),
            ),
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._db = db
        self._client = client
        self.botfather = "@BotFather"

    async def bot_conifg(self):
        if self.config["toggle"]:
            async with self._client.conversation(self.botfather) as conv:
                await conv.send_message("/setmenubutton")
                await conv.mark_read()
                await conv.send_message(f"@{self.inline.bot_username}")
                await conv.mark_read()
                await conv.send_message(self.config["bio_url"])
                await conv.mark_read()
                await conv.send_message("🔗 Bio")
                await conv.mark_read()
        else:
            async with self._client.conversation(self.botfather) as conv:
                await conv.send_message("/setmenubutton")
                await conv.mark_read()
                await conv.send_message(f"@{self.inline.bot_username}")
                await conv.mark_read()
                await conv.send_message("/empty")
                await conv.mark_read()

    @loader.unrestricted
    @loader.ratelimit
    async def biotogglecmd(self, message):
        """
         - toggle bio page(default: off)
        Based on... my code)
        """
        self.config["toggle"] = not self.config["toggle"]
        await self.bot_conifg()
        await utils.answer(
            message,
            self.strings["answer"].format("on" if self.config["toggle"] else "off"),
        )
