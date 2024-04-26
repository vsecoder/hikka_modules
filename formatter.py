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
# meta pic: https://img.icons8.com/fluency/344/pen-1.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/fluency/344/pen-1.png&title=FormatterMod&description=Module%20for%20prettifying%20the%20formatting%20of%20messages

__version__ = (1, 0, 1)

import logging
from .. import loader, utils  # type: ignore

import datetime as dt
import re
from telethon.tl.types import Message

logger = logging.getLogger(__name__)


def _copy_tl(o, **kwargs):
    d = o.to_dict()
    del d["_"]
    d.update(kwargs)
    return o.__class__(**d)


@loader.tds
class FormatterMod(loader.Module):
    """
    Module for prettifying the formatting of messages 🪛

    📌 For example write:
    --------------------
    Hi, now is {now}, today is {today}, yesterday is {yesterday}, my id is {id}, username is @{username}...

    ⌨️ Keyboard:
    ~
    📥 Modules $ https://t.me/vsecoder_m
    👨‍💻 Dev $ https://t.me/vsecoder
    --------------------

    P.S. "~" is a separator for keyboard and message.
         "$" is a separator for button and link.

    """

    strings = {"name": "Formatter"}

    async def client_ready(self, client, db):
        self._client = client
        self.me = await client.get_me()
        self.html = await self.import_lib(
            "https://raw.githubusercontent.com/vsecoder/hikka_modules/main/libs/html2.py",
            suspend_on_error=True,
        )

    async def watcher(self, message: Message):
        if (
            not isinstance(message, Message)
            or not message.out
            or message.text.split()
            and message.text.split()[0].lower() in self.allmodules.commands
            or utils.remove_html(message.text).startswith(self.get_prefix())
        ):
            return

        text = message.text

        keyboard = []
        if len(text.split("\n~\n")) == 2:
            for key in message.raw_text.split("\n~\n")[1].split("\n"):
                if len(key.split(" $ ")) == 2:
                    button = key.split(" $ ")[0]
                    CLEANR = re.compile(
                        "<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});"
                    )
                    link = re.sub(CLEANR, "", key.split(" $ ")[1])
                    keyboard.append([{"text": button, "url": link}])

        text = text.split("\n~\n")[0]

        """ Deleted because of bugs
        raw_cut_text = message.raw_text.split("\n~\n")
        logger.error(str(raw_cut_text))

        entities = self.html.parse(message.text)[1]

        for entity in entities.copy():
            if not hasattr(entity, "offset") or not hasattr(entity, "length"):
                continue

            if entity.offset > len(raw_cut_text):
                entities.remove(entity)
                continue

            if entity.offset + entity.length > len(raw_cut_text):
                entities[entities.index(entity)] = _copy_tl(
                    entity,
                    length=len(raw_cut_text) - entity.offset,
                )

        text = self.html.unparse(raw_cut_text, entities)
        """

        formats = {
            "{now}": dt.datetime.now(),
            "{today}": dt.date.today(),
            "{yesterday}": dt.date.today() - dt.timedelta(days=1),
            "{id}": self._client.tg_id,
            "{username}": self.me.username,
            "{phone}": self.me.phone,
            "{msg}": message,
        }

        for key, value in formats.items():
            text = text.replace(key, utils.escape_html(value))

        if text and text != message.text or keyboard and keyboard != [[]]:
            await utils.answer(message, text, reply_markup=keyboard)
