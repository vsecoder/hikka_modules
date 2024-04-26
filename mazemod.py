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
# meta pic: https://img.icons8.com/external-icongeek26-linear-colour-icongeek26/344/external-maze-game-development-icongeek26-linear-colour-icongeek26.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/external-icongeek26-linear-colour-icongeek26/344/external-maze-game-development-icongeek26-linear-colour-icongeek26.png&title=MazeMod&description=Telegram%20Maze%20Game

__version__ = (2, 0, 0)

import logging
import random
from telethon import TelegramClient
from .. import loader  # type: ignore
from ..inline.types import InlineCall  # type: ignore

logger = logging.getLogger(__name__)


class Maze:
    def __init__(self, rowsNumber, columnsNumber):
        self.rowsNumber = rowsNumber
        self.columnsNumber = columnsNumber
        self.maze = []

    def isEven(self, number):
        return number % 2 == 0

    def getRandomFrom(self, array):
        return random.choice(array)

    def setField(self, x, y, value):
        if x < 0 or x >= self.columnsNumber or y < 0 or y >= self.rowsNumber:
            return False

        self.maze[y][x] = value

    def getField(self, x, y):
        if x < 0 or x >= self.columnsNumber or y < 0 or y >= self.rowsNumber:
            return False

        return self.maze[y][x]

    def isMaze(self):
        for x in range(self.columnsNumber):
            for y in range(self.rowsNumber):
                if self.isEven(x) and self.isEven(y) and self.getField(x, y) == "⬜️":
                    return False

        return True

    def moveTractor(self, tractor):
        directs = []
        if tractor["x"] > 0:
            directs.append("left")

        n = self.columnsNumber - 2

        if tractor["x"] < n:
            directs.append("right")

        if tractor["y"] > 0:
            directs.append("up")

        n = self.rowsNumber - 2

        if tractor["y"] < n:
            directs.append("down")

        direct = self.getRandomFrom(directs)

        if direct == "left":
            if self.getField(tractor["x"] - 2, tractor["y"]) == "⬜️":
                self.setField(tractor["x"] - 1, tractor["y"], "⬛️")
                self.setField(tractor["x"] - 2, tractor["y"], "⬛️")
            tractor["x"] -= 2
        if direct == "right":
            if self.getField(tractor["x"] + 2, tractor["y"]) == "⬜️":
                self.setField(tractor["x"] + 1, tractor["y"], "⬛️")
                self.setField(tractor["x"] + 2, tractor["y"], "⬛️")
            tractor["x"] += 2
        if direct == "up":
            if self.getField(tractor["x"], tractor["y"] - 2) == "⬜️":
                self.setField(tractor["x"], tractor["y"] - 1, "⬛️")
                self.setField(tractor["x"], tractor["y"] - 2, "⬛️")
            tractor["y"] -= 2
        if direct == "down":
            if self.getField(tractor["x"], tractor["y"] + 2) == "⬜️":
                self.setField(tractor["x"], tractor["y"] + 1, "⬛️")
                self.setField(tractor["x"], tractor["y"] + 2, "⬛️")
            tractor["y"] += 2

    def generate_map(self):
        for _ in range(self.rowsNumber):
            row = ["⬜️" for _ in range(self.columnsNumber)]
            self.maze.append(row)

        evenColums = []
        for column in range(self.columnsNumber):
            if self.isEven(column):
                evenColums.append(column)

        startX = 2
        startY = 2

        tractor = {"x": startX, "y": startY}

        self.setField(startX, startY, "⬛️")

        while not self.isMaze():
            self.moveTractor(tractor)

        return self.maze


@loader.tds
class MazeModMod(loader.Module):
    """Module for play maze"""

    strings = {
        "name": "MazeMod",
        "cfg_maze_width": "Maze width and height, default is 30x30",
        "answer": "🕹 <b>Click on the inline buttons to move:</b> <i>{0}</i>",
        "doc": "\n 🟦 - player \n ⬛️ - road\n ⬜️ - wall\n 🟩 - finish\n",
        "move": "▶️ Moved\n",
        "not_allowed": "💭 Not allowed\n",
        "win": "🎉 You win!",
        "error": "❗️ Error!",
    }

    strings_ru = {
        "answer": "🕹 <b>Нажимайте на инлайн кнопки что двигаться:</b> <i>{0}</i>",
        "doc": "\n 🟦 - игрок \n ⬛️ - дорога\n ⬜️ - стена\n 🟩 - финиш\n",
        "move": "▶️ Передвинулся\n",
        "not_allowed": "💭 Не разрешено\n",
        "win": "🎉 Вы победили!",
        "error": "❗️ Ошибка!",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "maze_width",
            "10",
            self.strings["cfg_maze_width"],
        )
        self.name = self.strings["name"]

    async def client_ready(self, client: TelegramClient, db):
        self._db = db
        self._client = client

    async def render(self, message: InlineCall, press, maze, player):
        text = self.strings["answer"].format(self.strings["not_allowed"])
        move = {"x": player["x"], "y": player["y"]}
        if press == "up":
            move["y"] = move["y"] - 1
        if press == "left":
            move["x"] = move["x"] - 1
        if press == "down":
            move["y"] = move["y"] + 1
        if press == "right":
            move["x"] = move["x"] + 1

        if maze[move["y"]][move["x"]] == "⬜":
            pass
        elif maze[move["y"]][move["x"]] == "⬛️":
            maze[player["y"]][player["x"]] = "⬛️"
            player = move
            text = self.strings["answer"].format(self.strings["move"])
        elif maze[move["y"]][move["x"]] == "🟩":
            text = self.strings["win"]
            return await message.edit(text=text)

        maze[player["y"]][player["x"]] = "🟦"

        keyboard = [
            [
                {"text": "🔼", "callback": self.render, "args": ["up", maze, player]},
            ],
            [
                {"text": "◀️", "callback": self.render, "args": ["left", maze, player]},
                {
                    "text": "▶️",
                    "callback": self.render,
                    "args": ["right", maze, player],
                },
            ],
            [
                {"text": "🔽", "callback": self.render, "args": ["down", maze, player]},
            ],
        ]

        for column in maze:
            for row in column:
                for i in row:
                    text = text + i
            text = text + "\n"

        await message.edit(text=text, reply_markup=keyboard)

    @loader.unrestricted
    @loader.ratelimit
    async def mazecmd(self, message):
        """
         - generate maze and start play
        Based on... my code)
        """
        size = int(self.config["maze_width"])
        generate = Maze(size, size)
        maze = generate.generate_map()

        player = {"x": 0, "y": 0}
        maze[player["y"]][player["x"]] = "🟦"
        maze[size - 2][size - 2] = "🟩"

        text = self.strings["answer"].format(self.strings["doc"])
        keyboard = [
            [
                {"text": "🔼", "callback": self.render, "args": ["up", maze, player]},
            ],
            [
                {"text": "◀️", "callback": self.render, "args": ["left", maze, player]},
                {
                    "text": "▶️",
                    "callback": self.render,
                    "args": ["right", maze, player],
                },
            ],
            [
                {
                    "text": "🔽",
                    "callback": self.render,
                    "args": [
                        "down",
                        maze,
                        player,
                    ],
                },
            ],
        ]

        for column in maze:
            for row in column:
                for i in row:
                    text = text + i
            text = text + "\n"

        await message.delete()
        await self.inline.form(
            text=text,
            message=message,
            always_allow=[message.from_id],
            reply_markup=keyboard,
        )
