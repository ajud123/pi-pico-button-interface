# follow this to install pygobject: https://pygobject.gnome.org/getting_started.html
import asyncio
from typing import Any, Callable
from evdev import uinput, ecodes as e
from main import DataProtocol

async def keepAlive(transport: DataProtocol):
    while True:
        await asyncio.sleep(1)
    pass

def getFirstSource(dict):
    for key in dict:
        return key
    return ""

async def init(propertyChangedCallback: Callable[[Any, str], Any], transport: DataProtocol):
    print("keyboard initialised")
    loop = asyncio.get_running_loop()
    task = loop.create_task(keepAlive(transport))
    return

# cat /usr/include/linux/input-event-codes.h

def handleInput(bank, button, state, rotation):
    if button == 0 and state == 2 and bank == 0:
        with uinput.UInput() as ui:
            # ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
            ui.write(e.EV_KEY, e.KEY_F14, 1)
            ui.syn()
    if button == 1 and state == 2 and bank == 0:
        with uinput.UInput() as ui:
            # ui.write(e.EV_KEY, e.KEY_LEFTSHIFT, 1)
            ui.write(e.EV_KEY, e.KEY_F15, 1)
            ui.syn()
    pass

def redraw():
    pass

def stop():
    pass