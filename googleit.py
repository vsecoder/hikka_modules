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
# meta pic: https://img.icons8.com/bubbles/344/google-logo.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/bubbles/344/google-logo.png&title=GoogleIT&description=Google%20search%20module%20for%20userbot

__version__ = (2, 0, 0)

import logging
import asyncio
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class GoogleItMod(loader.Module):
    """Module for google search"""

    strings = {
        "name": "Google it",
        "cfg_searc_url": "Searcher",
        "answer": "😒 I advise you to look in the search engine first: ",
        "error": "Error!\n .googleit | text",
    }

    strings_ru = {
        "cfg_searc_url": "Поисковик",
        "answer": "😒 Советую для начала заглянуть в поисковик: ",
        "error": "Ошибка!\n \n .googleit | text",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "search_url",
            "https://www.google.com/search?q={query}",
            self.strings["cfg_searc_url"],
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._client = client

    @loader.unrestricted
    @loader.ratelimit
    async def googleitcmd(self, message):
        """
        {text} - text to search
        """
        args = message.text.replace(f"{self.get_prefix()}googleit ", "")
        if args:
            url = self.config["search_url"].format(query=args).replace(" ", "+")
            await utils.answer(message, f'{self.strings["answer"]}{url}')
        else:
            await utils.answer(message, self.strings["error"])
            await asyncio.sleep(5)
            await message.delete()
