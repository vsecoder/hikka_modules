__version__ = (2, 1, 1)

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
# requires: yandex-music aiohttp
# meta desc: Module for yandex music. Based on SpotifyNow, YaNow and WakaTime [beta]
# meta pic: https://img.freepik.com/premium-vector/yandex-music-logo_578229-242.jpg
# meta banner: https://chojuu.vercel.app/api/banner?img=https://img.freepik.com/premium-vector/yandex-music-logo_578229-242.jpg&title=YMNow&description=Module%20for%20yandex%20music

import logging
import asyncio
import logging
import aiohttp
import random
import json
import string
from asyncio import sleep
from yandex_music import ClientAsync
from telethon import TelegramClient
from telethon.tl.types import Message
from telethon.errors.rpcerrorlist import FloodWaitError
from telethon.tl.functions.account import UpdateProfileRequest
from .. import loader, utils  # type: ignore

logger = logging.getLogger(__name__)
logging.getLogger("yandex_music").propagate = False


# https://github.com/FozerG/YandexMusicRPC/blob/main/main.py#L133
async def get_current_track(client, token):
    device_info = {
        "app_name": "Chrome",
        "type": 1,
    }

    ws_proto = {
        "Ynison-Device-Id": "".join(
            [random.choice(string.ascii_lowercase) for _ in range(16)]
        ),
        "Ynison-Device-Info": json.dumps(device_info),
    }

    timeout = aiohttp.ClientTimeout(total=15, connect=10)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.ws_connect(
                url="wss://ynison.music.yandex.ru/redirector.YnisonRedirectService/GetRedirectToYnison",
                headers={
                    "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(ws_proto)}",
                    "Origin": "http://music.yandex.ru",
                    "Authorization": f"OAuth {token}",
                },
                timeout=10,
            ) as ws:
                recv = await ws.receive()
                data = json.loads(recv.data)

            if "redirect_ticket" not in data or "host" not in data:
                print(f"Invalid response structure: {data}")
                return {"success": False}

            new_ws_proto = ws_proto.copy()
            new_ws_proto["Ynison-Redirect-Ticket"] = data["redirect_ticket"]

            to_send = {
                "update_full_state": {
                    "player_state": {
                        "player_queue": {
                            "current_playable_index": -1,
                            "entity_id": "",
                            "entity_type": "VARIOUS",
                            "playable_list": [],
                            "options": {"repeat_mode": "NONE"},
                            "entity_context": "BASED_ON_ENTITY_BY_DEFAULT",
                            "version": {
                                "device_id": ws_proto["Ynison-Device-Id"],
                                "version": 9021243204784341000,
                                "timestamp_ms": 0,
                            },
                            "from_optional": "",
                        },
                        "status": {
                            "duration_ms": 0,
                            "paused": True,
                            "playback_speed": 1,
                            "progress_ms": 0,
                            "version": {
                                "device_id": ws_proto["Ynison-Device-Id"],
                                "version": 8321822175199937000,
                                "timestamp_ms": 0,
                            },
                        },
                    },
                    "device": {
                        "capabilities": {
                            "can_be_player": True,
                            "can_be_remote_controller": False,
                            "volume_granularity": 16,
                        },
                        "info": {
                            "device_id": ws_proto["Ynison-Device-Id"],
                            "type": "WEB",
                            "title": "Chrome Browser",
                            "app_name": "Chrome",
                        },
                        "volume_info": {"volume": 0},
                        "is_shadow": True,
                    },
                    "is_currently_active": False,
                },
                "rid": "ac281c26-a047-4419-ad00-e4fbfda1cba3",
                "player_action_timestamp_ms": 0,
                "activity_interception_type": "DO_NOT_INTERCEPT_BY_DEFAULT",
            }

            async with session.ws_connect(
                url=f"wss://{data['host']}/ynison_state.YnisonStateService/PutYnisonState",
                headers={
                    "Sec-WebSocket-Protocol": f"Bearer, v2, {json.dumps(new_ws_proto)}",
                    "Origin": "http://music.yandex.ru",
                    "Authorization": f"OAuth {token}",
                },
                timeout=10,
                method="GET",
            ) as ws:
                await ws.send_str(json.dumps(to_send))
                recv = await asyncio.wait_for(ws.receive(), timeout=10)
                ynison = json.loads(recv.data)
                track_index = ynison["player_state"]["player_queue"][
                    "current_playable_index"
                ]
                if track_index == -1:
                    print("No track is currently playing.")
                    return {"success": False}
                track = ynison["player_state"]["player_queue"]["playable_list"][
                    track_index
                ]

            await session.close()
            info = await client.tracks_download_info(track["playable_id"], True)
            track = await client.tracks(track["playable_id"])
            res = {
                "paused": ynison["player_state"]["status"]["paused"],
                "duration_ms": ynison["player_state"]["status"]["duration_ms"],
                "progress_ms": ynison["player_state"]["status"]["progress_ms"],
                "entity_id": ynison["player_state"]["player_queue"]["entity_id"],
                "repeat_mode": ynison["player_state"]["player_queue"]["options"][
                    "repeat_mode"
                ],
                "entity_type": ynison["player_state"]["player_queue"]["entity_type"],
                "track": track,
                "info": info,
                "success": True,
            }
            return res

    except Exception as e:
        print(f"Failed to get current track: {str(e)}")
        return {"success": False}


