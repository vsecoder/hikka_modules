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

version = (1, 0, 0)

from telethon import functions
from telethon.tl.types import Message
import asyncio
import logging

from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


@loader.tds
class ChatGPTfreeMod(loader.Module):
    """
    Бесплатный модуль для ChatGPT
    https://t.me/Jarvis_IT_Assistant_bot
    Сначала запустите бота и отключите уведомления
    """

    strings = {
        "name": "ChatGPTfree",
        "loading": "🔄 Ваш запрос обрабатывается...",
        "no_args": "🚫 Не указан текст для обработки!",
        "start_text": "<b>🤖 ChatGPT:</b>\n",
        "context_text": "❕ Создался новый диалог. Предыдущие запросы удалены.",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.gpt_free = "@Jarvis_IT_Assistant_bot"

    async def message_q(
        self,
        text: str,
        user_id: int,
        mark_read: bool = False,
        delete: bool = False,
        ignore_answer: bool = False,
    ):
        """Отправляет сообщение и возращает ответ"""
        async with self.client.conversation(user_id) as conv:
            msg = await conv.send_message(text)
            while True:
                await asyncio.sleep(1)
                response = await conv.get_response()
                if mark_read:
                    await conv.mark_read()

                if delete:
                    await msg.delete()
                    await response.delete()

                if ignore_answer:
                    return response

                if "✅ Запрос отправлен" in response.text:
                    continue

                if "Ожидание ответа" in response.text:
                    continue

                return response

    async def chatgptfreecmd(self, message: Message):
        """
        {text} - обработать текст через ChatGPT
        """
        args = utils.get_args_raw(message)

        if not args:
            return await utils.answer(message, self.strings["no_args"])

        await utils.answer(message, self.strings["loading"])

        response = await self.message_q(
            args, self.gpt_free, mark_read=True, delete=True, ignore_answer=False
        )

        text = self.strings["start_text"] + response.text.replace(
            "/context", "<code>.contextgpt</code>"
        )

        return await utils.answer(message, text)

    async def contextgptcmd(self, message: Message):
        """
        - сбросить диалог и начать новый
        """
        await self.message_q(
            "/context", self.gpt_free, mark_read=True, delete=True, ignore_answer=True
        )
        return await utils.answer(message, self.strings["context_text"])
