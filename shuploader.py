__version__ = (1, 0, 1)

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

import io
import random

import requests
from telethon.tl.types import Message

from .. import loader, utils


@loader.tds
class ShUploaderMod(loader.Module):
    """Different engines file uploader [BETA]"""

    strings = {
        "name": "ShUploader",
        "uploading": "<emoji document_id=5445284980978621387>🚫</emoji> <b>Uploading...</b>",
        "noargs": "<emoji document_id=5843952899184398024>🚫</emoji> <b>No file specified</b>",
        "err": "<emoji document_id=5843952899184398024>🚫</emoji> <b>Upload error</b>",
        "uploaded": '🎡 <b>File <a href="{0}">uploaded</a></b>!\n\n<code>{0}</code>',
    }

    strings_ru = {
        "uploading": "<emoji document_id=5445284980978621387>🚫</emoji> <b>Загрузка...</b>",
        "noargs": "<emoji document_id=5843952899184398024>🚫</emoji> <b>Файл не указан</b>",
        "err": "<emoji document_id=5843952899184398024>🚫</emoji> <b>Ошибка загрузки</b>",
        "uploaded": '<emoji document_id=5226711870492126219>🎡</emoji> <b>Файл <a href="{0}">загружен</a></b>!\n\n<code>{0}</code>',
    }

    async def get_media(self, message: Message):
        reply = await message.get_reply_message()
        m = None
        name = None
        if reply and reply.media:
            m = reply
        elif message.media:
            m = message
        elif not reply:
            await utils.answer(message, self.strings("noargs"))
            return False

        if not m:
            file = io.BytesIO(bytes(reply.raw_text, "utf-8"))
            name = "file.txt"
        else:
            file = io.BytesIO(await self._client.download_media(m, bytes))
            name = (
                m.file.name
                or (
                    "".join(
                        [
                            random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
                            for _ in range(16)
                        ]
                    )
                )
                + m.file.ext
            )

        return {
            "io": file,
            "name": name,
        }

    async def uploadcmd(self, message: Message):
        """
        --days [days] - delete file after [days] --downloads [downloads] - delete file after [downloads]
        """
        message = await utils.answer(message, self.strings("uploading"))
        file = await self.get_media(message)
        args = utils.get_args(message)
        if not file:
            return
        
        headers = {}
        
        if args:
            if '--days' in args:
                days = args[args.index('--days')+1]
                if days.isdigit():
                    headers['Max-Days'] = days

            if '--downloads' in args:
                downloads = args[args.index('--downloads')+1]
                if downloads.isdigit():
                    headers['Max-Downloads'] = downloads

        try:
            sh = await utils.run_sync(
                requests.put,
                f"https://sh.vsecoder.me/{file['name']}",
                data=file["io"],
                headers=headers,
            )
        except ConnectionError:
            await utils.answer(message, self.strings("err"))
            return

        url = sh.text
        await utils.answer(message, self.strings("uploaded").format(url))
