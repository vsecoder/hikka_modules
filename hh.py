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
# meta pic: https://avatars.githubusercontent.com/u/128410002
# meta banner: https://chojuu.vercel.app/api/banner?img=https://avatars.githubusercontent.com/u/128410002&title=HH&description=Hikkahost%20userbot%20manager%20module

import os
import enum
import aiohttp
from aiohttp import ClientConnectorError
from datetime import datetime, timezone
from typing import Union, Optional, Tuple, List, Dict

from .. import loader, utils

__version__ = (2, 0, 0)


FLAGS = {
    "ad": "🇦🇩",  # Андорра
    "ae": "🇦🇪",  # ОАЭ
    "af": "🇦🇫",  # Афганистан
    "ag": "🇦🇬",  # Антигуа и Барбуда
    "ai": "🇦🇮",  # Ангилья
    "al": "🇦🇱",  # Албания
    "am": "🇦🇲",  # Армения
    "ao": "🇦🇴",  # Ангола
    "aq": "🇦🇶",  # Антарктика
    "ar": "🇦🇷",  # Аргентина
    "at": "🇦🇹",  # Австрия
    "au": "🇦🇺",  # Австралия
    "aw": "🇦🇼",  # Аруба
    "ax": "🇦🇽",  # Аландские острова
    "az": "🇦🇿",  # Азербайджан
    "ba": "🇧🇦",  # Босния и Герцеговина
    "bb": "🇧🇧",  # Барбадос
    "bd": "🇧🇩",  # Бангладеш
    "be": "🇧🇪",  # Бельгия
    "bf": "🇧🇫",  # Буркина-Фасо
    "bg": "🇧🇬",  # Болгария
    "bh": "🇧🇭",  # Бахрейн
    "bi": "🇧🇮",  # Бурунди
    "bj": "🇧🇯",  # Бенин
    "bl": "🇧🇱",  # Сен-Бартельми
    "bm": "🇧🇲",  # Бермудские острова
    "bn": "🇧🇳",  # Бруней
    "bo": "🇧🇴",  # Боливия
    "bq": "🇧🇶",  # Бонэйр, Синт-Эстатиус и Саба
    "br": "🇧🇷",  # Бразилия
    "bs": "🇧🇸",  # Багамы
    "bt": "🇧🇹",  # Бутан
    "bv": "🇧🇻",  # остров Буве
    "bw": "🇧🇼",  # Ботсвана
    "by": "🇧🇾",  # Беларусь
    "bz": "🇧🇿",  # Белиз
    "ca": "🇨🇦",  # Канада
    "cc": "🇨🇨",  # Кокосовые (Килинг) острова
    "cd": "🇨🇩",  # Конго - Киншаса
    "cf": "🇨🇫",  # Центральноафриканская Республика
    "cg": "🇨🇬",  # Конго - Браззавиль
    "ch": "🇨🇭",  # Швейцария
    "ci": "🇨🇮",  # Кот-д’Ивуар
    "ck": "🇨🇰",  # Острова Кука
    "cl": "🇨🇱",  # Чили
    "cm": "🇨🇲",  # Камерун
    "cn": "🇨🇳",  # Китай
    "co": "🇨🇴",  # Колумбия
    "cr": "🇨🇷",  # Коста-Рика
    "cu": "🇨🇺",  # Куба
    "cv": "🇨🇻",  # Кабо-Верде
    "cw": "🇨🇼",  # Кюрасао
    "cx": "🇨🇽",  # остров Рождества
    "cy": "🇨🇾",  # Кипр
    "cz": "🇨🇿",  # Чехия
    "de": "🇩🇪",  # Германия
    "dj": "🇩🇯",  # Джибути
    "dk": "🇩🇰",  # Дания
    "dm": "🇩🇲",  # Доминика
    "do": "🇩🇴",  # Доминиканская Республика
    "dz": "🇩🇿",  # Алжир
    "ec": "🇪🇨",  # Эквадор
    "ee": "🇪🇪",  # Эстония
    "eg": "🇪🇬",  # Египет
    "eh": "🇪🇭",  # Западная Сахара
    "er": "🇪🇷",  # Эритрея
    "es": "🇪🇸",  # Испания
    "et": "🇪🇹",  # Эфиопия
    "fi": "🇫🇮",  # Финляндия
    "fj": "🇫🇯",  # Фиджи
    "fk": "🇫🇰",  # Фолклендские острова
    "fm": "🇫🇲",  # Микронезия
    "fo": "🇫🇴",  # Фарерские острова
    "fr": "🇫🇷",  # Франция
    "ga": "🇬🇦",  # Габон
    "gb": "🇬🇧",  # Великобритания
    "gd": "🇬🇩",  # Гренада
    "ge": "🇬🇪",  # Грузия
    "gf": "🇬🇫",  # Французская Гвиана
    "gg": "🇬🇬",  # Гернси
    "gh": "🇬🇭",  # Гана
    "gi": "🇬🇮",  # Гибралтар
    "gl": "🇬🇱",  # Гренландия
    "gm": "🇬🇲",  # Гамбия
    "gn": "🇬🇳",  # Гвинея
    "gp": "🇬🇵",  # Гваделупа
    "gq": "🇬🇶",  # Экваториальная Гвинея
    "gr": "🇬🇷",  # Греция
    "gs": "🇬🇸",  # Южная Георгия и Южные Сандвичевы острова
    "gt": "🇬🇹",  # Гватемала
    "gu": "🇬🇺",  # Гуам
    "gw": "🇬🇼",  # Гвинея-Бисау
    "gy": "🇬🇾",  # Гайана
    "hk": "🇭🇰",  # Гонконг
    "hm": "🇭🇲",  # остров Херд и острова Макдональд
    "hn": "🇭🇳",  # Гондурас
    "hr": "🇭🇷",  # Хорватия
    "ht": "🇭🇹",  # Гаити
    "hu": "🇭🇺",  # Венгрия
    "id": "🇮🇩",  # Индонезия
    "ie": "🇮🇪",  # Ирландия
    "il": "🇮🇱",  # Израиль
    "im": "🇮🇲",  # остров Мэн
    "in": "🇮🇳",  # Индия
    "io": "🇮🇴",  # Британская территория в Индийском океане
    "iq": "🇮🇶",  # Ирак
    "ir": "🇮🇷",  # Иран
    "is": "🇮🇸",  # Исландия
    "it": "🇮🇹",  # Италия
    "je": "🇯🇪",  # Джерси
    "jm": "🇯🇲",  # Ямайка
    "jo": "🇯🇴",  # Иордания
    "jp": "🇯🇵",  # Япония
    "ke": "🇰🇪",  # Кения
    "kg": "🇰🇬",  # Киргизия
    "kh": "🇰🇭",  # Камбоджа
    "ki": "🇰🇮",  # Кирибати
    "km": "🇰🇲",  # Коморы
    "kn": "🇰🇳",  # Сент-Китс и Невис
    "kp": "🇰🇵",  # Корейская Народно-Демократическая Республика
    "kr": "🇰🇷",  # Республика Корея
    "kw": "🇰🇼",  # Кувейт
    "ky": "🇰🇾",  # Каймановы острова
    "kz": "🇰🇿",  # Казахстан
    "la": "🇱🇦",  # Лаос
    "lb": "🇱🇧",  # Ливан
    "lc": "🇱🇨",  # Сент-Люсия
    "li": "🇱🇮",  # Лихтенштейн
    "lk": "🇱🇰",  # Шри-Ланка
    "lr": "🇱🇷",  # Либерия
    "ls": "🇱🇸",  # Лесото
    "lt": "🇱🇹",  # Литва
    "lu": "🇱🇺",  # Люксембург
    "lv": "🇱🇻",  # Латвия
    "ly": "🇱🇾",  # Ливия
    "my": "🇲🇾",
    "md": "🇲🇩",
    "mv": "🇲🇻",
    "mw": "🇲🇼",
    "mx": "🇲🇽",
    "my": "🇲🇾",
    "mz": "🇲🇿",
    "na": "🇳🇦",
    "nc": "🇳🇨",
    "ne": "🇳🇪",
    "nf": "🇳🇫",
    "ng": "🇳🇬",
    "ni": "🇳🇮",
    "nl": "🇳🇱",
    "no": "🇳🇴",
    "np": "🇳🇵",
    "nr": "🇳🇷",
    "nu": "🇳🇺",
    "nz": "🇳🇿",
    "om": "🇴🇲",
    "pa": "🇵🇦",
    "pe": "🇵🇪",
    "pf": "🇵🇫",
    "pg": "🇵🇬",
    "ph": "🇵🇭",
    "pk": "🇵🇰",
    "pl": "🇵🇱",
    "pm": "🇵🇲",
    "pn": "🇵🇳",
    "pr": "🇵🇷",
    "ps": "🇵🇸",
    "pt": "🇵🇹",
    "pw": "🇵🇼",
    "py": "🇵🇾",
    "qa": "🇶🇦",
    "re": "🇷🇪",
    "ro": "🇷🇴",
    "rs": "🇷🇸",
    "ru": "🇷🇺",
    "rw": "🇷🇼",
    "sa": "🇸🇦",
    "sb": "🇸🇧",
    "sc": "🇸🇨",
    "sd": "🇸🇩",
    "se": "🇸🇪",
    "sg": "🇸🇬",
    "sh": "🇸🇭",
    "si": "🇸🇮",
    "sj": "🇸🇯",
    "sk": "🇸🇰",
    "sl": "🇸🇱",
    "sm": "🇸🇲",
    "sn": "🇸🇳",
    "so": "🇸🇴",
    "sr": "🇸🇷",
    "ss": "🇸🇸",
    "st": "🇸🇹",
    "sv": "🇸🇻",
    "sx": "🇸🇽",
    "sy": "🇸🇾",
    "sz": "🇸🇿",
    "tc": "🇹🇨",
    "td": "🇹🇩",
    "tf": "🇹🇫",
    "tg": "🇹🇬",
    "th": "🇹🇭",
    "tj": "🇹🇯",
    "tk": "🇹🇰",
    "tl": "🇹🇱",
    "tm": "🇹🇲",
    "tn": "🇹🇳",
    "to": "🇹🇴",
    "tr": "🇹🇷",
    "tt": "🇹🇹",
    "tv": "🇹🇻",
    "tw": "🇹🇼",
    "tz": "🇹🇿",
    "ua": "🇺🇦",
    "ug": "🇺🇬",
    "um": "🇺🇲",
    "us": "🇺🇸",
    "va": "🇻🇦",
    "vc": "🇻🇨",
    "ve": "🇻🇪",
    "vg": "🇻🇬",
    "vi": "🇻🇮",
    "vn": "🇻🇳",
    "vu": "🇻🇺",
    "wf": "🇼🇫",
    "ws": "🇼🇸",
    "xk": "🇽🇰",
    "ye": "🇾🇪",
    "yt": "🇾🇹",
    "za": "🇿🇦",
    "zm": "🇿🇲",
    "zw": "🇿🇼",
}


