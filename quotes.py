__version__ = (0, 0, 2)
"""
                                _
  __   _____  ___  ___ ___   __| | ___ _ __
  \ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
   \ V /\__ \  __/ (_| (_) | (_| |  __/ |
    \_/ |___/\___|\___\___/ \__,_|\___|_|

    Copyleft 2022 t.me/vsecoder                                                            
    This program is free software; you can redistribute it and/or modify 

    Thk @Fl1yd, based on his module

"""

import base64
import io
import logging
from time import gmtime
from typing import List, Union

import requests
import telethon  # type: ignore
from telethon.tl import types  # type: ignore
from telethon.tl.patched import Message  # type: ignore

from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


class EntityPayload:
    def __init__(
        self,
        type_: str,
        offset: int,
        length: int,
        url: Union[str, None] = None,
        user: Union[dict, None] = None,
        language: Union[str, None] = None,
        **kwargs,
    ):
        self.type = type_
        self.offset = offset
        self.length = length
        self.url = url
        self.user = user
        self.language = language
        self._ = kwargs

    def to_dict(self):
        return {
            "_": "MessageEntity",
            "type": self.type,
            "offset": self.offset,
            "length": self.length,
            "url": self.url,
            "user": self.user,
            "language": self.language,
            ("custom_emoji_id" if self.type == "custom_emoji" else None): (
                str(self._["document_id"]) if self.type == "custom_emoji" else None
            ),
        }


class UserPayload:
    def __init__(
        self,
        id_: int,
        first_name: str,
        last_name: str,
        username: str,
        language_code: str,
        title: Union[str, None],
        emoji_status: str,
        photo: dict,
        type_: str,
    ):
        self.id = id_
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.language_code = language_code
        self.title = title
        self.emoji_status = emoji_status
        self.photo = photo
        self.type = type_
        self.name = f"{self.first_name or ''} {self.last_name or ''}"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language_code": self.language_code,
            "title": self.title,
            "emoji_status": self.emoji_status,
            "photo": self.photo,
            "type": self.type,
            "name": self.name,
        }


class MessagePayload:
    def __init__(
        self,
        text: str,
        entities: Union[List[EntityPayload], None],
        chat_id: int,
        avatar: bool,
        from_: UserPayload,
        reply: Union[dict, None],
        media: Union[dict, None] = None,
        voice: Union[str, None] = None,
        is_forward: bool = False,
        via_bot: Union[str, None] = None,
    ):
        self.text = text
        self.media = media
        self.voice = {"waveform": voice} if voice else None
        self.entities = entities
        self.chat_id = chat_id
        self.avatar = avatar
        self.from_ = from_
        self.reply = reply

        if is_forward:
            self.from_.name = f"Forwarded from {self.from_.name}"

        if via_bot:
            self.from_.name = f"via @{via_bot}"

    def to_dict(self):
        return {
            "text": self.text,
            "media": {"base64": self.media} if self.media else None,
            "voice": self.voice,
            "entities": [entity.to_dict() for entity in self.entities]
            if self.entities
            else None,
            "chatId": self.chat_id,
            "avatar": self.avatar,
            "from": self.from_.to_dict(),
            "replyMessage": self.reply,
        }


class QuotePayload:
    def __init__(
        self,
        messages: List[MessagePayload],
        type_: str = "quote",
        **kwargs,
    ):
        self.type = type_
        self.messages = messages
        self._ = kwargs

    def to_dict(self):
        return {
            "type": self.type,
            "format": "webp",
            "width": 512,
            "height": 768,
            "scale": 2,
            "messages": [message.to_dict() for message in self.messages],
            **self._,
        }


def get_message_media(message: Message):
    return (
        message.photo
        #or message.sticker
        #or message.video
        #or message.video_note
        #or message.gif
        or message.web_preview
        if message and message.media
        else None
    )


def get_entities(entities: types.TypeMessageEntity):
    # coded by @droox
    r = []  # EntityPayload
    if entities:
        for entity in entities:
            entity = entity.to_dict()
            logger.error(entity)
            entity["type"] = entity.pop("_").replace("MessageEntity", "").lower()
            if entity["type"] == "customemoji":
                entity["type"] = "custom_emoji"
            type_ = entity["type"]
            offset = entity["offset"]
            length = entity["length"]
            del entity["type"], entity["offset"], entity["length"]

            r.append(
                EntityPayload(
                    type_,
                    offset,
                    length,
                    **entity,
                )
            )
    return r


