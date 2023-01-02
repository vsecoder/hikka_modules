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
# meta pic: https://img.icons8.com/external-flaticons-lineal-color-flat-icons/344/external-screen-edutainment-flaticons-lineal-color-flat-icons-2.png

__version__ = (2, 0, 0)

import logging
import asyncio
import requests
import io
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class GoogleItMod(loader.Module):
    """Module for screenshot web site"""

    strings = {
        "name": "ScreenWeb",
        "answer": "🖥 Screenshot {0} {1}x{2}px:",
        "error": "Error!\n \n .screenweb <url>=str <width>=int <height>=int",
        "cfg_url": "Url to API"
    }

    strings_ru = {
        "answer": "🖥 Скриншот {0} {1}x{2}px:",
        "error": "Ошибка!\n \n .screenweb <url>=строка <width>=число <height>=число",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "url",
            "https://webshot.deam.io/{0}/?width={1}&height={2}?type=png&no_cookie_banners=true&lazy_load=true&destroy_screenshot=true&dark_mode=true&wait_for_event=load&delay=1000&accept_languages=ru&ttl=10",
            self.strings["cfg_url"],
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.unrestricted
    @loader.ratelimit
    async def screenwebcmd(self, message):
        """
         <url>=str <width>=int <height>=int
        .screenweb https://google.com/
        .screenweb https://vsecoder.ml/ 1920 1080
        """
        args = utils.get_args(message)
        if not args:
            await utils.answer(message, self.strings["error"])
            return

        try:
            width = args[2]
            height = args[3]
        except Exception:
            width = 1920
            height = 1080

        url = self.config["url"].format(args[0], width, height)
        photo = await utils.run_sync(requests.get, url)

        if not photo.ok:
            await utils.answer(message, "<b>Что-то пошло не так..</b>")
            return

        photo = io.BytesIO(photo.content)
        photo.name = "screen.png"
        photo.seek(0)

        await utils.answer(
            message, self.strings["answer"].format(args[0], width, height)
        )
        await self.client.send_file(message.peer_id, photo)
