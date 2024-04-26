"""
                              _
__   _____  ___  ___ ___   __| | ___ _ __
\ \ / / __|/ _ \/ __/ _ \ / _` |/ _ \ '__|
 \ V /\__ \  __/ (_| (_) | (_| |  __/ |
  \_/ |___/\___|\___\___/ \__,_|\___|_|

  Copyleft 2022 t.me/vsecoder
  This program is free software; you can redistribute it and/or modify

  Thk @fleef
"""

import contextlib

# meta developer: @vsecoder_m
# meta pic: https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCO9v08B8wLGwL4UMxZzlf7tNOvsRvWQjMypjq5uyvxhAa03NbOO40DY1m-Rr4aYeK7WE&usqp=CAU
# meta banner: https://chojuu.vercel.app/api/banner?img=https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSCO9v08B8wLGwL4UMxZzlf7tNOvsRvWQjMypjq5uyvxhAa03NbOO40DY1m-Rr4aYeK7WE&usqp=CAU&title=SearX&description=Telegram%20SearX%20Engine


__version__ = (1, 0, 1)

import logging
import json
import urllib3

from datetime import datetime

from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)

with contextlib.suppress(Exception):
    urllib3.disable_warnings()

engines = (
    "bing_images",
    "mediawiki",
    "searchcode_code",
    "yahoo_news",
    "semantic_scholar",
    "btdigg",
    "nyaa",
    "1337x",
    "bing_news",
    "reddit",
    "startpage",
    "apkmirror",
    "bandcamp",
    "genius",
    "wolframalpha_noapi",
    "torrentz",
    "youtube_noapi",
    "archlinux",
    "vimeo",
    "sepiasearch",
    "fdroid",
    "piratebay",
    "soundcloud",
    "bing",
    "frinkiac",
    "ina",
    "google_videos",
    "openstreetmap",
    "pdbe",
    "rumble",
    "openverse",
    "ebay",
    "tvmaze",
    "mediathekviewweb",
    "onesearch",
    "mixcloud",
    "duckduckgo",
    "bing_videos",
    "duckduckgo_images",
    "pubmed",
    "yahoo",
    "github",
    "microsoft_academic",
    "digg",
    "google_images",
    "tineye",
    "google_scholar",
    "framalibre",
    "duckduckgo_definitions",
    "xpath",
    "currency_convert",
    "gentoo",
    "translated",
    "unsplash",
    "json_engine",
    "invidious",
    "google",
    "kickass",
    "etools",
    "dictzone",
    "photon",
    "yggtorrent",
    "deezer",
    "duden",
    "seznam",
    "gigablast",
    "deviantart",
    "wikidata",
    "tokyotoshokan",
    "flickr_noapi",
    "peertube",
    "qwant",
    "stackexchange",
    "imdb",
    "wordnik",
    "loc",
    "www1x",
    "solidtorrents",
    "google_news",
    "sjp",
    "wikipedia",
    "dailymotion",
    "arxiv",
    "yandex",
)

engines_str = "| "
for engine in engines:
    engines_str += f"{engine} | "


@loader.tds
class SearXMod(loader.Module):
    """Module for multi search"""

    strings = {
        "name": "SearX",
        "cfg_engine": f"Search engine, all: \n{engines_str}",
        "cfg_searx_link": "SearX link, get from https://searx.space/",
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Error: \n{}",
        "loading": "<emoji document_id=5381942305081010778>⏳</emoji> Loading...",
    }

    strings_ru = {
        "cfg_engine": f"Поисковик, все: \n{engines_str}",
        "cfg_searx_link": "Ссылка на SearX, получить можно на https://searx.space/",
        "error": "<emoji document_id=5467928559664242360>❗️</emoji> Ошибка: \n{}",
        "loading": "<emoji document_id=5381942305081010778>⏳</emoji> Загрузка...",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "engine",
                "duckduckgo",
                self.strings["cfg_engine"],
                validator=loader.validators.String(),
            ),
            loader.ConfigValue(
                "searx_link",
                "https://searx.thegpm.org/",
                self.strings["cfg_searx_link"],
                validator=loader.validators.Link(),
            ),
        )

    async def request(
        self, session, query: str, engine: str = "yandex", count_results: int = 3
    ):
        if engine not in engines:
            return self.strings["error"].format("This engine is not found")
        if not query:
            return self.strings["error"].format("Specify a request")

        def_params = dict(
            category_general="1",
            q=query,
            language="ru-RU",
            format="json",
            engines=engine,
        )

        url = self.config["searx_link"]

        start_time = datetime.now()

        raw_results = json.loads(
            session.request("GET", url, fields={**def_params}).data.decode("UTF-8")
        )["results"]

        len_raw_result = len(raw_results)
        raw_results = (
            raw_results[:2]
            if len_raw_result < count_results
            else raw_results[:count_results]
        )

        pretty_result = "".join(
            f" 💡: <i>{result['title']}</i>\n 🔗: {result['url']}\n\n"
            for result in raw_results
        )

        return (
            f"📟 <b>{engine}</b>\n\n{pretty_result}\n⏱: {datetime.now() - start_time}"
        )

    async def client_ready(self, client, db):
        self._client = client

    async def searxcmd(self, message):
        """
         {text} - search text in the internet

        Based on SearX and t.me/fleef code
        """
        args = utils.get_args_raw(message).split("&")

        await utils.answer(message, self.strings["loading"])
        session = urllib3.PoolManager()
        result = await self.request(session, args[0], self.config["engine"], 3)
        await utils.answer(message, result)
