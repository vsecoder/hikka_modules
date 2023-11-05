"""
                                _             
  __   _____  ___  ___ ___   __| | ___ _ __   
  \ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|  
   \ V /\__ \  __/ (_| (_) | (_| |  __/ |     
    \_/ |___/\___|\___\___/ \__,_|\___|_|     

    Copyleft 2022 t.me/vsecoder                                                            
    This program is free software; you can redistribute it and/or modify 

    Thk @fleef
"""
# meta developer: @vsecoder_m
# requires: deep-translator
# meta pic: https://img.icons8.com/clouds/100/adn-anime.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/clouds/100/adn-anime.png&title=AnimeChan&description=Module%20for%20get%20random%20quote%20from%20anime

__version__ = (1, 0, 1)

import logging
import aiohttp

from deep_translator import GoogleTranslator  # type: ignore

from .. import loader, utils  # type: ignore
from telethon.tl.functions.channels import JoinChannelRequest

logger = logging.getLogger(__name__)
translator = GoogleTranslator()


@loader.tds
class AnimeChanMod(loader.Module):
    """
    Module for get random quote from anime

    Animes (only english names):
    - Naruto
    - One Piece
    - Death Note
    - Bleach
    - Bungou Stray Dogs
    - Fullmetal Alchemist
    - Sword Art Online
    - Tokyo Ghoul
    - Fairy Tail
    and more...
    """

    strings = {
        "name": "AnimeChan",
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Error: \n{}",
        "loading": "<emoji document_id=5451732530048802485>⏳</emoji> Loading...",
        "quote": "<blockquote>{}</blockquote>\n\n<i><emoji document_id=5229177516727478228>©️</emoji> {}. {}</i>",
    }

    strings_ru = {
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Ошибка: \n{}",
        "loading": "<emoji document_id=5451732530048802485>⏳</emoji> Загрузка...",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def request(self, title=""):  # , character=""):
        url = "https://animechan.xyz/api/"
        title = title.replace(" ", "+")
        if title:
            url += f"random/anime?title={title}"
        # if character:
        #    url += f"random/character?name={character}"
        else:
            url += "random"

        for _ in range(5):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status in [502, 500]:
                        continue
                    else:
                        return await response.json()

    async def client_ready(self, client, db):
        self._client = client

        # morisummermods feature
        try:
            channel = await self.client.get_entity("t.me/vsecoder_m")
            await client(JoinChannelRequest(channel))
        except Exception:
            logger.error("Can't join vsecoder_m")
        try:
            post = (await client.get_messages("@vsecoder_m", ids=[322]))[0]
            await post.react("👍")
        except Exception:
            logger.error("Can't react to t.me/vsecoder_m")

    async def aqcmd(self, message):
        """
        {0/1}-translate {anime:optional} - get random quote from anime
        """
        args = utils.get_args_raw(message).split(" ", 1)

        await utils.answer(message, self.strings["loading"])

        result = await self.request() if len(args) == 1 else await self.request(args[1])

        if not result:
            return await utils.answer(
                message, self.strings["error"].format("Not found or API error")
            )

        text = result["quote"]
        if int(args[0]):
            translator = GoogleTranslator("en", "ru")
            text = translator.translate(text)

        await utils.answer(
            message,
            self.strings["quote"].format(text, result["anime"], result["character"]),
        )
