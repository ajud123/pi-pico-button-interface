import asyncio
import serial_asyncio
import serial.tools.list_ports
import serial
import serial_asyncio

class DataProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        # print('port opened', transport)
        # self.transport.write(b'\xFF')
        # transport.serial.rts = False  # You can manipulate Serial object via transport
        # transport.write(b'Hello, World!\n')  # Write serial data via transport

    def load_params(self, handler, screenCount, redrawHandler, connectionLostHandler):
        self.handle_input = handler
        self.screenCount = screenCount
        self.currentScreen = 0
        self.redrawHandler = redrawHandler
        self.connectionLostHandler = connectionLostHandler
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
        self.connectionLostHandler()
        # self.transport.loop.stop()

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

class LimitedTransport:
    def __init__(self, transport: serial_asyncio.SerialTransport, protocol: DataProtocol, id: int):
        self.transport = transport
        self.protocol = protocol
        self.id = id
        pass

    def write(self, data):
        if self.protocol.currentScreen == self.id:
            self.transport.write(data)

class SerialManager:
    def GetPorts():
        return serial.tools.list_ports.comports()
    
    async def Connect(port, baudrate) -> tuple[serial_asyncio.SerialTransport, DataProtocol]:
        loop = asyncio.get_running_loop()
        transport, protocol = await serial_asyncio.create_serial_connection(loop, DataProtocol, port, baudrate=baudrate)
        return transport, protocol
    
    pass
