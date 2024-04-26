"""
                              _
__   _____  ___  ___ ___   __| | ___ _ __
\ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
 \ V /\__ \  __/ (_| (_) | (_| |  __/ |
  \_/ |___/\___|\___\___/ \__,_|\___|_|

  Copyleft 2022 t.me/vsecoder
  This program is free software; you can redistribute it and/or modify

"""

import contextlib

# meta developer: @vsecoder_m
# meta pic: https://img.icons8.com/color/344/antivirus-scanner--v1.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/color/344/antivirus-scanner--v1.png&title=Check%20module&description=Module%20for%20check%20modules

__version__ = (3, 3, 0)

import logging
import re
import requests
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)


checker_regex = {
    "critical": [
        {"command": "DeleteAccountRequest", "perms": "delete account"},
        {"command": "edit_2fa", "perms": "change 2FA password"},
        {"command": "get_me", "perms": "presumably get your profile account data"},
        {"command": "disconnect", "perms": "disconnect account"},
        {"command": "log_out", "perms": "disconnect account"},
        {"command": "ResetAuthorizationRequest", "perms": "kill account sessions"},
        {
            "command": "GetAuthorizationsRequest",
            "perms": "get telegram api_id and api_hash",
        },
        {"command": "AddRequest", "perms": "get telegram api_id and api_hash"},
        {"command": "pyarmor", "perms": "all(obfuscated script)"},
        {"command": "pyrogram", "perms": "another tg client"},
        {"command": "system", "perms": "presumably eval commands"},
        {"command": "eval", "perms": "presumably eval python code"},
        {"command": "exec", "perms": "presumably exec python code"},
        {
            "command": "sessions",
            "perms": "get all sessions data, delete sessoins, copy and send sessions",
        },
        {"command": "subprocess", "perms": "eval commands"},
        {"command": "torpy", "perms": "download viruses"},
        {"command": "httpimport", "perms": "import malicious scripts"},
    ],
    "warn": [
        {"command": "list_sessions", "perms": "get all account sessions"},
        {"command": "LeaveChannelRequest", "perms": "leave channel and chats"},
        {"command": "JoinChannelRequest", "perms": "join channel and chats"},
        {
            "command": "ChannelAdminRights",
            "perms": "edit channel and chats users perms",
        },
        {"command": "EditBannedRequest", "perms": "kick and ban users"},
        {"command": "remove", "perms": "presumably remove files"},
        {"command": "rmdir", "perms": "presumably remove dirs"},
        {"command": "telethon", "perms": "telethon funcs"},
        {"command": "get_response", "perms": "get telegram messages"},
    ],
    "council": [
        {"command": "requests", "perms": "send requests"},
        {"command": "get_entity", "perms": "get entities"},
        {"command": "get_dialogs", "perms": "get dialogs"},
        {"command": "os", "perms": "presumably get os info"},
        {"command": "sys", "perms": "presumably get sys info"},
        {"command": "import", "perms": "import modules"},
        {"command": "client", "perms": "all client functions"},
        {"command": "send_message", "perms": "send messages"},
        {"command": "send_file", "perms": "send files"},
        {"command": "TelegramClient", "perms": "create new session"},
        {"command": "download_file", "perms": "download telegram files"},
        {"command": "ModuleConfig", "perms": "create configs"},
    ],
}


@loader.tds
class CheckModulesMod(loader.Module):
    """Module for check modules"""

    strings = {
        "name": "Check module",
        "cfg_lingva_url": (
            "Check the module for suspicious features, scam, and find out what the"
            " module has access to"
        ),
        "answer": (
            "🔍 <b>Module check complete</b>:\n\n⛔️ Criticals:\n{0}\n🟡 Warns:\n{1}\n✅"
            " Councils:\n{2}"
        ),
        "component": " ▪️ «<code>{0}</code>» in module have permissions on <i>{1}</i>",
        "error": (
            "Error!\n\n.checkmod <module_link>\n.checkmod"
            " https://raw.githubusercontent.com/vsecoder/hikka_modules/main/googleit.py"
        ),
    }

    strings_ru = {
        "cfg_lingva_url": (
            "Проверьте модуль на подозрительные возможности, скам, и узнайте к чему"
            " есть доступ у модуля"
        ),
        "answer": (
            "🔍 <b>Проверка модуля завершена</b>:\n\n⛔️ Критические:\n{0}\n🟡"
            " Предупреждения:\n{1}\n✅ Советы:\n{2}"
        ),
        "component": " ▪️ «<code>{0}</code>» в модуле имеет разрешения на <i>{1}</i>",
        "error": (
            "Ошибка!\n\n.checkmod <module_link>\n.checkmod"
            " https://raw.githubusercontent.com/vsecoder/hikka_modules/main/googleit.py"
        ),
    }

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    async def check_m(self, args):
        string = args
        critical = ""
        warn = ""
        council = ""
        for command in checker_regex["critical"]:
            r = re.search(command["command"], string)
            if r is not None:
                critical = (
                    critical
                    + self.strings["component"].format(
                        command["command"], command["perms"]
                    )
                    + "\n"
                )

        if not critical:
            critical = " ▪️ ➖\n"

        for command in checker_regex["warn"]:
            r = re.search(command["command"], string)
            if r is not None:
                warn = (
                    warn
                    + self.strings["component"].format(
                        command["command"], command["perms"]
                    )
                    + "\n"
                )

        if not warn:
            warn = " ▪️ ➖\n"

        for command in checker_regex["council"]:
            r = re.search(command["command"], string)
            if r is not None:
                council = (
                    council
                    + self.strings["component"].format(
                        command["command"], command["perms"]
                    )
                    + "\n"
                )

        if not council:
            council = " ▪️ ➖\n"

        return self.strings["answer"].format(critical, warn, council, args)

    @loader.unrestricted
    @loader.ratelimit
    async def checkmodcmd(self, message):
        """
        <module_link> or "reply file" or "send file" - perform module check
        """
        args = utils.get_args_raw(message)
        if args:
            with contextlib.suppress(Exception):
                r = await utils.run_sync(requests.get, args)
                string = r.text
                await utils.answer(message, await self.check_m(string))
                return

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

        args = code_from_message or code_from_reply
        await utils.answer(message, await self.check_m(args))
