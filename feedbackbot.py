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
# meta pic: https://img.icons8.com/fluency/344/feedback.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/fluency/344/feedback.png&title=Feedback&description=Feedback%20bot%20for%20Hikka%20modules

__version__ = (3, 0, 1)

import logging
import time
from telethon.utils import get_display_name
from aiogram.types import Message as AiogramMessage
from .. import loader, utils  # type: ignore
from ..inline.types import InlineCall  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class FeedbackBotMod(loader.Module):
    """FeedbackBot"""
    strings = {
        "name": "📥 Feedback",
        "start": "✌️ Hi, I'm feedback bot as {}",
        "fb_message": "📝 Take to send message",
        "wait": "⏳ You can send next message in {} second(-s)",
        "start_feedback": (
            "📝 Write 1 message, and I'll send it to {}\n\n[{} per minute]"
        ),
        "sent": "📩 Message sent",
        "banned": "🚫 You are banned",
        "user_banned": "🚫 {} is banned",
    }

    strings_ru = {
        "start": "✌️ Привет, я бот обратной связи {}",
        "fb_message": "📝 Нажмите для отправки сообщения",
        "wait": "⏳ Вы можете отправить сообщение через {} секунд(-ы)",
        "start_feedback": "📝 Напишите сообщение, и я отправлю его {}\n\n[{} в минуту]",
        "sent": "📩 Сообщение отправлено",
        "banned": "🚫 Вы забанены",
        "user_banned": "🚫 {} забанен",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "ratelimit",
                "1",
                "Rate limit(in minutes)",
                validator=loader.validators.Integer(minimum=0),
            )
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._client = client

        self._name = utils.escape_html(get_display_name(await client.get_me()))

        self._ratelimit = {}
        self._ban_list = []

        self.__doc__ = (
            "Module from add feedback bot 👨‍💻\n\n"
            "📝 Dev: @vsecoder\n"
            "📥 Source: github.com/vsecoder/hikka_modules"
            f"🔗 Feedback link: t.me/{self.inline.bot_username}?start=feedback\n\n"
            '❌ Toggle in .security "✅ Everyone (inline)" to use'
        )

    async def aiogram_watcher(self, message: AiogramMessage):
        if message.text == "/start feedback":
            if str(message.from_user.id) in map(str, self._ban_list):
                return await message.answer(self.strings["banned"])

            _markup = self.inline.generate_markup(
                {"text": self.strings["fb_message"], "data": "fb_message"}
            )

            await message.answer(
                self.strings["start"].format(self._name),
                reply_markup=_markup,
            )

        if self.inline.gs(message.from_user.id) == "fb_send_message":
            await self.inline.bot.forward_message(
                self._tg_id,
                message.chat.id,
                message.message_id,
            )
            _markup = self.inline.generate_markup(
                {"text": "🚫 Ban", "data": f"fb_ban/{message.from_user.id}"}
            )
            await self.inline.bot.send_message(
                self._tg_id,
                f"{message.chat.id}",
                reply_markup=_markup,
            )
            await message.answer(self.strings["sent"])
            self._ratelimit[message.from_user.id] = (
                time.time() + self.config["ratelimit"] * 60
            )
            self.inline.ss(message.from_user.id, False)

    @loader.inline_everyone
    async def feedback_callback_handler(self, call: InlineCall):
        if call.data == "fb_cancel":
            self.inline.ss(call.from_user.id, False)
            await self.inline.bot.delete_message(
                call.message.chat.id,
                call.message.message_id,
            )
            return

        if call.data.split("/")[0] == "fb_ban":
            fb_ban_id = call.data.split("/")[1]
            if str(fb_ban_id) in str(self._ban_list):
                pass
            else:
                self._ban_list.append(fb_ban_id)
                await call.answer(self.strings["user_banned"].format(fb_ban_id))

        if call.data != "fb_message":
            return

        if str(call.from_user.id) in str(self._ban_list):
            await call.answer(
                self.strings["banned"],
                show_alert=True,
            )

        if (
            call.from_user.id in self._ratelimit
            and self._ratelimit[call.from_user.id] > time.time()
        ):
            await call.answer(
                self.strings["wait"].format(
                    self._ratelimit[call.from_user.id] - time.time()
                ),
                show_alert=True,
            )
            return

        self.inline.ss(call.from_user.id, "fb_send_message")

        await call.answer(
            self.strings["start_feedback"].format(self._name, self.config["ratelimit"]),
        )
