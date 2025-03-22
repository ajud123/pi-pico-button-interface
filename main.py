import json
import os
from importlib.machinery import SourceFileLoader
import asyncio
import argparse
import time

# import serial
import serial_asyncio

from serialmgr import SerialManager

class DataProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        # print('port opened', transport)
        # self.transport.write(b'\xFF')
        # transport.serial.rts = False  # You can manipulate Serial object via transport
        # transport.write(b'Hello, World!\n')  # Write serial data via transport

    def load_params(self, handler, screenCount, redrawHandler):
        self.handle_input = handler
        self.screenCount = screenCount
        self.currentScreen = 0
        self.redrawHandler = redrawHandler
        pass

    def data_received(self, data):  
        if data[0] == 0:
            # print('input data received', repr(data))
            bank = data[1]
            button = data[2]
            state = data[3] 
            rotation = data[4] if len(data) > 4 else 0
            if button != 3:
                # asyncio.create_task(self.handle_input(bank, button, state))
                self.handle_input(bank, button, state, rotation)
            elif state == 2:
                self.currentScreen = (self.currentScreen + (1 if bank == 0 else -1)) % self.screenCount
                self.transport.write(bytes([0xFE]))
                self.redrawHandler()

        else:
            print('unknown data received', repr(data))
        # if b'\n' in data:
            # self.transport.close()

    def write(self, data): # use b'{datahere}' for input
        self.transport.write(data)  # Write serial data via transport

    def connection_lost(self, exc):
        print('port closed')
        self.transport.loop.stop()

    def pause_writing(self):
        print('pause writing')
        print(self.transport.get_write_buffer_size())

    def resume_writing(self):
        print(self.transport.get_write_buffer_size())
        print('resume writing')

    def pause_reading(self):
        # This will stop the callbacks to data_received
        self.transport.pause_reading()

    def resume_reading(self):
        # This will start the callbacks to data_received again with all data that has been received in the meantime.
        self.transport.resume_reading()




async def initializeModules(modules, callback, transport, protocol):
    fullInit = True
    for i in range(len(modules)):
        try:
            lTransport = LimitedTransport(transport, protocol, i)
            await modules[i]["module"].init(callback, lTransport)
        except Exception as ex:
            print(f"Failed to initialize module {modules[i]["name"]} {ex}")        
            fullInit = False

    # for module in modules:
    #     try:
    #         await module["module"].init(callback, transport)
    #     except Exception as ex:
    #         print(f"Failed to initialize module {module["name"]} {ex}")        
    #         fullInit = False
    return fullInit

class LimitedTransport:
    def __init__(self, transport: serial_asyncio.SerialTransport, protocol: DataProtocol, id: int):
        self.transport = transport
        self.protocol = protocol
        self.id = id
        pass

    def write(self, data):
        if self.protocol.currentScreen == self.id:
            self.transport.write(data)

currentModule = 0

async def main(emulated):
    loaded = []

    print("Raspberry Pi Pico Button box interface starting")

    with open('modules.json', 'r') as f:
        modules = json.load(f)
        for module in modules:
            if not module.endswith(".py"):
                module += ".py"
            fullpath = os.path.join('modules', module)
            print(f"Loading module from {fullpath}")
            imported = SourceFileLoader(module.replace(".py", ""), fullpath).load_module()
            loaded.append({"name": module.replace(".py", ""), "module": imported})

    if emulated:
        from emulator import Emulator, EmulatorTransport
        Emulator.Start()
        loop = asyncio.get_running_loop()
        # coro = serial_asyncio.create_serial_connection(loop, None, '/dev/ttyUSB0', baudrate=115200)
        coro = DataProtocol()
        coro.connection_made(EmulatorTransport())
        await asyncio.sleep(1)
        coro.write_to_rpi(b"\x02\x01Amogus")
        coro.write_to_rpi(b"\x03\x00"+(64).to_bytes()+(64).to_bytes()+b"test1")
        coro.write_to_rpi(b"\x03\x01"+(64).to_bytes()+(32).to_bytes()+b"test2")
        # transport, protocol = loop.create_task(coro)
        # Emulator.Stop()
    else:
        print("should be using serial")
        loop = asyncio.get_running_loop()
        transport, protocol = await serial_asyncio.create_serial_connection(loop, DataProtocol, '/dev/ttyACM1', baudrate=115200)

        def cb(changes, id):
            for changed, variant in changes.items():
                print(f'[{id}] property changed: {changed} - {variant.value}')
                print(transport)

        success = await initializeModules(loaded, cb, transport, protocol)
        print("All modules initialized." if success else "Failed to initialize all modules.")

        def inputHandler(bank, button, state, rotation):
            loaded[protocol.currentScreen]["module"].handleInput(bank, button, state, rotation)

        def redrawHandler():
            loaded[protocol.currentScreen]["module"].redraw()

        protocol.load_params(inputHandler, len(loaded), redrawHandler)
        # await asyncio.sleep(10)
        # time.sleep(10)
        # protocol.write_to_rpi(b"\xFF")
        # transport, protocol = loop.create_task(coro)
        transport.write(bytes([0xFF]))
        transport.write(bytes([0x00, 10]))
        transport.write(bytes([0x01, 10]))
        # transport.write(b"\x02\x001\n")
        # transport.write(b"\x02\x012\n")
        # transport.write(b"\x02\x023\n")
        # transport.write(b"\x02\x031\n")
        # transport.write(b"\x02\x042\n")
        # transport.write(b"\x02\x053\n")
        # transport.write(b"\x04\x00\x00"+(64-8*3).to_bytes()+(10).to_bytes()+b"\x00\x00omg\n")
        # transport.write(b"\x04\x01\x01"+(64-8*3).to_bytes()+(20).to_bytes()+b"\xFF\x00omg\n")
        # transport.write(b"\x04\x02\x02"+(64-8*3).to_bytes()+(30).to_bytes()+b"\x00\x00omg\n")
        # transport.write(b"\x04\x03\x03"+(64-8*3).to_bytes()+(40).to_bytes()+b"\x00\x00omg\n")
        dataTransport = transport
        # protocol.write_to_rpi(b"\x03\x00"+(64).to_bytes()+(64).to_bytes()+b"xd")
        # protocol.write_to_rpi(b"\x03\x01"+(64).to_bytes()+(32).to_bytes()+b"omg")






if __name__ == "__main__":
    parser = argparse.ArgumentParser("simple_example")
    parser.add_argument("--emulated", "-e", help="Connects to an emulated interface.", required=False, action="store_true")
    args = parser.parse_args()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(main(args.emulated))
    loop.run_forever()


    # loop.run_until_complete(main())