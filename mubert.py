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
# meta pic: https://img.icons8.com/cotton/344/musical-notes.png

__version__ = (2, 0, 0)

import time
import logging
import json
import httpx
from .. import loader, utils

logger = logging.getLogger(__name__)


@loader.tds
class MubertMod(loader.Module):
    """
    🎵 Module for generate AI music
    """

    strings = {
        "name": "Mubert"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            "token",
            "",
            "Token, generate as command .muberttoken"
        )
        self.name = self.strings["name"]

    async def client_ready(self, client, db):
        self._client = client

    async def muberttokencmd(self, message):
        """
        {email} - get personal access token in Mubert and define API methods
        """
        args = utils.get_args_raw(message)
        email = args

        if args:
            r = httpx.post('https://api-b2b.mubert.com/v2/GetServiceAccess', 
                json={
                    "method":"GetServiceAccess",
                    "params": {
                        "email": email,
                        "license":"ttmmubertlicense#f0acYBenRcfeFpNT4wpYGaTQIyDI4mJGv5MfIhBFz97NXDwDNFHmMRsBSzmGsJwbTpP1A6i07AXcIeAHo5",
                        "token":"4951f6428e83172a4f39de05d5b3ab10d58560b8",
                        "mode": "loop"
                    }
                }
            )

            rdata = json.loads(r.text)
            #logger.info(rdata)

            # "probably incorrect e-mail"
            if rdata['status'] != 1:
                return await message.edit(rdata['error']['text'])

            pat = rdata['data']['pat']
            self.config["token"] = pat
            await message.edit("Token saved!")
        else:
            await message.edit("You need to specify the token!")

    async def mubertcmd(self, message):
        """
        {tags} - tags as generate music
        """
        args = utils.get_args_raw(message)
        tags = args.split(' ')

        if not tags:
            return await message.edit("You need to specify tags!")

        if len(tags) >= 3:
            tags = ['downtempo', 'agender', 'dub']
        else:
            tags = ['sad', 'world music', 'orchestral']

        if not self.config["token"]:
            return await message.edit("You need to specify the token, .muberttoken {email}!")

        maxit = 10
        r = httpx.post('https://api-b2b.mubert.com/v2/RecordTrackTTM', 
            json={
                "method":"RecordTrackTTM",
                "params": {
                    "pat": self.config["token"], 
                    "duration": 60,
                    "tags": tags,
                    "mode": 'track'
                }
            }
        )

        rdata = json.loads(r.text)
        #logger.info(rdata)
        if rdata['status'] != 1:
            return await message.edit(rdata['error']['text'])

        trackurl = rdata['data']['tasks'][0]['download_link']

        for i in range(maxit):
            time.sleep(1)
            await message.edit(f"Generating track {i+1}/{maxit}")

        await message.edit(f"Generated track: {trackurl}")
        await message.client.send_file(message.to_id, trackurl, text=str(trackurl), reply_to=message.id, voice_note=False)