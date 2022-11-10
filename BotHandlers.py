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
# meta pic: https://img.icons8.com/cute-clipart/512/futurama-bender.png

__version__ = (2, 0, 0)

import logging
from .. import loader, utils
from aiogram.types import Message as AiogramMessage

logger = logging.getLogger(__name__)

template = {
    "command": None,
    "text": None,
}


@loader.tds
class BotHandlers(loader.Module):
    """
    Module for create bot commands handlers
    """

    strings = {
        "name": "BotHandlers",
    }

    async def client_ready(self, client, db):
        self._client = client
        self.db = db

    async def addhandlercmd(self, message):
        """
         <command> <text> - Add handler
        """
        args = utils.get_args_raw(message)
        if not args or len(args.split()) < 2:
            await message.edit("<b>Usage:</b> .addhandler <command> <reply>")
            return

        command = args.split()[0]
        reply = args.split()[1]

        cmd = template.copy()
        cmd["command"] = command
        cmd["text"] = reply

        commands = self.db.get("BotHandlers", "commands")
        if not commands:
            commands = []
        commands.append(cmd)
        self.db.set("BotHandlers", "commands", commands)

        await message.edit(f"<b>Added handler:</b> {command} -> {reply}")

    async def delhandlercmd(self, message):
        """
         <command> - Delete handler
        """
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("<b>Usage:</b> .delhandler <command>")
            return

        command = args

        commands = self.db.get("BotHandlers", "commands")
        if not commands:
            await message.edit("<b>There are no handlers</b>")
            return

        for cmd in commands:
            if cmd["command"] == command:
                commands.remove(cmd)
                self.db.set("BotHandlers", "commands", commands)
                await message.edit(f"<b>Deleted handler:</b> {command}")
                return

        await message.edit(f"<b>Handler {command} not found!</b>")

    async def listhandlerscmd(self, message):
        """
         - List handlers
        """
        commands = self.db.get("BotHandlers", "commands")

        string = "List handlers:\n"

        for command in commands:
            string += f" - {command['command']}"

        await message.answer(string)

    async def aiogram_watcher(self, message: AiogramMessage):
        commands = self.db.get("BotHandlers", "commands")
        if not commands:
            return

        for cmd in commands:
            if cmd["command"] == message.text:
                await message.answer(cmd["text"])
                return
