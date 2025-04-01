# from ssd1327 import SSD1327_SPI
# from machine import Pin, SPI, mem32
# import framebuf
# import sys
# from utime import sleep, sleep_ms, ticks_ms, ticks_diff, time
import random
# import uselect
import math
# import micropython
from inputSystem import InputSystem
from settings import Settings
import displayio
import terminalio
import busio
import board
import adafruit_ssd1327
from adafruit_display_text import label, scrolling_label
from adafruit_display_shapes import line, rect
from time import time, sleep
import usb_cdc
import re

# spi = SPI(0, sck=Pin("GP2"), mosi=Pin("GP3"))
# res = Pin("GP14")
# dc = Pin("GP15")
# cs = Pin("GP5")

# ssd1327 = SSD1327_SPI(128, 128, spi, dc, res, cs)

# a = bytearray(logo_data.data())

# ssd1327.fill(0)
# ssd1327.blit(fbuf, 0, 0, 0)
# ssd1327.show()

# SIE_STATUS=const(0x50110000+0x50)
# CONNECTED=const(1<<16)
# SUSPENDED=const(1<<4)

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


class HwScreen:
    palette: displayio.Palette
    # framebuffer
    # a = bytearray(128*128*3)
    # fbuf = framebuf.FrameBuffer(a, 128, 128, framebuf.GS4_HMSB)

    # drawing variables
    # labels = ["", "", "", "", "", ""]
    # topOffset = 0
    # bottomOffset = 0

    # drawObjects: list = [DrawObject]*128

    def __init__(self):
        displayio.release_displays()
        spi = busio.SPI(board.GP2, board.GP3)
        cs = board.GP5
        dc = board.GP15
        reset = board.GP14
        display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
        display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
        root = displayio.Group()
        color_count = 16
        color_palette = displayio.Palette(16)
        for i in range(color_count):
            component = i * 255 // (color_count - 1)
            color_palette[i] = component << 16 | component << 8 | component
        display.root_group = root

        self.root = root
        self.pallete = color_palette
        HwScreen.palette = color_palette
        self._display = display
        self._display_bus = display_bus

class Screen:
    def __init__(self, parent: displayio.Group):
        self.group = displayio.Group()
        parent.append(self.group)
        self.labels = [""]*6
        self._labelObjs = [[label.Label, line.Line]]*6
        self.topOffset = 0
        self.bottomOffset = 0
        self.objects = displayio.Group()
        for i in range(256):
            self.objects.append(displayio.Group())
        self.group.append(self.objects)
        self.__initLabels()
        pass

    def __initLabels(self):
        for index in range(0, 6):
            labelGrp = displayio.Group()
            vertPos = (index % 3)
            horPos = math.floor(index / 3)
            offset = 15
            lineOffset = 10
            spacing = math.floor((128-self.topOffset-self.bottomOffset)/2)
            x = 0+offset if horPos == 0 else 128-offset
            xL = 0+lineOffset if horPos == 0 else 128-lineOffset
            y = self.topOffset+spacing*vertPos
            anchorPoint = (0 if horPos == 0 else 1, 0.5)
            anchoredPos = (x, y)
            labelGrp.append(label.Label(terminalio.FONT, text=self.labels[index], color=HwScreen.palette[12], anchor_point=anchorPoint, anchored_position=anchoredPos))
            labelGrp.append(line.Line(xL, y, 0 if horPos == 0 else 128, y, HwScreen.palette[12]))
            self._labelObjs[index] = labelGrp
            self.group.append(labelGrp)
            # self.fbuf.text(label, x if horPos == 0 else x - (len(label)*8), y-4, 12)
            # cls.fbuf.line(xL, y, 0 if horPos == 0 else 128, y, 12)            
        pass

    def UpdateButtonAlignment(self, top: int = None, bottom: int = None):
        if top != None:
            self.topOffset = top
        if bottom != None:
            self.bottomOffset = bottom
        for index in range(0, 6):
            vertPos = (index % 3)
            horPos = math.floor(index / 3)
            offset = 15
            # lineOffset = 10
            spacing = math.floor((128-self.topOffset-self.bottomOffset)/2)
            x = 0+offset if horPos == 0 else 128-offset
            # xL = 0+lineOffset if horPos == 0 else 128-lineOffset
            y = self.topOffset+spacing*vertPos
            anchoredPos = (x, y)
            self._labelObjs[index][0].anchored_position = anchoredPos
            self._labelObjs[index][1].y = y
        

    def UpdateButtonLabel(self, index: int, label: str):
        self.labels[index] = label
        self._labelObjs[index][0].text = label

    def updateOthers(self):
        for element in self.objects:
            if isinstance(element, scrolling_label.ScrollingLabel):
                element.update()

        




    # @classmethod
    # def DrawButtonLabel(cls, index: int, label: str):
    #     vertPos = (index % 3)
    #     horPos = math.floor(index / 3)
    #     offset = 15
    #     lineOffset = 10
    #     spacing = math.floor((128-cls.topOffset-cls.bottomOffset)/2)
    #     x = 0+offset if horPos == 0 else 128-offset
    #     xL = 0+lineOffset if horPos == 0 else 128-lineOffset
    #     y = cls.topOffset+spacing*vertPos
    #     cls.fbuf.text(label, x if horPos == 0 else x - (len(label)*8), y-4, 12)
    #     cls.fbuf.line(xL, y, 0 if horPos == 0 else 128, y, 12)

    # @classmethod
    # def GenerateImage(cls):
    #     cls.fbuf.fill(0)
    #     for idx in range(len(cls.labels)):
    #         cls.DrawButtonLabel(idx, cls.labels[idx])
    #     for drawable in cls.drawObjects:
    #         drawable.draw(drawable)

