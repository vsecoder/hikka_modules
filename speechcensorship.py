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
# requires: git+https://github.com/vsecoder/py-censure

__version__ = (2, 0, 0)

import logging
from .. import loader, utils  # type: ignore
from censure import Censor

logger = logging.getLogger(__name__)


@loader.tds
class SpeechCensorshipMod(loader.Module):
    """Module for censoring your speech"""

    strings = {
        "name": "SpeechCensorship",
        "_cfg_replace_symbols": "Replace symbols for censoring",
        "_cfg_language": "Language",
        "turn": "<emoji document_id=5235698355119596341>😆</emoji> <b>Censorship mode {}</b>",
    }

    strings_ru = {
        "_cfg_replace_symbols": "Символы для замены мата",
        "_cfg_language": "Язык",
        "turn": "<emoji document_id=5235698355119596341>😆</emoji> <b>Режим цензуры {}</b>",
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.get("censorship_work", False)
        self.me = await client.get_me()

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "replace_symbols",
                "#",
                lambda m: self.strings["_cfg_replace_symbols"],
            ),
            loader.ConfigValue(
                "language",
                ["ru", "en"],
                lambda m: self.strings["_cfg_language"],
                validator=loader.validators.MultiChoice(["ru", "en"]),
            ),
        )
        self.name = self.strings["name"]

    async def censorshipcmd(self, message):
        """
        Turn on/off censorship mode
        """
        censorship_work = self.get("censorship_work", False)

        work = "on" if not censorship_work else "off"
        self.set("censorship_work", not censorship_work)

        await utils.answer(message, self.strings["turn"].format(work))

    async def censor_task(self, text):
        languages = self.config["language"]
        replace_symbols = self.config["replace_symbols"]

        censors = [Censor.get(lang) for lang in languages]

        for censor in censors:
            text = censor.clean_line(text, beep=replace_symbols)[0]

        return text

    async def watcher(self, message):
        try:
            if self.me.id != message.from_id:
                return

            censorship_work = self.get("censorship_work", False)

            if not censorship_work:
                return

            text = message.text

            if text:
                censored = await self.censor_task(text)

                if text != censored:
                    await message.edit(censored)
        except:
            return
