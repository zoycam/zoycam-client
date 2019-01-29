import asyncio, base64, websockets, json, ssl, sys

import cloud, util
from mlog import mlog
from monitor import monitor
from capture import capture

def get_config():
    filename = "config/zoycam.cfg"
    if(len(sys.argv) == 2):
        filename = sys.argv[1]
    c = util.fread(filename, "r")
    return json.loads(c)

async def cam_worker(state):
    while(state["closed"] == False):
        if(state["logged"] != True):
            await asyncio.sleep(1)
            continue
        ok, imagefile, objects, timestamp = state["camera"].fetch()
        if(imagefile != None and len(imagefile) > 0 and objects > 0):
            mlog.debug("Broadcast objects: %d" % objects)
            state["monitor"].update(imagefile, objects, timestamp)
            await cloud.broadcast(state)
        await asyncio.sleep(1)

async def login(state, cfg):
    if(state["closed"] == True):
        return
    msg = cloud.login_msg(cfg["user"], cfg["pass"], cfg["device"])
    mlog.debug("Attempt to login")
    await state["ws"].send(msg)

async def ws_recv(state):
    commands = { "account_login_reply" : cloud.login_reply,
                 "camera_request"      : cloud.camera_request,
                 "camera_reinit"       : cloud.camera_reinit }
    while(state["closed"] == False):
        try:
            msg = await state["ws"].recv()
            mlog.debug("Received: %d bytes" % len(msg))
            command, payload = util.deserialize(msg)
            if(command in commands): await commands[command](state, payload)
        except websockets.exceptions.ConnectionClosed as e:
            mlog.error("Connection error: " + e)
            state["closed"] = True
            break
        except:
            mlog.warning("Received unsupported message ")
    mlog.debug("Leaving..")

async def run(camera, loop):
    try:
        cfg = get_config()
        state = { "closed"  : False,
                  "camera"  : camera,
                  "logged"  : False,
                  "monitor" : monitor(cfg["camera"]),
                  "ssl"     : ssl.SSLContext() }
        state["ssl"].verify_mode = ssl.CERT_NONE
        state["camera"].setnode(cfg["camera"])

        async with websockets.connect(
                'wss://'+cfg["host"]+'/websocket', ssl=state["ssl"]) as websocket:
            state["ws"] = websocket
            task1 = loop.create_task(cam_worker(state))
            task2 = loop.create_task(ws_recv(state))
            task3 = loop.create_task(login(state, cfg))
            await task1
            await task2
            await task3
    except OSError as e:
        raise("Exception: ", e)

def main():
    camera = capture()
    if(camera.init() != 0):
        mlog.error("Camera failed")
        exit(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(camera, loop))

main()
