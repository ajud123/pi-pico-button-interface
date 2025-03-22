from importlib.machinery import SourceFileLoader
from serialmgr import SerialManager
import os
from serialmgr import LimitedTransport
from asyncio.events import get_event_loop
import asyncio

class ButtonBoxManager:
    modules = []
    _loaded = []
    _initialized = []
    _transport = None
    hasConnection = False

    async def Start(port, baudrate = 115200):
        transport, protocol = await SerialManager.Connect(port, baudrate)
        ButtonBoxManager.hasConnection = True

        def cb(changes, id):
            for changed, variant in changes.items():
                print(f'[{id}] property changed: {changed} - {variant.value}')
                print(transport)

        loadedModules = ButtonBoxManager.LoadModules()
        ButtonBoxManager._loaded = loadedModules

        success = await ButtonBoxManager.initializeModules(loadedModules, cb, transport, protocol)
        print("All modules initialized." if success else "Failed to initialize all modules.")

        def inputHandler(bank, button, state, rotation):
            loadedModules[protocol.currentScreen]["module"].handleInput(bank, button, state, rotation)

        def redrawHandler():
            loadedModules[protocol.currentScreen]["module"].redraw()

        def connLost():
            ButtonBoxManager.hasConnection = False

        protocol.load_params(inputHandler, len(loadedModules), redrawHandler, connLost)

        transport.write(bytes([0xFF]))
        transport.write(bytes([0x00, 10]))
        transport.write(bytes([0x01, 10]))
        ButtonBoxManager._transport = transport
        
    def Stop():
        if ButtonBoxManager._transport != None:
            if ButtonBoxManager.hasConnection:
                ButtonBoxManager._transport.abort()
            ButtonBoxManager._transport = None
        if len(ButtonBoxManager._initialized) > 0:
            for i in ButtonBoxManager._initialized:
                ButtonBoxManager._loaded[i]["module"].stop()
            ButtonBoxManager._initialized = []

    def LoadModules():
        loaded = []
        for module in ButtonBoxManager.modules:
            fullpath = os.path.join('modules', module)
            print(f"Loading module from {fullpath}")
            imported = SourceFileLoader(module.replace(".py", ""), fullpath).load_module()
            loaded.append({"name": module.replace(".py", ""), "module": imported})
        return loaded
    pass

    async def initializeModules(modules, callback, transport, protocol):
        fullInit = True
        for i in range(len(modules)):
            try:
                lTransport = LimitedTransport(transport, protocol, i)
                await modules[i]["module"].init(callback, lTransport)
                ButtonBoxManager._initialized.append(i)
            except Exception as ex:
                print(f"Failed to initialize module {modules[i]["name"]} {ex}")        
                fullInit = False

        return fullInit