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

__version__ = (2, 0, 0)

import logging
from typing import Optional
from .. import loader, utils  # type: ignore

from pygments.lexers import guess_lexer, get_lexer_by_name
from pygments.formatters import ImageFormatter
from pygments import highlight
from PIL import Image

from pygments.styles.monokai import MonokaiStyle
from pygments.styles.zenburn import ZenburnStyle
from pygments.styles.material import MaterialStyle
from pygments.styles.dracula import DraculaStyle

from io import BytesIO


STYLE_CLASS_MAP = {
    "monokai": MonokaiStyle,
    "zenburn": ZenburnStyle,
    "material": MaterialStyle,
    "dracula": DraculaStyle,
}


class FormatCode:
    def run(
        self,
        code: str,
        language: str,
        font: str = "DejaVu Sans Mono",
        style: str = "monokai",
        line_numbers: bool = True,
    ) -> str:
        name = "out.png"
        max_height = 10000
        max_width = 10000
        code = (
            "\n"
            + "\n".join(f"  {x[:max_width]}  " for x in code.splitlines()[:max_height])
            + "\n"
        )

        try:
            lexer = get_lexer_by_name(language.lower())
        except:
            lexer = guess_lexer(code)

        style = STYLE_CLASS_MAP.get(style, style)
        formatter = ImageFormatter(
            font_name=font,
            font_size=36,
            style=style,
            line_numbers=line_numbers,
            image_pad=20,
            line_pad=12,
        )
        result = highlight(code, lexer, formatter)
        stream = BytesIO(result)

        image = Image.open(stream).convert("RGBA")
        stream.close()
        image.save(name)

        return name


logger = logging.getLogger(__name__)


@loader.tds
class OctoCodeMod(loader.Module):
    """Module for octopussed code"""

    strings = {
        "name": "OctoCode",
        "answer": "🐙 <b>Code</b> <i>octopussed</i>: ",
        "loading": "🐙 <b>Loading</b>...",
        "cfg_theme": "🦎 Themes: monokai, zenburn, material, dark",
        "cfg_font": "🦎 Type of font url .ttf",
        "cfg_line_numbers": "🦎 Type True/False to manage a number of line numbers",
        "cfg_default_lang": "🦎 Enter the programming language to use by default",
        "error": "❗️ Error: {0}",
    }

    strings_ru = {
        "answer": "🐙 <b>Код</b> <i>осьмоножен</i>: ",
        "loading": "🐙 <b>Загрузка</b>...",
        "cfg_theme": "🦎 Темы: monokai, zenburn, material, dark",
        "cfg_font": "🦎 Введите ссылку на шрифт .ttf",
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
                    ["monokai", "zenburn", "material", "dark"]
                ),
            ),
            loader.ConfigValue(
                "line_numbers",
                True,
                self.strings["cfg_line_numbers"],
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "default_lang",
                "python",
                self.strings["cfg_default_lang"],
            ),
        )
        self.name = self.strings["name"]

    @loader.unrestricted
    @loader.ratelimit
    async def octocmd(self, message):
        """
         <code> or "reply file" or "send file"
        Octopussed your code
        """
        await utils.answer(message, self.strings["loading"])
        try:
            file = ""
            query = ""
            formatter = FormatCode()
            args = utils.get_args_raw(message)
            if args:
                try:
                    formatter.run(
                        args,
                        language=self.config["default_lang"],
                        font=self.config["font"],
                        style=self.config["theme"],
                        line_numbers=self.config["line_numbers"],
                    )
                except Exception as e:
                    await utils.answer(message, self.strings["error"].format(e))
                    return

                await utils.answer(message, self.strings["answer"])
                return await self._client.send_file(
                    utils.get_chat_id(message),
                    open("out.png", "rb"),
                )

            try:
                code_from_message = (
                    await self._client.download_file(message.media, bytes)
                ).decode("utf-8")
            except Exception:
                code_from_message = ""

            try:
                reply = await message.get_reply_message()
                code_from_reply = (
                    await self._client.download_file(reply.media, bytes)
                ).decode("utf-8")
            except Exception:
                code_from_reply = ""

            query = code_from_message or code_from_reply
            try:
                formatter.run(
                    query,
                    language=self.config["default_lang"],
                    font="DejaVu Sans Mono",
                    style=self.config["theme"],
                    line_numbers=self.config["line_numbers"],
                )
            except Exception as e:
                await utils.answer(message, self.strings["error"].format(e))
                return

            await utils.answer(message, self.strings["answer"])
            await self._client.send_message(
                utils.get_chat_id(message),
                file=open("out.png", "rb"),
                force_document=(len(args.splitlines()) > 50),
                reply_to=getattr(message, "reply_to_msg_id", None),
            )
        except Exception as e:
            await utils.answer(message, self.strings["error"].format(e))