mainScreen: HwScreen = None

class DvdScreen:
    def __init__(self, screen: HwScreen):
        self.x = random.randrange(0, 128-(3*8))
        self.y = random.randrange(0, 128-8)
        self.label = label.Label(terminalio.FONT, text="dvd", color=screen.pallete[12], anchor_point=(0,0), anchored_position=(self.x, self.y))
        self.leftright = 0
        self.updown = 0
        self.screen = screen
        self.group = displayio.Group()
        self.group.append(self.label)
        screen.root.append(self.group)
        pass

    def Hide(self):
        self.group.hidden = True

    def Show(self):
        self.group.hidden = False

    def step(self):
        if self.leftright == 0:
            if self.x == 0:
                self.leftright = 1
            else:
                self.x -= 1
        elif self.leftright == 1:
            if self.x == 128-self.label.bounding_box[2]:
                self.leftright = 0
            else:
                self.x += 1
            
        if self.updown == 0:
                if self.y == 0:
                    self.updown = 1
                else:
                    self.y -= 1
        elif self.updown == 1:
            if self.y == 128-self.label.bounding_box[3]:
                self.updown = 0
            else:
                self.y += 1
        self.label.anchored_position = (self.x, self.y)
        for group in self.screen.root:
            group.hidden = True
        self.group.hidden = False
        # self.screen.root[self.screen.root.index(self.group)].hidden = False

