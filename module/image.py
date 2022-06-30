import asyncio
import function_pattern_matching as fpm
from schema import Schema
import base64
import aiofiles
import json

from module import Module
from capture import capture


class ModuleImage(Module):
    def __init__(self, state):
        super().__init__(state)

    def init_schema(self):
        self.schema = Schema({
            "name": "Image",
            "active": bool,
            "deps": list,
            "camera_id": int,
            "processing": str,
        })

    async def loop(self, wsclient, cap):
        ok, imagefile, objects, timestamp = cap.fetch()
        if(imagefile != None and len(imagefile) > 0):
            async with aiofiles.open(imagefile, mode="rb") as f:
                contents = await f.read()

            encoded = base64.b64encode(contents)
            s = {
                "event": "data",
                "type": "Image",
                "value": encoded.decode("utf-8")
            }

            if wsclient.ws:
                await wsclient.ws.send(json.dumps(s))
            else:
                print("Data not sent yet")

        await asyncio.sleep(5)
        asyncio.ensure_future(self.loop(wsclient, cap))

    @fpm.case
    @fpm.guard
    async def fire(self: fpm._, data: fpm._,  version: fpm.eq("1")):
        cap = capture()
        cap.init()
        wsclient = self.get_module(data["deps"][0])
        await self.loop(wsclient, cap)
