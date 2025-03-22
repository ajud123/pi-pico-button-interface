# from machine import Pin, SPI
# from utime import sleep_ms
# from ssd1327 import SSD1327_SPI
# import framebuf
from board import *
import displayio
import adafruit_ssd1327
import busio
from time import sleep
from inputSystem import InputSystem
from settings import Settings
import math
import adafruit_display_text as text
import adafruit_display_shapes as shapes

class SettingsScreen:
    selectedOption = 0
    changing = False

    def _handleKbdIntr(change: int):
        Settings.settings["kbd_intr"] = str(int(SettingsScreen.options[SettingsScreen.selectedOption]["value"]) + change)
        SettingsScreen.options[SettingsScreen.selectedOption]["value"] = Settings.settings["kbd_intr"]
        pass

    print(Settings.settings)
    print("kbd_intr" in Settings.settings)

    KbdOption = {"name": "KBD INTR", 
                 "value": Settings.settings["kbd_intr"] if "kbd_intr" in Settings.settings else "3",
                 "handler": _handleKbdIntr,
                 "saveAfterExit": True} 

    def _handleInputTest(change: int):
        inputTest()
        pass

    InputTestOption = {"name": "Input test", "handler": _handleInputTest}

    options = [KbdOption, InputTestOption]

    @classmethod
    def handleSelection(cls, change: int):
        if not cls.changing:
            cls.selectedOption = (cls.selectedOption + change)%len(cls.options)
        elif "handler" in cls.options[cls.selectedOption]:
            cls.options[cls.selectedOption]["handler"](change)

class DevScreen:
    ssd1327: adafruit_ssd1327.SSD1327
    # fbuf: framebuf.FrameBuffer

def inputTest():
    ssd1327 = DevScreen.ssd1327
    # fbuf = DevScreen.fbuf
    # ssd1327.fill(0)
    # ssd1327.blit(fbuf, 0, 0, 0)
    # ssd1327.show()

    while True:
        InputSystem.updateButtons()
        buttons = InputSystem.ButtonState
        encoder = InputSystem.EncoderState
        fbuf.fill(0)
        
        fbuf.rect(10, 10, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.TOP] == 1 else 8, True)
        fbuf.rect(10, 30, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.MID] == 1 else 8, True)
        fbuf.rect(10, 50, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.BOT] == 1 else 8, True)
        fbuf.rect(10, 70, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.SIDE] == 1 else 8, True)
        fbuf.rect(108, 10, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.TOP] == 1 else 8, True)
        fbuf.rect(108, 30, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.MID] == 1 else 8, True)
        fbuf.rect(108, 50, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.BOT] == 1 else 8, True)
        fbuf.rect(108, 70, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.SIDE] == 1 else 8, True)

        fbuf.rect(int(64-(len(str(InputSystem._r.value()))/2)), 90, len(str(InputSystem._r.value())), 8, 0, True)
        fbuf.text(str(InputSystem._r.value()), int(64-(len(str(InputSystem._r.value()))/2*8)), 90, 8)
        fbuf.rect(59, 100, 10, 10, 12 if encoder[InputSystem.BTN] == 1 else 8, True)
        fbuf.rect(0, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTLEFT else 8, True)
        fbuf.rect(118, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT else 8, True)

        ssd1327.fill(0)
        ssd1327.blit(fbuf, 0, 0, 0)
        ssd1327.show()
        # print(str(BtnOne.value()) + " " + str(BtnTwo.value()) + " " + str(BtnThree.value()) + " " + str(BtnFour.value()) + " ")
        # sleep_ms(0.0001)



def startTest():
    InputSystem.initInputs()
    spi = busio.SPI(GP2, GP3)
    cs = GP5
    dc = GP15
    reset = GP14
    # spi = SPI(0, sck=Pin("GP2"), mosi=Pin("GP3"))
    # res = Pin("GP14")
    # dc = Pin("GP15")
    # cs = Pin("GP5")


    # ssd1327 = SSD1327_SPI(128, 128, spi, dc, res, cs)
    displayio.release_displays()
    display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
    sleep(1)
    display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
    g = displayio.Group()
    color_count = 16
    img = displayio.Bitmap(128, 128, 16)
    color_palette = displayio.Palette(16)
    t = displayio.TileGrid(img, pixel_shader=color_palette)

    dimension = min(display.width, display.height)

    pixels_per_step = dimension // color_count


    for i in range(dimension):

        if i % pixels_per_step == 0:
            continue
        img[i, i] = i // pixels_per_step


    for i in range(color_count):
        component = i * 255 // (color_count - 1)
        print(component)
        color_palette[i] = component << 16 | component << 8 | component

    g.append(t)
    display.root_group = g

    sleep(100)
    

    # a = bytearray(logo_data.data())
    # a = bytearray(128*128*3)
    # fbuf = framebuf.FrameBuffer(a, 128, 128, framebuf.GS4_HMSB)
    # ssd1327.fill(0)
    # ssd1327.blit(fbuf, 0, 0, 0)
    # ssd1327.show()

    # DevScreen.ssd1327 = ssd1327
    # DevScreen.fbuf = fbuf

    while True:
        InputSystem.updateButtons()
        buttons = InputSystem.ButtonState
        encoder = InputSystem.EncoderState
        fbuf.fill(0)
        fbuf.text("SYSTEM OPTIONS", 64-int(len("SYSTEM OPTIONS")/2*8), 10, 12)
        if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT:
            SettingsScreen.handleSelection(1)
        elif encoder[InputSystem.ROT] == InputSystem.ROTLEFT:
            SettingsScreen.handleSelection(-1)
        if encoder[InputSystem.BTN] == 1:
            SettingsScreen.changing = not SettingsScreen.changing
            if not SettingsScreen.changing and "saveAfterExit" in SettingsScreen.options[SettingsScreen.selectedOption] and SettingsScreen.options[SettingsScreen.selectedOption]["saveAfterExit"]:
                Settings.SaveSettings()
                

        for i in range(len(SettingsScreen.options)):
            option = SettingsScreen.options[i]
            color = 8
            if i == SettingsScreen.selectedOption:
                color = 12 if not SettingsScreen.changing else 0
                fbuf.rect(0, 10+(10*(i+1)), 128, 10, 12, True if SettingsScreen.changing else False)
            fbuf.text(option["name"], 8, 11+(10*(i+1)), color)
            if "value" in option:
                fbuf.text(option["value"], 120-(len(option["value"])*8), 11+(10*(i+1)), color)
            # fbuf.rect()
        # fbuf.rect(10, 10, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(10, 30, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(10, 50, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(10, 70, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.SIDE] == 1 else 8, True)
        # fbuf.rect(108, 10, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(108, 30, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(108, 50, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(108, 70, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.SIDE] == 1 else 8, True)

        fbuf.rect(int(64-(len(str(InputSystem._r.value()))/2)), 90, len(str(InputSystem._r.value())), 8, 0, True)
        # fbuf.text(str(InputSystem._r.value()), int(64-(len(str(InputSystem._r.value()))/2)), 90, 8)
        # fbuf.rect(59, 100, 10, 10, 12 if encoder[InputSystem.BTN] == 1 else 8, True)
        # fbuf.rect(0, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTLEFT else 8, True)
        # fbuf.rect(118, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT else 8, True)

        ssd1327.fill(0)
        ssd1327.blit(fbuf, 0, 0, 0)
        ssd1327.show()
        # print(str(BtnOne.value()) + " " + str(BtnTwo.value()) + " " + str(BtnThree.value()) + " " + str(BtnFour.value()) + " ")
        sleep_ms(1)