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
# meta pic: https://img.icons8.com/fluency/344/timer.png
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.icons8.com/fluency/344/timer.png&title=Account%20Time&description=Get%20the%20account%20registration%20date%20and%20time!

__version__ = (2, 5, 0)

import logging
import asyncio
from typing import Callable, Tuple
import time
from dateutil.relativedelta import relativedelta
import numpy as np
from datetime import datetime
from .. import loader, utils  # type: ignore

data = {
    "1000000": 1380326400,
    "2768409": 1383264000,
    "7679610": 1388448000,
    "11538514": 1391212000,
    "15835244": 1392940000,
    "23646077": 1393459000,
    "38015510": 1393632000,
    "44634663": 1399334000,
    "46145305": 1400198000,
    "54845238": 1411257000,
    "63263518": 1414454000,
    "101260938": 1425600000,
    "101323197": 1426204000,
    "111220210": 1429574000,
    "103258382": 1432771000,
    "103151531": 1433376000,
    "116812045": 1437696000,
    "122600695": 1437782000,
    "109393468": 1439078000,
    "112594714": 1439683000,
    "124872445": 1439856000,
    "130029930": 1441324000,
    "125828524": 1444003000,
    "133909606": 1444176000,
    "157242073": 1446768000,
    "143445125": 1448928000,
    "148670295": 1452211000,
    "152079341": 1453420000,
    "171295414": 1457481000,
    "181783990": 1460246000,
    "222021233": 1465344000,
    "225034354": 1466208000,
    "278941742": 1473465000,
    "285253072": 1476835000,
    "294851037": 1479600000,
    "297621225": 1481846000,
    "328594461": 1482969000,
    "337808429": 1487707000,
    "341546272": 1487782000,
    "352940995": 1487894000,
    "369669043": 1490918000,
    "400169472": 1501459000,
    "616816630": 1529625600,
    "727572658": 1543708800,
    "782000000": 1546300800,
    "925078064": 1563290000,
    "1974255900": 1634000000,
    "3318845111": 1618028800,
    "4317845111": 1620028800,
    "5336336790": 1646368100,
    "5396587273": 1648014800,
    "6020888206": 1675534800,
    "6057123350": 1676198350,
    "6554264430": 1695654800,
}


class Function:
    def __init__(self, order: int = 3):
        self.order = 3

        self.x, self.y = self._unpack_data()
        self._func = self._fit_data()

    def _unpack_data(self) -> Tuple[list, list]:
        x_data = np.array(list(map(int, data.keys())))
        y_data = np.array(list(data.values()))

        return (x_data, y_data)

    def _fit_data(self) -> Callable[[int], int]:
        fitted = np.polyfit(self.x, self.y, self.order)
        return np.poly1d(fitted)

    def add_datapoint(self, pair: tuple):
        pair[0] = str(pair[0])

        data.update([pair])

        # update the model with new data
        # self.x, self.y = self._unpack_data()
        self._func = self._fit_data()

    def func(self, tg_id: int) -> int:
        value = self._func(tg_id)
        current = time.time()

        if value > current:
            value = current

        return value


logger = logging.getLogger(__name__)


@loader.tds
class AcTimeMod(loader.Module):
    """Module for get account time"""

    strings = {
        "name": "Account Time",
        "info": "Get the account registration date and time!",
        "error": "Error!",
        "answer": (
            "⏳ This account: {0}\n🕰 A registered: {1}\n\nP.S. The module script is"
            " trained with the number of requests from different ids, so the data can"
            " be refined"
        ),
    }

    strings_ru = {
        "info": "Узнай дату регистрации аккаунта, и время, которое вы его используете!",
        "error": "Ошибка!",
    }

    def __init__(self):
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self.client = client
        self.db = db

    def time_format(self, unix_time: int, fmt="%Y-%m-%d") -> list:
        result = [str(datetime.utcfromtimestamp(unix_time).strftime(fmt))]

        d = relativedelta(datetime.now(), datetime.utcfromtimestamp(unix_time))
        result.append(f"{d.years} years, {d.months} months, {d.days} days")

        return result

    @loader.unrestricted
    @loader.ratelimit
    async def actimecmd(self, message):
        """
         - get the account registration date and time [beta]
        P.S. You can also send a command in response to a message
        """
        try:
            interpolation = Function()
            reply = await message.get_reply_message()

            if reply:
                date = self.time_format(
                    unix_time=round(interpolation.func(int(reply.sender.id)))
                )
            else:
                date = self.time_format(
                    unix_time=round(interpolation.func(int(message.from_id)))
                )

            await utils.answer(message, self.strings["answer"].format(date[0], date[1]))
        except Exception as e:
            await utils.answer(message, f'{self.strings["error"]}\n\n{e}')
            if message.out:
                await asyncio.sleep(5)
                await message.delete()