@loader.tds
class YmNowBetaMod(loader.Module):
    """
    Module for yandex music. Based on SpotifyNow, YaNow and WakaTime. [BETA]
    """

    strings = {
        "name": "YmNowBeta",
        "no_token": "<b><emoji document_id=5843952899184398024>🚫</emoji> Specify a token in config!</b>",
        "playing": "<b><emoji document_id=5188705588925702510>🎶</emoji> Now playing: </b><code>{}</code><b> - </b><code>{}</code>\n<b>🕐 {}</b>",
        "no_args": "<b><emoji document_id=5843952899184398024>🚫</emoji> Provide arguments!</b>",
        "tutorial": (
            "ℹ️ <b>To enable widget, send a message to a preffered chat with text"
            " </b><code>{YANDEXMUSIC}</code>"
        ),
        "no_results": "<b><emoji document_id=5285037058220372959>☹️</emoji> No results found :(</b>",
        "autobioe": "<b>🔁 Autobio enabled</b>",
        "autobiod": "<b>🔁 Autobio disabled</b>",
        "_cfg_yandexmusictoken": "Yandex.Music account token",
        "_cfg_autobiotemplate": "Template for AutoBio",
        "_cfg_automesgtemplate": "Template for AutoMessage",
        "_cfg_update_interval": "Update interval",
        "no_lyrics": "<b><emoji document_id=5843952899184398024>🚫</emoji> Track doesn't have lyrics.</b>",
        "guide": (
            '<a href="https://github.com/MarshalX/yandex-music-api/discussions/513#discussioncomment-2729781">'
            "Instructions for obtaining a Yandex.Music token</a>"
        ),
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "YandexMusicToken",
                None,
                lambda: self.strings["_cfg_yandexmusictoken"],
                validator=loader.validators.Hidden(),
            ),
            loader.ConfigValue(
                "AutoBioTemplate",
                "🎧 {}",
                lambda: self.strings["_cfg_autobiotemplate"],
                validator=loader.validators.String(),
            ),
        )

    async def on_dlmod(self):
        if not self.get("guide_send", False):
            await self.inline.bot.send_message(
                self._tg_id,
                self.strings["guide"],
            )
            self.set("guide_send", True)

    async def client_ready(self, client: TelegramClient, db):
        self.client = client
        self.db = db
        self._premium = getattr(await self.client.get_me(), "premium", False)
        if self.get("autobio", False):
            self.autobio.start()

    @loader.command()
    async def ynowcmd(self, message: Message):
        """Get now playing track"""

        if not self.config["YandexMusicToken"]:
            await utils.answer(message, self.strings["no_token"])
            return

        try:
            client = ClientAsync(self.config["YandexMusicToken"])
            await client.init()
        except:  # noqa: E722
            await utils.answer(message, self.strings["no_token"])
            return

        res = await get_current_track(client, self.config["YandexMusicToken"])

        track = res["track"]

        if not track:
            await utils.answer(message, self.strings["no_results"])
            return

        track = track[0] # type: ignore

        link = res["info"][0]["direct_link"] # type: ignore
        title = track["title"]
        artists = [artist["name"] for artist in track["artists"]]
        duration_ms = int(track["duration_ms"])

        caption = self.strings["playing"].format(
            utils.escape_html(", ".join(artists)),
            utils.escape_html(title),
            f"{duration_ms // 1000 // 60:02}:{duration_ms // 1000 % 60:02}",
        )
        lnk = track["id"]

        await self.inline.form(
            message=message,
            text=caption,
            reply_markup={
                "text": "song.link",
                "url": f"https://song.link/ya/{lnk}",
            },
            silent=True,
            audio={
                "url": link,
                "title": utils.escape_html(title),
                "performer": utils.escape_html(", ".join(artists)),
            },
        )

    @loader.command()
    async def ybio(self, message: Message):
        """Show now playing track in your bio"""

        if not self.config["YandexMusicToken"]:
            await utils.answer(message, self.strings["no_token"])
            return

        try:
            client = ClientAsync(self.config["YandexMusicToken"])
            await client.init()
        except:
            await utils.answer(message, self.strings["no_token"])
            return

        current = self.get("autobio", False)
        new = not current
        self.set("autobio", new)

        if new:
            await utils.answer(message, self.strings["autobioe"])
            self.autobio.start()
        else:
            await utils.answer(message, self.strings["autobiod"])
            self.autobio.stop()

    @loader.loop(interval=60)
    async def autobio(self):
        client = ClientAsync(self.config["YandexMusicToken"])

        await client.init()

        res = await get_current_track(client, self.config["YandexMusicToken"])

        track = res["track"]

        track = track[0]  # type: ignore

        title = track["title"]
        artists = [artist["name"] for artist in track["artists"]]
        duration_ms = int(track["duration_ms"])

        text = self.config["AutoBioTemplate"].format(
            f"{', '.join(artists)} - {title} | {duration_ms // 1000 // 60:02}:{duration_ms // 1000 % 60:02}",
        )

        try:
            await self.client(
                UpdateProfileRequest(about=text[: 140 if self._premium else 70])
            )
        except FloodWaitError as e:
            logger.info(f"Sleeping {e.seconds}")
            await sleep(e.seconds)
            return