class Error(enum.Enum):
    critical = 500
    not_found = 404
    unauthorized = 403
    unknown = 0


class Host:
    def __init__(
        self,
        id: int,
        name: str,
        server_id: int,
        port: int,
        start_date: str,
        end_date: str,
        rate: float,
    ):
        self.id = id
        self.name = name
        self.server_id = server_id
        self.port = port
        self.start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.rate = rate


class API:
    async def _request(
        self,
        url: str,
        method: str = "GET",
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Union[Dict, List[Union[Dict, int]]]:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    method, url, params=params, data=data, headers=headers
                ) as response:
                    if response.status == 200:
                        answer = await response.json()

                        if "status_code" in answer:
                            return [{"detail": answer["detail"]}, answer["status_code"]]

                        return answer if isinstance(answer, dict) else {"data": answer}

                    return [{"detail": await response.text()}, response.status]

            except ClientConnectorError:
                return [{"detail": "Connection error"}, 500]

            except Exception as e:
                return [{"detail": f"Unknown error: {e}"}, 500]


class HostAPI(API):
    def __init__(self, url: str, token: str):
        self.auth_header = {"token": token}
        self._url = f"{url}/api/host"

    async def check_answer(
        self, res: Union[Dict, List]
    ) -> Tuple[bool, Union["Error", Dict]]:
        if isinstance(res, list):
            for error in Error:
                if error.value == res[1]:
                    return False, error

            return False, Error.unknown

        return True, res

    async def get_host(self, user_id: Union[str, int]) -> Union[Host, "Error"]:
        route = f"{self._url}/{user_id}"
        res = await self._request(route, method="GET", headers=self.auth_header)

        answer = await self.check_answer(res)
        if not answer[0]:
            return answer[1]

        host = res["host"]
        return Host(**host)

    async def action(self, user_id, action):
        route = f"{self._url}/{user_id}"
        payload = {"action": action}

        await self._request(
            route,
            method="PUT",
            params=payload,
            headers=self.auth_header,
        )

    async def get_stats(self, user_id) -> Dict:
        return await self._request(
            f"{self._url}/{user_id}/stats", headers=self.auth_header
        )

    async def get_status(self, user_id) -> Dict:
        return await self._request(
            f"{self._url}/{user_id}/status", headers=self.auth_header
        )

    async def get_servers(self) -> List:
        return await self._request(
            "https://api.hikka.host/api/server/get/all-open"
        )

    async def get_logs(
        self, tg_id: Union[str, int], lines: Union[str, int] = "all"
    ) -> Dict:
        route = f"{self._url}/{tg_id}/logs/{lines}"
        return await self._request(route, method="GET", headers=self.auth_header)


