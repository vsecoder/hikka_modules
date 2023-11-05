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
# meta pic: https://img.icons8.com/external-vitaliy-gorbachev-lineal-color-vitaly-gorbachev/344/external-translate-online-learning-vitaliy-gorbachev-lineal-color-vitaly-gorbachev.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/external-vitaliy-gorbachev-lineal-color-vitaly-gorbachev/344/external-translate-online-learning-vitaliy-gorbachev-lineal-color-vitaly-gorbachev.png&title=VsecoderTranlate&description=Telegram%20Translate%20Bot

__version__ = (2, 2, 1)

import logging
import translators as vt  # type: ignore
from .. import loader, utils  # type: ignore
from telethon.tl.functions.channels import JoinChannelRequest

logger = logging.getLogger(__name__)


@loader.tds
class VseTranslateMod(loader.Module):
    strings = {
        "name": "💠 Vsecoder Translate",
        "invalid_args": "📥 Invalid arguments!",
        "answer": (
            "💠 <b>{}</b> <i>from:</i><b>[{}]</b>"
            " <i>to:</i><b>[{}]</b>\n\n<code>{}</code>"
        ),
        "error": "📥 Error!",
    }

    strings_ru = {
        "invalid_args": "📥 Неправильные аргументы!",
        "answer": (
            "💠 <b>{}</b> <i>с:</i><b>[{}]</b> <i>на:</i><b>[{}]</b>\n\n<code>{}</code>"
        ),
        "error": "📥 Ошибка!",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "default_lang",
                "ru",
                "Which language to translate by default",
                validator=loader.validators.Choice(
                    ["ru", "en", "de", "fr", "es", "it", "pt", "ja", "zh", "ko"]
                ),
            ),
            loader.ConfigValue(
                "default_translator",
                "google",
                "Which translator to use by default",
                validator=loader.validators.Choice(
                    ["google", "yandex", "bing", "iciba"]
                ),
            ),
        )

    async def client_ready(self, client, _):
        self._client = client

        # morisummermods feature
        try:
            channel = await self.client.get_entity("t.me/vsecoder_m")
            await client(JoinChannelRequest(channel))
        except Exception:
            logger.error("Can't join vsecoder_m")

    async def translate(
        self,
        text: str,
        lang_from: str = "auto",
        lang_to: str = "ru",
        translator: str = "google",
    ) -> dict:
        translators = {
            "google": vt.google,
            "yandex": vt.yandex,
            "bing": vt.bing,
            "iciba": vt.iciba,
        }

        if translator not in translators:
            return {"error": self.strings["invalid_translator"]}

        translater = translators[translator]
        return {
            "translator": translator,
            "from": lang_from,
            "to": lang_to,
            "text": translater(text, from_language=lang_from, to_language=lang_to),
        }

    async def vsetranslatecmd(self, message):
        """
         [from_language] [to_language] [text]
        .vsetranslate en ru Hello, world!
        """
        args = utils.get_args(message)
        langs = ["auto", "ru", "en", "de", "fr", "es", "it", "pt", "ja", "zh", "ko"]
        translators = ["google", "yandex", "bing", "iciba"]
        text = message.text.replace(f"{self.get_prefix()}vsetranslate", "")
        t = ""
        if not args:
            return await utils.answer(message, self.strings["invalid_args"])
        if args[0] not in langs:  # .vsetranslate text
            t = await self.translate(
                text,
                translator=self.config["default_translator"],
                lang_to=self.config["default_lang"],
            )
        elif args[1] not in langs:  # .vsetranslate from_language text
            text = message.text.replace(
                f"{self.get_prefix()}vsetranslate {args[0]}", ""
            )
            t = await self.translate(
                text,
                translator=self.config["default_translator"],
                lang_to=self.config["default_lang"],
                lang_from=args[0],
            )
        elif args[2] not in translators:  # .vsetranslate from_language to_language text
            text = message.text.replace(
                f"{self.get_prefix()}vsetranslate {args[0]} {args[1]}", ""
            )
            t = await self.translate(
                text,
                translator=self.config["default_translator"],
                lang_to=args[1],
                lang_from=args[0],
            )
        else:  # .vsetranslate from_language to_language translator text
            text = message.text.replace(
                f"{self.get_prefix()}vsetranslate {args[0]} {args[1]} {args[2]}", ""
            )
            t = await self.translate(
                text,
                translator=args[2],
                lang_to=args[1],
                lang_from=args[0],
            )
        try:
            await utils.answer(
                message,
                self.strings["answer"].format(
                    t["translator"],
                    t["from"],
                    t["to"],
                    t["text"],
                ),
            )
        except Exception:
            await utils.answer(message, self.strings["error"])
