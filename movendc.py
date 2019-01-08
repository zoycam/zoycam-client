import asyncio, base64, websockets, ssl

import cloud, util
from monitor import monitor
from capture import capture

USER    = "john"
PASS    = "doe"
DEVNAME = "device01"

async def cam_worker(state):
    while(state["closed"] == False):
        if(state["logged"] != True):
            await asyncio.sleep(1)
            continue
        ok, imagefile, objects, timestamp = state["camera"].fetch()
        if(imagefile != None and len(imagefile) > 0 and objects > 0):
            state["monitor"].update(imagefile, objects, timestamp)
        await asyncio.sleep(1)

async def login(state):
    if(state["closed"] == True):
        return
    msg = cloud.login_msg(USER, PASS, DEVNAME)
    await state["ws"].send(msg)

async def ws_recv(state):
    commands = { "account_login_reply" : cloud.login_reply,
                 "camera_request"      : cloud.camera_request }
    while(state["closed"] == False):
        try:
            msg = await state["ws"].recv()
            command, payload = util.deserialize(msg)
            if(command in commands): await commands[command](state, payload)
        except websockets.exceptions.ConnectionClosed as e:
            print("connection error: ", e)
            state["closed"] = True
            break
        except:
            print("error")
    print("quitting..")

async def run(camera, loop):
    try:
        state = { "closed"  : False,
                  "camera"  : camera,
                  "logged"  : False,
                  "monitor" : monitor(),
                  "ssl"     : ssl.SSLContext() }
        state["ssl"].verify_mode = ssl.CERT_NONE

        async with websockets.connect(
                'wss://localhost:8443/websocket', ssl=state["ssl"]) as websocket:
            state["ws"] = websocket
            task1 = loop.create_task(cam_worker(state))
            task2 = loop.create_task(ws_recv(state))
            task3 = loop.create_task(login(state))
            await task1
            await task2
            await task3
    except OSError as e:
        print("error: ", e)
    except:
        print("error")

def main():
    camera = capture()
    if camera.init() != 0:
        print("Camera failed")
        exit(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(camera, loop))

main()