def get_message_text(message: Message, reply: bool = False):
    mb = 1024 * 1024
    if message.photo and reply:
        return "📷 Photo"
    elif message.sticker:  #and reply:
        return f"{message.file.emoji} Sticker"
    elif message.video_note:  #and reply:
        return "📹 Video note"
    elif message.video:  #and reply:
        return "📹 Video"
    elif message.gif:  #and reply:
        return "🖼 GIF"
    elif message.poll:
        return "📊 Questioning"
    elif message.geo:
        return "📍 Geolocation"
    elif message.contact:
        return "👤 Contact"
    elif message.voice:
        duration = strftime(message.voice.attributes[0].duration)
        size = (
            message.voice.size / 1024
            if message.voice.size < mb
            else (message.voice.size / 1024 / 1024)
        )
        return f"▶️                  {duration}, {size:.1f} {('KB' if message.voice.size < mb else 'MB')}"
    elif message.audio:
        audio_attributes = message.audio.attributes[0]
        duration = strftime(audio_attributes.duration)
        return f"🎧 Music: {duration} | {audio_attributes.performer} - {audio_attributes.title}"
    elif type(message.media) == types.MessageMediaDocument and not get_message_media(
        message
    ):
        media = message.media.document.size
        size = (
            media / 1024
            if media < mb
            else (media / 1024 / 1024)
        )
        return f"💾 File: {message.file.name}, {size:.1f} {('KB' if media < mb else 'MB')}"
    elif type(message.media) == types.MessageMediaDice:
        return f"{message.media.emoticon} {message.media.value} points"
    elif type(message) == types.MessageService:
        return f"Service message: {message.action.to_dict()['_']}"
    else:
        return message.raw_text


def strftime(time: Union[int, float]):
    t = gmtime(time)
    return (
        f"{t.tm_hour:02d}:" if t.tm_hour > 0 else ""
    ) + f"{t.tm_min:02d}:{t.tm_sec:02d}"


def decode_waveform(wf):
    if not wf:
        return [0 for _ in range(0, 20)]
    bits_count = len(wf) * 8
    values_count = bits_count // 5

    if not values_count:
        return []

    last_idx = values_count - 1

    result = []
    for i in range(last_idx):
        j = i * 5
        byte_idx = j // 8
        bit_shift = j % 8
        result.append((wf[byte_idx] >> bit_shift) & 0b11111)

    last_byte_idx = (last_idx * 5) // 8
    last_bit_shift = (last_idx * 5) % 8
    last_value = (
        wf[last_byte_idx]
        if last_byte_idx == len(wf) - 1
        else int.from_bytes(wf[last_byte_idx : last_byte_idx + 2], "little")
    )
    result.append((last_value >> last_bit_shift) & 0b11111)

    return result


async def get_reply(message: Message) -> Union[dict, None]:
    reply_name = reply_text = None
    if not message.fwd_from:
        if reply := await message.get_reply_message():
            reply_name = telethon.utils.get_display_name(reply.sender)
            reply_text = get_message_text(reply, True)

    return (
        {
            "chatId": message.chat_id,
            "text": reply_text,
            "name": reply_name,
        }
        if reply_name
        else None
    )


