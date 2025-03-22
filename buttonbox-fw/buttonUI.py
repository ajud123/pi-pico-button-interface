# from ssd1327 import SSD1327_SPI
# from machine import Pin, SPI, mem32
# import framebuf
import sys
# from utime import sleep, sleep_ms, ticks_ms, ticks_diff, time
import random
# import uselect
import math
# import micropython
from settings import Settings

spi = SPI(0, sck=Pin("GP2"), mosi=Pin("GP3"))
res = Pin("GP14")
dc = Pin("GP15")
cs = Pin("GP5")

ssd1327 = SSD1327_SPI(128, 128, spi, dc, res, cs)

# a = bytearray(logo_data.data())

# ssd1327.fill(0)
# ssd1327.blit(fbuf, 0, 0, 0)
# ssd1327.show()

SIE_STATUS=const(0x50110000+0x50)
CONNECTED=const(1<<16)
SUSPENDED=const(1<<4)

def _bounceDVD(x, y, leftright, updown):
    if leftright == 0:
        if x == 0:
            leftright = 1
        else:
            x -= 1
    elif leftright == 1:
        if x == 128-(5*8):
            leftright = 0
        else:
            x += 1
        
    if updown == 0:
            if y == 0:
                updown = 1
            else:
                y -= 1
    elif updown == 1:
        if y == 128-8:
            updown = 0
        else:
            y += 1
    return (x, y, leftright, updown)

class DrawObject:
    def __init__(self, fb: framebuf.FrameBuffer):
        self.fbuf = fb
        pass

    def draw(self):
        pass

class TextObject(DrawObject):
    def __init__(self, fb: framebuf.FrameBuffer, type: int, xPos: int, yPos: int, text: str):
        DrawObject.__init__(self, fb)
        self.type = type
        self.box = self.type == 0x01 or type == 0x03
        if self.box:
            self.boxColor = 0 if type == 0x01 else 12
        self.color = 12 if type == 0x00 or type == 0x01 else 0
        self.x = xPos
        self.y = yPos
        self.text = text

    def draw(self):
        if self.box:
            self.fbuf.rect(self.x, self.y, len(self.text)*8, 8, self.boxColor, True)
        self.fbuf.text(self.text, self.x, self.y, self.color)


class Screen:
    # framebuffer
    a = bytearray(128*128*3)
    fbuf = framebuf.FrameBuffer(a, 128, 128, framebuf.GS4_HMSB)

    # drawing variables
    labels = ["", "", "", "", "", ""]
    topOffset = 0
    bottomOffset = 0

    drawObjects: list = [DrawObject]*128

    @classmethod
    def DrawButtonLabel(cls, index: int, label: str):
        vertPos = (index % 3)
        horPos = math.floor(index / 3)
        offset = 15
        lineOffset = 10
        spacing = math.floor((128-cls.topOffset-cls.bottomOffset)/2)
        x = 0+offset if horPos == 0 else 128-offset
        xL = 0+lineOffset if horPos == 0 else 128-lineOffset
        y = cls.topOffset+spacing*vertPos
        cls.fbuf.text(label, x if horPos == 0 else x - (len(label)*8), y-4, 12)
        cls.fbuf.line(xL, y, 0 if horPos == 0 else 128, y, 12)

    @classmethod
    def GenerateImage(cls):
        cls.fbuf.fill(0)
        for idx in range(len(cls.labels)):
            cls.DrawButtonLabel(idx, cls.labels[idx])
        for drawable in cls.drawObjects:
            drawable.draw(drawable)

def StartBUI():
    leftright = 0
    updown = 0
    x = random.randrange(0, 128-(3*8))
    y = random.randrange(0, 128-8)
    # old_status = SUSPENDED
    # last_ms = time()
    last_time = time()
    spoll = uselect.poll()
    spoll.register(sys.stdin, uselect.POLLIN)
    connected = False

    intrVal = int(Settings.settings["kbd_intr"]) if "kbd_intr" in Settings.settings else 3
    micropython.kbd_intr(intrVal) # WARNING THIS WILL DISABLE STOPPING OF THE PROJECT

    while True:
        # fbuf.fill(0)
        if time() - last_time > 30:
            connected = False
        if connected:
            Screen.GenerateImage()
        ssd1327.fill(0)

        if spoll.poll(0):
            command = sys.stdin.buffer.read(1)
            puredata = ""
            for i in range(len(command)):
                puredata += str(command[i]) + " "
            print("[RECV]: " + str(command[0]) + f"({puredata})")
            # received = bytearray(sys.stdin.buffer.readline())
            if command[0] == 0xFF or command[0] == 0x7E:
                connected = True
            elif command[0] == 0xFE or command[0] == 0x7D:
                print("Received 0xFE or 0x7D, exiting...")
                print(command[0])
                return
            elif command[0] == 0x00: # top button offset
                if spoll.poll(0):
                    data = sys.stdin.buffer.read(1)
                    Screen.topOffset = data[0]
            elif command[0] == 0x01: # bottom button offset
                if spoll.poll(0):
                    data = sys.stdin.buffer.read(1)
                    Screen.bottomOffset = data[0]
            elif command[0] == 0x02:
                index: int = -1
                label: str = ""
                if spoll.poll(0):
                    data = sys.stdin.buffer.read(1)
                    index = data[0] if len(data) > 0 else -1
                    print(f"Label index {index}")
                if spoll.poll(0):
                    data = sys.stdin.buffer.readline()
                    label = data.decode().rstrip()
                    print(f"Label new text {label}")
                Screen.labels[index] = label
            elif command[0] == 0x03:
                pass
            elif command[0] == 0x04: # write text to screen  [index] [type] [x] [y] "text"
                if spoll.poll(0):
                    objIdx: int = sys.stdin.buffer.read(1)[0]
                    if spoll.poll(0):
                        type: int = sys.stdin.buffer.read(1)[0]
                        if spoll.poll(0):
                            xPos: int = sys.stdin.buffer.read(1)[0]
                            if spoll.poll(0):
                                yPos: int = sys.stdin.buffer.read(1)[0]
                                if spoll.poll(0):
                                    data = sys.stdin.buffer.readline()
                                    label = data.decode().rstrip()
                                    Screen.drawObjects[objIdx] = TextObject(Screen.fbuf, type, xPos, yPos, label)

            # if command[0] == 0xFF:
                # connected = True
            # if

            last_time = time()

        # c = (sys.stdin.read(10) if spoll.poll(0) else "")
        # v = sys.stdin.buffer.read(5)
        # print("recv: " + str(c))
        # status = (mem32[SIE_STATUS] & (CONNECTED | SUSPENDED))
        # if status==CONNECTED:
        #     fbuf.text("comfound", x, y, 12)
        #     ssd1327.blit(fbuf, 0, 0, 0)
        #     ssd1327.show()
        #     sleep_ms(1)
            # old_status = status
            # continue
        
        # elif old_status != status and status == SUSPENDED:
            # last_ms = time()
        # fbuf.fill(0)
        # print(str(x) + " " + str(y) + " " + str(leftright) + " " + str(updown))
        # print(time()-last_ms)
        # if time() - last_ms < 60:
        if not connected:
            x, y, leftright, updown = _bounceDVD(x, y, leftright, updown)
            Screen.fbuf.fill(0)
            Screen.fbuf.text("dvd", x, y, 12)
            # ssd1327.fill(0)
        ssd1327.blit(Screen.fbuf, 0, 0, 0)
        ssd1327.show()
        sleep(0.25)
