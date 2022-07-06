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
# meta pic: https://img.icons8.com/external-flaticons-lineal-color-flat-icons/344/external-roulette-casino-flaticons-lineal-color-flat-icons-3.png

__version__ = (2, 3, 2)

import logging
import asyncio
import random
from .. import loader, utils
from telethon import functions

logger = logging.getLogger(__name__)


@loader.tds
class RussianRouletteMod(loader.Module):
    """Module for "Russian roulette" game"""

    strings = {
        "name": "Russian roulette",
        "cfg_lingva_url": "1/8 chance of destroying the account, are you taking a chance or are you afraid?)",
        "answer": "😒 You're lucky, but only now...",
        "answer2": "😏 * the sound of a gunshot *",
        "answer3": "🤨 Were you seriously expecting account deletion?",
        "error": "😡 Ah, EMAE, the revolver broke...",
    }

    strings_ru = {
        "cfg_lingva_url": "Шанс 1/8 на уничтожение аккаунта, рискнешь или боишься?)",
        "answer": "😒 Тебе повезло, но только сейчас...",
        "answer2": "😏 * звук выстрела *",
        "answer3": "🤨 Ты серьёзно ожидал удаление аккаунта?",
        "error": "😡 Ах, ЁМАЁ, сломался то, револьвер...",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "real",
            "1",
            lambda m: self.strings("cfg_real", m),
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

        await self.save_stat("download")

    async def save_stat(self, state):
        bot = "@modules_stat_bot"
        m = await self._client.send_message(bot, f"/{state} russianroulette")
        await self._client.delete_messages(bot, m)

    async def on_unload(self):
        await self.save_stat("unload")

    @loader.unrestricted
    @loader.ratelimit
    async def revolvercmd(self, message):
        """
         - to start "Russian roulette"
        """
        try:
            roulette = []
            real = int(self.config["real"])
            roulette.append(1)
            for i in range(7):
                roulette.append(0)

            result = random.choice(roulette)
            if result != 1:
                await utils.answer(message, self.strings["answer"])
            else:
                await utils.answer(message, self.strings["answer2"])
                await asyncio.sleep(3)
                if real == '1':
                    await utils.answer(message, 'gg')
                    self.client(functions.account.DeleteAccountRequest(reason='Lose in Russian roulette'))
                else:
                    await utils.answer(message, self.strings["error"])
        except:
            await utils.answer(message, self.strings["error"])
