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
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/external-flaticons-lineal-color-flat-icons/344/external-roulette-casino-flaticons-lineal-color-flat-icons-3.png&title=Russian%20roulette&description=Telegram%20Russian%20roulette%20game

__version__ = (2, 3, 2)

import logging
import asyncio
import random
from .. import loader, utils  # type: ignore
from telethon import functions

logger = logging.getLogger(__name__)


@loader.tds
class RussianRouletteMod(loader.Module):
    """Module for "Russian roulette" game"""

    strings = {
        "name": "Russian roulette",
        "cfg_lingva_url": (
            "1/8 chance of destroying the account, are you taking a chance or are you"
            " afraid?)"
        ),
        "answer": "😒 You're lucky, but only now...",
        "answer2": "😏 * the sound of a gunshot *",
        "answer3": "🤨 Were you seriously expecting account deletion?",
        "error": "😡 Ah, EMAE, the revolver broke...",
        "cfg_real": "If set to `True`, if you lose, your account will be deleted",
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
            loader.ConfigValue(
                "real",
                False,
                self.strings["cfg_real"],
                validator=loader.validators.Link(),
            )
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    @loader.unrestricted
    @loader.ratelimit
    async def revolvercmd(self, message):
        """
        - to start "Russian roulette"
        """
        try:
            roulette = [1]
            roulette.extend(0 for _ in range(7))
            result = random.choice(roulette)
            if result != 1:
                await utils.answer(message, self.strings["answer"])
            else:
                await utils.answer(message, self.strings["answer2"])
                await asyncio.sleep(3)
                await utils.answer(message, "gg")
                if self.config["real"]:
                    self.client(
                        functions.account.DeleteAccountRequest(
                            reason="Lose in Russian roulette"
                        )
                    )
        except Exception:
            await utils.answer(message, self.strings["error"])
