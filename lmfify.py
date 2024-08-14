"""
                              _
__   _____  ___  ___ ___   __| | ___ _ __
\ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
 \ V /\__ \  __/ (_| (_) | (_| |  __/ |
  \_/ |___/\___|\___\___/ \__,_|\___|_|

  Copyleft 2024 t.me/vsecoder
  This program is free software; you can redistribute it and/or modify

"""
# meta developer: @vsecoder_m
# meta pic: https://img.icons8.com/bubbles/344/google-logo.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/bubbles/344/google-logo.png&title=LMFIFY&description=Let%20me%20find%20it%20for%20you%20in%20Google%20/%20Yandex

__version__ = (2, 0, 0)

import logging
import asyncio
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class LMFIFYMod(loader.Module):
    """Let me find it for you in Google / Yandex"""

    strings = {
        "name": "LMFIFY",
        "cfg_searc_engine": "Searcher, http://yaforyou.ru/?= or https://track24.ru/google/?q=",
        "answer": "<b><emoji document_id=5276167890624585747>👩‍💻</emoji> Let me find it for you: </b><a href='{}'>👉click</a>",
        "error": "Need text!",
    }

    strings_ru = {
        "cfg_searc_url": "Поисковик, http://yaforyou.ru/?= или https://track24.ru/google/?q=",
        "answer": "<b><emoji document_id=5276167890624585747>👩‍💻</emoji> Дай-ка я найду: </b><a href='{}'>👉click</a>",
        "error": "Нужен текст!",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "search_url",
            "https://track24.ru/google/?q={query}",
            self.strings["cfg_searc_engine"],
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._client = client

    @loader.unrestricted
    @loader.ratelimit
    async def finditcmd(self, message):
        """
        {text} - find it in search engine
        """
        args = utils.get_args_raw(message)
        if args:
            url = self.config["search_url"].format(query=args).replace(" ", "+")
            await utils.answer(message, self.strings["answer"].format(url))
        else:
            await utils.answer(message, self.strings["error"])
            await asyncio.sleep(5)
            await message.delete()