def StartBUI():
    mainScreen = HwScreen()
    
    mainLayer = displayio.Group()
    mainScreen.root.append(mainLayer)
    screen = Screen(mainLayer)
    dvdDisplay = DvdScreen(mainScreen)
    # old_status = SUSPENDED
    # last_ms = time()
    last_time = time()
    # spoll = uselect.poll()
    # spoll.register(sys.stdin, uselect.POLLIN)
    connected = False

    # intrVal = int(Settings.settings["kbd_intr"]) if "kbd_intr" in Settings.settings else 3
    # micropython.kbd_intr(intrVal) # WARNING THIS WILL DISABLE STOPPING OF THE PROJECT
    InputSystem.initInputs()
    encoderPos = InputSystem._r.position
    usb_cdc.data.reset_input_buffer()
    while True:
        InputSystem.updateButtons()
        shouldUpdateTime = False
        for bank in range(len(InputSystem.ButtonState)):
            for i in range(len(InputSystem.ButtonState[bank])):
                if InputSystem.ButtonState[bank][i] != 0:
                    shouldUpdateTime = True
                    usb_cdc.data.write(bytes([0, bank, i, InputSystem.ButtonState[bank][i]+1]))
        if InputSystem.EncoderState[InputSystem.BTN] != 0:
            shouldUpdateTime = True
            usb_cdc.data.write(bytes([0, 2, 0, InputSystem.EncoderState[InputSystem.BTN]+1]))

        newPos = InputSystem._r.position
        if newPos != encoderPos:
            diff = newPos - encoderPos
            usb_cdc.data.write(bytes([0, 2, 1, diff < 0, abs(diff)]))
            shouldUpdateTime = True

        encoderPos = newPos

        if shouldUpdateTime:
            pass
            # last_time = time()
            # mainScreen.root.hidden = False

        # fbuf.fill(0)
        if time() - last_time > 30:
            connected = False
        # if connected:
            # Screen.GenerateImage()
        # ssd1327.fill(0)

        while usb_cdc.data.in_waiting > 0:
            mainScreen.root.hidden = False
            connected = True
            dvdDisplay.Hide()
            mainLayer.hidden = False
            command = usb_cdc.data.read(1)
            puredata = ""
            for i in range(len(command)):
                puredata += str(command[i]) + " "
            print("[RECV]: " + str(command[0]) + f"({puredata})")
            # received = bytearray(sys.stdin.buffer.readline())
            # if command[0] == 0xFF or command[0] == 0x7E:
            if command[0] == 0xFE:
                print("Resetting screen...")
                for i in range(256):
                    screen.objects[i] = displayio.Group()
                screen.UpdateButtonAlignment(top=0, bottom=0)
                for i in range(6):
                    screen.UpdateButtonLabel(i, "")
            elif command[0] == 0x00: # top button offset
                if usb_cdc.data.in_waiting > 0:
                    data = usb_cdc.data.read(1)
                    screen.UpdateButtonAlignment(top=data[0])

            elif command[0] == 0x01: # bottom button offset
                if usb_cdc.data.in_waiting > 0:
                    data = usb_cdc.data.read(1)
                    screen.UpdateButtonAlignment(bottom=data[0])

            elif command[0] == 0x02:
                index: int = -1
                text: str = ""
                if usb_cdc.data.in_waiting > 0:
                    data = usb_cdc.data.read(1)
                    index = data[0] if len(data) > 0 else -1
                if usb_cdc.data.in_waiting > 0:
                    data = usb_cdc.data.readline()
                    text = data.decode().rstrip()
                print(f"Label new text '{text}' at index {index}")
                screen.UpdateButtonLabel(index, text)
            elif command[0] == 0x03:
                pass
            elif command[0] == 0x04: # write text to screen  [index] [type] [x] [y] [xAnchor] [yAnchor] "text"
                if usb_cdc.data.in_waiting > 6:
                    data = usb_cdc.data.read(6)
                    objIdx: int = data[0]
                    type: int = data[1]
                    # xPos: int = data[2]
                    # yPos: int = data[3]
                    position = (data[2], data[3])
                    anchor = (data[4]/255, data[5]/255)
                    # xAnchor = data[4]/256
                    # yAnchor = data[5]/256
                    data = usb_cdc.data.readline()
                    text = data.decode().rstrip()
                    isWhite = type < 2
                    color = HwScreen.palette[12] if isWhite else HwScreen.palette[0]
                    backgroundColor = None if type == 0x00 or type == 0x02 else (HwScreen.palette[12] if not isWhite else HwScreen.palette[0])
                    # print(backgroundColor, (type & (0x00 | 0x02)), type)
                    print(f"Drawing text. Params: index={objIdx}, Type={type}, position={position}, anchor={anchor}")
                    screen.objects[objIdx] = label.Label(terminalio.FONT, text=text, color=color, background_color=backgroundColor, anchor_point=anchor, anchored_position=position)
            elif command[0] == 0x05: # write scrolling text to screen  [index] [type] [x] [y] [xAnchor] [yAnchor] [scrollSpeedSeconds] [scrollSpeedSecondFraction] [maxChars] "text"
                if usb_cdc.data.in_waiting > 9:
                    data = usb_cdc.data.read(9)
                    objIdx: int = data[0]
                    type: int = data[1]
                    # xPos: int = data[2]
                    # yPos: int = data[3]
                    position = (data[2], data[3])
                    anchor = (data[4]/255, data[5]/255)
                    seconds = float(data[6])+(1/data[7] if data[7] != 0 else 0)
                    maxchars = data[8]
                    # xAnchor = data[4]/256
                    # yAnchor = data[5]/256
                    data = usb_cdc.data.readline()
                    text = re.sub('[^A-z0-9 -.]', '', data.decode().rstrip()).replace(" ", " ")
                    isWhite = type < 2
                    color = HwScreen.palette[12] if isWhite else HwScreen.palette[0]
                    backgroundColor = None if type == 0x00 or type == 0x02 else (HwScreen.palette[12] if not isWhite else HwScreen.palette[0])
                    # print(backgroundColor, (type & (0x00 | 0x02)), type)
                    print(f"Drawing scrolling text. Params: text={text}, index={objIdx}, Type={type}, position={position}, anchor={anchor}, seconds={seconds}, maxchars={maxchars}")
                    if not isinstance(screen.objects[objIdx], scrolling_label.ScrollingLabel):
                        screen.objects[objIdx] = scrolling_label.ScrollingLabel(terminalio.FONT, text=text, animate_time=seconds, max_characters=maxchars, color=color, background_color=backgroundColor, anchor_point=anchor, anchored_position=position)
                    else:
                        screen.objects[objIdx].text = text
                        screen.objects[objIdx].animate_time = seconds
                        screen.objects[objIdx].max_characters = maxchars
                        screen.objects[objIdx].color = color
                        screen.objects[objIdx].background_color = backgroundColor
                        screen.objects[objIdx].anchor_point = anchor
                        screen.objects[objIdx].anchored_position = position

            elif command[0] == 0x06: # draw rectangle to screen  [index] [x] [y] [width] [height] [outlineColor] [fillColor] [stroke]
                if usb_cdc.data.in_waiting > 7:
                    data = usb_cdc.data.read(8)
                    objIdx: int = data[0]
                    x: int = data[1]
                    y: int = data[2]
                    width: int = data[3]
                    height: int = data[4]
                    outlineColor: int = HwScreen.palette[data[5]%16] if data[5] != 0 else None
                    fillColor: int = HwScreen.palette[data[6]%16] if data[6] != 0 else None
                    stroke: int = data[7]
                    print(f"Drawing rect. Params: index={objIdx}, position={(x, y)}, size={(width, height)}, outline={outlineColor}, fill={fillColor}, stroke={stroke}")
                    screen.objects[objIdx] = rect.Rect(x=x, y=y, width=width, height=height, outline=outlineColor, fill=fillColor, stroke=stroke)

                    # Screen.drawObjects[objIdx] = TextObject(Screen.fbuf, type, xPos, yPos, label)

            # if command[0] == 0xFF:
                # connected = True
            # if
            last_time = time()

        screen.updateOthers()
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
        if not connected and time() - last_time < 60:
            dvdDisplay.step()
            sleep(0.25)
        elif not connected and time() - last_time > 60:
            mainScreen.root.hidden = True
            # x, y, leftright, updown = _bounceDVD(x, y, leftright, updown)
            # Screen.fbuf.fill(0)
            # Screen.fbuf.text("dvd", x, y, 12)
            # ssd1327.fill(0)
        # ssd1327.blit(Screen.fbuf, 0, 0, 0)
        # ssd1327.show()