@loader.tds
class HHMod(loader.Module):
    """@hikkahost userbot manager module"""

    strings = {
        "name": "HH",
        "info": (
            "<emoji document_id=5413334818047940135>👤</emoji> <b>Info for</b> <code>{id}</code>\n\n"
            "<emoji document_id=5418136591484865679>📶</emoji> <b>Status:</b> {status}\n"
            "<emoji document_id=5415992848753379520>⚙️</emoji> <b>Server:</b> {server}\n"
            "<emoji document_id=5416042764863293485>❤️</emoji> <b>The subscription expires after</b> <code>{days_end} days</code>\n"
            "{stats}\n"
            "{warns}"
        ),
        "logs": "<emoji document_id=5411608069396254249>📄</emoji> All docker container logs from the userbot\n\n<i>In t.me/hikkahost_bot/hhapp logs more readable</i>",
        "stats": "<emoji document_id=5413394354884596702>💾</emoji> <b>Used now:</b> <code>{cpu_percent}%</code> CPU, <code>{memory}MB</code> RAM\n",
        "loading_info": "<emoji document_id=5416094132672156295>⌛️</emoji> Loading...",
        "no_apikey": "<emoji document_id=5411402525146370107>🚫</emoji> Not specified API Key, need get token:\n\n1. Go to the @hikkahost_bot\n2. Send /token\n3. Paste token to .config HH",
        "warn_sub_left": "<emoji document_id=5411402525146370107>🚫</emoji> <i>There are less than 5 days left until the end of the subscription</i>\n",
        "statuses": {
            "running": "🟢",
            "stopped": "🔴",
        },
        "server": "{flag} {name}",
        "not_hh": "Your userbot is not running on hikkahost, please, go to @hikkahost_bot",
        "restart": "<emoji document_id=5418136591484865679>🌘</emoji> Your bot user goes to reboot",
    }

    strings_ru = {
        "name": "HH",
        "info": (
            "<emoji document_id=5413334818047940135>👤</emoji> <b>Информация о</b> <code>{id}</code>\n\n"
            "<emoji document_id=5418136591484865679>📶</emoji> <b>Статус:</b> {status}\n"
            "<emoji document_id=5415992848753379520>⚙️</emoji> <b>Сервер:</b> {server}\n"
            "<emoji document_id=5416042764863293485>❤️</emoji> <b>Подписка истечёт через</b> <code>{days_end} дней</code>\n"
            "{stats}\n"
            "{warns}"
        ),
        "logs": "<emoji document_id=5411608069396254249>📄</emoji> Все логи docker контейнера от hikka\n\n<i>В t.me/hikkahost_bot/hhapp логи более читабельны</i>",
        "stats": "<emoji document_id=5413394354884596702>💾</emoji> <b>Используется:</b> <code>{cpu_percent}%</code> CPU, <code>{memory}MB</code> RAM\n",
        "loading_info": "<emoji document_id=5416094132672156295>⌛️</emoji> Загрузка...",
        "no_apikey": "<emoji document_id=5411402525146370107>🚫</emoji> Не задан ключ API, нужно получить токен:\n\n1. Зайдите в @hikkahost_bot\n2. Отправьте /token\n3. Запишите токен в .config HH",
        "warn_sub_left": "<emoji document_id=5411402525146370107>🚫</emoji> <i>Менее чем через 5 дней подписка истечёт</i>\n",
        "statuses": {
            "running": "🟢",
            "stopped": "🔴",
        },
        "server": "{flag} {name}",
        "not_hh": "Ваш юзербот запущен не через hikkahost, пожалуйста, зайдите в @hikkahost_bot",
        "restart": "<emoji document_id=5418136591484865679>🌘</emoji> Ваш юзербот отправлен в перезагрузку",
    }

    def __init__(self):
        self.name = self.strings["name"]
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "token",
                None,
                validator=loader.validators.Hidden(),
            ),
        )

    async def client_ready(self, client, db):
        self.host = True
        self.url = "https://api.hikka.host"

        if "HIKKAHOST" not in os.environ:
            self.host = False
            await self.inline.bot.send_message(
                self._tg_id, self.strings("not_hh")
            )

        self._client = client
        self._db = db
        self.me = await client.get_me()
        self.bot = "@hikkahost_bot"

    @loader.command(
        en_doc=" - ub status",
    )
    async def hinfocmd(self, message):
        """ - статус юзербота"""
        message = await utils.answer(message, self.strings("loading_info"))

        if self.config["token"] is None:
            await utils.answer(message, self.strings("no_apikey"))
            return

        token = self.config["token"]
        user_id = token.split(":")[0]
        api = HostAPI(self.url, token)

        host = await api.get_host(user_id)

        if isinstance(host, Error):
            await utils.answer(message, str(host))
            return

        status = await api.get_status(user_id)
        stats = (await api.get_stats(user_id))["stats"]
        working = True if status["status"] == "running" else False

        if working:
            cpu_stats = stats["cpu_stats"]
            cpu_total_usage = cpu_stats['cpu_usage']['total_usage']
            system_cpu_usage = cpu_stats['system_cpu_usage']

            ram_usage = round(stats["memory_stats"]["usage"] / (1024 * 1024), 2)
            cpu_percent = round((cpu_total_usage / system_cpu_usage) * 100.0, 2)

            stats = self.strings["stats"].format(
                cpu_percent=cpu_percent, memory=ram_usage
            )
        else:
            stats = ""

        end_date = host.end_date.replace(tzinfo=timezone.utc)
        warns = ""
        days_end = (end_date - datetime.now(timezone.utc)).days
        if days_end < 5:
            warns += self.strings["warn_sub_left"]

        servers = (await api.get_servers())["data"]

        server = servers[host.server_id - 1]
        server = self.strings["server"].format(
            flag=FLAGS[server["country_code"]],
            name=server["name"],
        )

        await utils.answer(
            message,
            self.strings["info"].format(
                id=user_id,
                warns=warns,
                stats=stats,
                server=server,
                days_end=days_end,
                status=self.strings["statuses"][status["status"]],
            ),
        )

    @loader.command(
        en_doc=" - ub logs",
    )
    async def hlogscmd(self, message):
        """ - логи юзербота"""
        if self.config["token"] is None:
            await utils.answer(message, self.strings("no_apikey"))
            return

        token = self.config["token"]
        user_id = token.split(":")[0]
        api = HostAPI(self.url, token)
        data = await api.get_logs(user_id)

        files_log = data["logs"].split("\\r\\n")

        with open("logs.txt", "w") as log_file:
            for log in files_log:
                log_file.write(log + "\n")

        await utils.answer_file(message, "logs.txt", self.strings("logs"))

    @loader.command(
        en_doc=" - ub restart",
    )
    async def hrestartcmd(self, message):
        """ - перезагрузить юзербота"""
        await utils.answer(message, self.strings("restart"))

        if self.config["token"] is None:
            await utils.answer(message, self.strings("no_apikey"))
            return

        token = self.config["token"]
        user_id = token.split(":")[0]
        api = HostAPI(self.url, token)

        data = await api.action(user_id, "restart")

        if isinstance(data, Error):
            await utils.answer(message, str(data))
            return
