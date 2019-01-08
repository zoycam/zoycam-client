import asyncio
import base64
import util

"""
def broadcast_msg(imagefile, objects, device, sessionid):
    b = util.fread(imagefile, "rb")
    encoded = base64.b64encode(b).decode('ascii')
    return util.serialize("broadcast", {"sessionid" : sessionid,
                                        "device"    : device,
                                        "image"     : encoded,
                                        "objects"   : objects})
"""
def login_msg(user, password, device):
    return util.serialize("account_login", {"user"   : user,
                                            "pass"   : password,
                                            "device" : device})

async def login_reply(state, payload):
    if "error" in payload and payload["error"] == "ok":
        state["logged"] = True

async def camera_request(state, payload):
    if "src" in payload and "dst" in payload:
        imagefile, objects, ts = state["monitor"].get_latest()
        if imagefile == "": return
        ib      = util.fread(imagefile, "rb")
        encoded = base64.b64encode(ib).decode('ascii')
        msg     = util.serialize("camera_request_done", {"src"       : payload["src"],
                                                         "dst"       : payload["dst"],
                                                         "image"     : encoded,
                                                         "objects"   : objects,
                                                         "timestamp" : ts})
        await state["ws"].send(msg)