@loader.tds
class QuotesMod(loader.Module):
    """
    Quotes by @vsecoder

    Now doesn't work stickers, gifs, video, audio.
    Fake quotes later.

    Thk @Fl1yd, based on his SQuotes module
    """

    strings = {
        "name": "Quotes",
        "no_reply": "<b>[Quotes]</b> No reply",
        "api_error": "<b>[Quotes]</b> API error",
        "no_args_or_reply": "<b>[Quotes]</b> No args or reply",
        "args_error": (
            "<b>[Quotes]</b> An error ocurred while parsing args. Request was:"
            " <code>{}</code>"
        ),
    }

    async def client_ready(self, client: telethon.TelegramClient, db: dict) -> None:
        self.client = client
        self.db = db
        self.api_endpoint = "http://q.api.vsecoder.dev/generate"
        self.settings = self.get_settings()

    async def qcmd(self, message: Message) -> None:
        """
        <reply> [quantity] [!story] [color] - Create nice quote from message(-s)
        """

        args: List[str] = utils.get_args(message)
        if not await message.get_reply_message():
            await utils.answer(message, self.strings["no_reply"])
            return

        stories = "!story" in args
        [count] = [int(arg) for arg in args if arg.isdigit() and int(arg) > 0] or [1]
        [bg_color] = [arg for arg in args if arg != "!story" and not arg.isdigit()] or [
            self.settings["bg_color"]
        ]

        payload = QuotePayload(
            await self.quote_parse_messages(message, count),
            ("stories" if stories else "quote"),
            **({"quote_color": bg_color, "text_color": self.settings["text_color"]}),
        ).to_dict()
        logger.error(payload)

        r = await self._api_request(payload)
        if r.status_code != 200:
            await utils.answer(message, self.strings["api_error"])
            return

        quote = r.json()["image"]
        img_data = quote.encode()
        content = base64.b64decode(img_data)
        quote = io.BytesIO(content)
        quote.name = f'Quote.{"png" if stories else "webp"}'

        await utils.answer(message, quote, force_document=stories)
        await (
            message[0] if isinstance(message, (list, tuple, set)) else message
        ).delete()

    async def quote_parse_messages(self, message: Message, count: int):
        payloads = []
        messages = [
            msg
            async for msg in self.client.iter_messages(
                message.chat_id,
                count,
                reverse=True,
                add_offset=1,
                offset_id=(await message.get_reply_message()).id,
            )
        ]

        for message in messages:
            media = get_message_media(message)
            base64_media = None
            if media:
                base64_media = base64.b64encode(
                    await self.client.download_file(media)
                ).decode()
            text = get_message_text(message, False)
            entities = get_entities(message.entities)
            user_entity = await self.client.get_entity(
                message.sender_id if not message.fwd_from else message.fwd_from.from_id
            )

            from_ = UserPayload(
                user_entity.id,
                user_entity.first_name,
                user_entity.last_name,
                user_entity.username
                if user_entity.username
                else user_entity.usernames[0].username if user_entity.usernames else "",
                "ru",
                None,
                str(user_entity.emoji_status.document_id)
                if user_entity.premium
                else None,
                {"small_file_id": user_entity.photo.photo_id}
                if user_entity.photo
                else None,
                "private",
            )

            reply = await get_reply(message)

            payloads.append(
                MessagePayload(
                    text,
                    entities,
                    message.chat_id,
                    True,
                    from_,
                    reply,
                    base64_media,
                    decode_waveform(message.voice.attributes[0].waveform)
                    if message.voice
                    else None,

                    True if message.fwd_from else False,
                    message.via_bot.username if message.via_bot else None
                )
            )

        return payloads

    async def get_profile_data(self, user: types.User):
        avatar = await self.client.download_profile_photo(user.id, bytes)
        return (
            telethon.utils.get_display_name(user),
            base64.b64encode(avatar).decode() if avatar else None,
        )

    async def sqsetcmd(self, message: Message) -> None:
        """<bg_color/text_color> <value> - Configure SQuotes"""
        args: List[str] = utils.get_args_raw(message).split(maxsplit=1)
        if not args:
            return await utils.answer(
                message,
                (
                    "<b>[Quotes]</b> Settings:\n\nMax messages"
                    " (<code>max_messages</code>):"
                    f" {self.settings['max_messages']}\nBackground color"
                    f" (<code>bg_color</code>): {self.settings['bg_color']}\nForeground"
                    f" color (<code>text_color</code>): {self.settings['text_color']}"
                ),
            )

        if args[0] == "reset":
            self.get_settings(True)
            await utils.answer(message, "<b>[Quotes]</b> Settings has been reset")
            return

        if len(args) < 2:
            await utils.answer(message, "<b>[Quotes]</b> Insufficient args")
            return

        mods = ["max_messages", "bg_color", "text_color"]
        if args[0] not in mods:
            await utils.answer(message, f"<b>[Quotes]</b> Unknown param")
            return
        elif args[0] == "max_messages":
            if not args[1].isdigit():
                await utils.answer(message, "<b>[Quotes]</b> Number is expected")
                return

            self.settings[args[0]] = int(args[1])

        else:
            self.settings[args[0]] = args[1]

        self.db.set("Quotes", "settings", self.settings)
        return await utils.answer(
            message, f"<b>[Quotes]</b> Param {args[0]} value is now {args[1]}"
        )

    def get_settings(self, force: bool = False):
        settings: dict = self.db.get("Quotes", "settings", {})
        if not settings or force:
            settings.update(
                {"max_messages": 15, "bg_color": "#162330", "text_color": "#fff"}
            )
            self.db.set("Quotes", "settings", settings)

        return settings

    async def _api_request(self, data: dict):
        return await utils.run_sync(requests.post, self.api_endpoint, json=data)
