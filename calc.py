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
# meta pic: https://img.icons8.com/color/344/calculate.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/color/344/calculate.png&title=Calc&description=Module%20for%20inline%20calc

__version__ = (2, 0, 0)

import logging
from telethon import TelegramClient
from .. import loader  # type: ignore
from ..inline.types import InlineCall  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class CalcMod(loader.Module):
    """Module for inline calc"""

    strings = {
        "name": "📟 Calc",
        "answer": "🧮 <b>Start calculating(press inline buttons):</b>",
        "calc": "🧮 <i>{0}</i>=<code>{1}</code>",
        "error": "❗️ Error!",
    }

    strings_ru = {
        "answer": "🧮 <b>Начните подсчитывать(нажимайте на инлайн кнопки):</b>",
        "error": "❗️ Ошибка!",
    }

    async def client_ready(self, client: TelegramClient, db):
        self._db = db
        self._client = client

    async def return_keyboard(self, expression):
        return [
            # 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣0️⃣➗✖️➕➖🧮
            [
                {"text": "1️⃣", "callback": self.calc, "args": ["1", expression]},
                {"text": "2️⃣", "callback": self.calc, "args": ["2", expression]},
                {"text": "3️⃣", "callback": self.calc, "args": ["3", expression]},
            ],
            [
                {"text": "4️⃣", "callback": self.calc, "args": ["4", expression]},
                {"text": "5️⃣", "callback": self.calc, "args": ["5", expression]},
                {"text": "6️⃣", "callback": self.calc, "args": ["6", expression]},
            ],
            [
                {"text": "7️⃣", "callback": self.calc, "args": ["7", expression]},
                {"text": "8️⃣", "callback": self.calc, "args": ["8", expression]},
                {"text": "9️⃣", "callback": self.calc, "args": ["9", expression]},
            ],
            [
                {"text": "➕", "callback": self.calc, "args": ["+", expression]},
                {"text": "0️⃣", "callback": self.calc, "args": ["0", expression]},
                {"text": "➖", "callback": self.calc, "args": ["-", expression]},
            ],
            [
                {"text": "➗", "callback": self.calc, "args": ["/", expression]},
                {"text": "🔙", "callback": self.calc, "args": ["C", expression]},
                {"text": "✖️", "callback": self.calc, "args": ["*", expression]},
            ],
        ]

    async def calc(self, message: InlineCall, press, expression):
        if expression == "0":
            expression = ""
        if press == "C":
            expression = expression[:-1]
        else:
            expression = expression + press

        a = ["+", "-", "*", "/", "=", "C"]
        b = False
        for i in a:
            if press == i:
                b = True

        if b is False and expression != "" and expression != "0":
            result = eval(expression)
        else:
            result = ""

        text = self.strings["calc"].format(expression, result)

        keyboard = await self.return_keyboard(expression)

        await message.edit(text=text, reply_markup=keyboard)

    @loader.unrestricted
    @loader.ratelimit
    async def calccmd(self, message):
        """
         - init calc
        Based on... my code)
        """

        text = self.strings["answer"]

        expression = "0"

        keyboard = await self.return_keyboard(expression)

        await message.delete()
        await self.inline.form(
            text=text,
            message=message,
            always_allow=[message.from_id],
            reply_markup=keyboard,
        )
