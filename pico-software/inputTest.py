# from machine import Pin, SPI
# from utime import sleep_ms
# from ssd1327 import SSD1327_SPI
# import framebuf
from board import *
import displayio
import adafruit_ssd1327
import busio
from time import sleep, monotonic_ns, monotonic
from inputSystem import InputSystem
from settings import Settings
import math
from adafruit_display_shapes import rect
from adafruit_display_text import label
import terminalio

displayio.release_displays()

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

    options = [InputTestOption]

    screen: displayio.Group

    selectionBox: rect.Rect

    ENTRY_HEIGHT = 12

    @classmethod
    def setChanging(cls, change: bool):
        if change:
            cls.selectionBox.fill = cls.selectionBox.outline
            for i in range(len(cls.screen[cls.selectedOption])):
                cls.screen[cls.selectedOption][i].color = DevScreen.pallete[8]
        else:
            cls.selectionBox.fill = None
            for i in range(len(cls.screen[cls.selectedOption])):
                cls.screen[cls.selectedOption][i].color = DevScreen.pallete[12]
        cls.changing = change
        pass

    @classmethod
    def handleSelection(cls, change: int):
        # print(change)
        if not cls.changing:
            cls.selectedOption = (cls.selectedOption + change)%len(cls.options)
            cls.selectionBox.y = 10+(cls.ENTRY_HEIGHT*(cls.selectedOption+1))
            for i in range(len(cls.screen)):
                for j in range(len(cls.screen[i])):
                    # print(i, cls.selectedOption)
                    cls.screen[i][j].color = DevScreen.pallete[12 if i == cls.selectedOption else 8]

                # print(dir(cls.screen[cls.selectedOption]))
                # print(cls.screen[cls.selectedOption][0])
            
        elif "handler" in cls.options[cls.selectedOption]:
            cls.options[cls.selectedOption]["handler"](change)

    @classmethod
    def generateScreen(cls):
        settings = displayio.Group()
        cls.screen = settings
        entryHeight = cls.ENTRY_HEIGHT
        rectangle = rect.Rect(0, 10+entryHeight, 128, entryHeight, fill=None, outline=DevScreen.pallete[12])
        cls.selectionBox = rectangle

        for i in range(len(cls.options)):
            element = displayio.Group()
            option = cls.options[i]
            color = 8
            if i == cls.selectedOption:
                color = 12 if not cls.changing else 0
                # element.append(rectangle)
#               fbuf.rect(0, 10+(10*(i+1)), 128, 10, 12, True if SettingsScreen.changing else False)

            element.append(label.Label(terminalio.FONT, text=option["name"], anchored_position=(8,10+(entryHeight*(i+1))), color=DevScreen.pallete[color], anchor_point=(0, 0)))
            # fbuf.text(option["name"], 8, , color)
            if "value" in option:
                # fbuf.text(option["value"], 120-(len(option["value"])*8), 11+(10*(i+1)), color)
                element.append(label.Label(terminalio.FONT, text=option["value"], anchored_position=(120,10+(entryHeight*(i+1))), color=DevScreen.pallete[color], anchor_point=(1, 0)))
            settings.append(element)

        return (rectangle, settings)




class DevScreen:
    ssd1327: adafruit_ssd1327.SSD1327
    pallete: displayio.Palette
    rootGroup: displayio.Group
    # fbuf: framebuf.FrameBuffer

def inputTest():
    root = DevScreen.rootGroup
    pallete = DevScreen.pallete

    root[0].hidden = True
    print(root[0])
    print(root[0].hidden)
    print(dir(root[0]))

    buttonLayout = [[None, None, None, None], [None, None, None, None]]
    testScreen = displayio.Group()
    buttonLayout[InputSystem.LEFT][InputSystem.TOP] = rect.Rect(10, 10, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.LEFT][InputSystem.MID] = rect.Rect(10, 30, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.LEFT][InputSystem.BOT] = rect.Rect(10, 50, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.LEFT][InputSystem.SIDE] = rect.Rect(10, 70, 10, 10, fill=pallete[8], outline=pallete[8])

    buttonLayout[InputSystem.RIGHT][InputSystem.TOP] = rect.Rect(108, 10, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.RIGHT][InputSystem.MID] = rect.Rect(108, 30, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.RIGHT][InputSystem.BOT] = rect.Rect(108, 50, 10, 10, fill=pallete[8], outline=pallete[8])
    buttonLayout[InputSystem.RIGHT][InputSystem.SIDE] = rect.Rect(108, 70, 10, 10, fill=pallete[8], outline=pallete[8])

    encoderBtn = rect.Rect(59, 100, 10, 10, fill=pallete[8], outline=pallete[8])
    encoderVal = label.Label(terminalio.FONT, text="n/a", color=pallete[12], anchor_point=(0.5, 0.5), anchored_position=(64, 90))
    # fbuf.rect(59, 100, 10, 10, 12 if encoder[InputSystem.BTN] == 1 else 8, True)


    for bank in buttonLayout:
        for group in bank:
            testScreen.append(group)
    testScreen.append(encoderBtn)
    testScreen.append(encoderVal)
    root.append(testScreen)

    # fbuf = DevScreen.fbuf
    # ssd1327.fill(0)
    # ssd1327.blit(fbuf, 0, 0, 0)
    # ssd1327.show()

    while True:
        start = monotonic()
        InputSystem.updateButtons()
        buttons = InputSystem.ButtonState
        encoder = InputSystem.EncoderState
        for x in range(len(buttonLayout)):
            for y in range(len(buttonLayout[x])):
                buttonLayout[x][y].fill = pallete[12] if buttons[x][y] == 1 else pallete[8]
                buttonLayout[x][y].outline = pallete[12] if buttons[x][y] == 1 else pallete[8]
        if encoder[InputSystem.BTN] == 1:
            encoderBtn.fill = pallete[12]
        else:
            encoderBtn.fill = pallete[8]
        encoderVal.text = str(InputSystem._r.position)
        end = monotonic()
        sleep(abs(1/60 - ((end-start)/1000)))
        # fbuf.fill(0)

        # fbuf.rect(10, 10, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(10, 30, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(10, 50, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(10, 70, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.SIDE] == 1 else 8, True)
        # fbuf.rect(108, 10, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(108, 30, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(108, 50, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(108, 70, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.SIDE] == 1 else 8, True)

        # fbuf.rect(int(64-(len(str(InputSystem._r.value()))/2)), 90, len(str(InputSystem._r.value())), 8, 0, True)
        # fbuf.text(str(InputSystem._r.value()), int(64-(len(str(InputSystem._r.value()))/2*8)), 90, 8)
        # fbuf.rect(59, 100, 10, 10, 12 if encoder[InputSystem.BTN] == 1 else 8, True)
        # fbuf.rect(0, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTLEFT else 8, True)
        # fbuf.rect(118, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT else 8, True)

        # ssd1327.fill(0)
        # ssd1327.blit(fbuf, 0, 0, 0)
        # ssd1327.show()
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

    display_bus = displayio.FourWire(spi, command=dc, chip_select=cs, reset=reset, baudrate=1000000)
    display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=128)
    g = displayio.Group()
    color_count = 16
    # img = displayio.Bitmap(128, 128, 16)
    color_palette = displayio.Palette(16)
    # t = displayio.TileGrid(img, pixel_shader=color_palette)

    # dimension = min(display.width, display.height)

    # pixels_per_step = dimension // color_count


    # for i in range(dimension):

    #     if i % pixels_per_step == 0:
    #         continue
    #     img[i, i] = i // pixels_per_step


    for i in range(color_count):
        component = i * 255 // (color_count - 1)
        # print(component)
        color_palette[i] = component << 16 | component << 8 | component
    DevScreen.pallete = color_palette
    # g.append(t)
    display.root_group = g
    mainScreen = displayio.Group()
    g.append(mainScreen)
    DevScreen.rootGroup = g


    # a = bytearray(logo_data.data())
    # a = bytearray(128*128*3)
    # fbuf = framebuf.FrameBuffer(a, 128, 128, framebuf.GS4_HMSB)
    # ssd1327.fill(0)
    # ssd1327.blit(fbuf, 0, 0, 0)
    # ssd1327.show()

    # DevScreen.ssd1327 = ssd1327
    # DevScreen.fbuf = fbuf
    text = label.Label(terminalio.FONT, text="SYSTEM OPTIONS")
    text.anchor_point=(0.5, 0.5)
    text.anchored_position=(64,8)
    mainScreen.append(text)
    mainScreen.append(rect.Rect(10, 10, 10, 10, fill=None))
    sbox, settingsscreen = SettingsScreen.generateScreen()
    mainScreen.append(sbox)
    mainScreen.append(settingsscreen)

    while True:
        InputSystem.updateButtons()
        buttons = InputSystem.ButtonState
        encoder = InputSystem.EncoderState
        # print(encoder)
        # g.append
        # fbuf.fill(0)
        # fbuf.text("SYSTEM OPTIONS", 64-int(len("SYSTEM OPTIONS")/2*8), 10, 12)
        if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT:
            SettingsScreen.handleSelection(1)
        elif encoder[InputSystem.ROT] == InputSystem.ROTLEFT:
            SettingsScreen.handleSelection(-1)
        if encoder[InputSystem.BTN] == 1:
            SettingsScreen.setChanging(not SettingsScreen.changing)
            if not SettingsScreen.changing and "saveAfterExit" in SettingsScreen.options[SettingsScreen.selectedOption] and SettingsScreen.options[SettingsScreen.selectedOption]["saveAfterExit"]:
                Settings.SaveSettings()


        # for i in range(len(SettingsScreen.options)):
        #     option = SettingsScreen.options[i]
        #     color = 8
        #     if i == SettingsScreen.selectedOption:
        #         color = 12 if not SettingsScreen.changing else 0
        #         fbuf.rect(0, 10+(10*(i+1)), 128, 10, 12, True if SettingsScreen.changing else False)
        #     fbuf.text(option["name"], 8, 11+(10*(i+1)), color)
        #     if "value" in option:
        #         fbuf.text(option["value"], 120-(len(option["value"])*8), 11+(10*(i+1)), color)

            # fbuf.rect()
        # fbuf.rect(10, 10, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(10, 30, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(10, 50, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(10, 70, 10, 10, 12 if buttons[InputSystem.LEFT][InputSystem.SIDE] == 1 else 8, True)
        # fbuf.rect(108, 10, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.TOP] == 1 else 8, True)
        # fbuf.rect(108, 30, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.MID] == 1 else 8, True)
        # fbuf.rect(108, 50, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.BOT] == 1 else 8, True)
        # fbuf.rect(108, 70, 10, 10, 12 if buttons[InputSystem.RIGHT][InputSystem.SIDE] == 1 else 8, True)

        # fbuf.rect(int(64-(len(str(InputSystem._r.value()))/2)), 90, len(str(InputSystem._r.value())), 8, 0, True)
        # fbuf.text(str(InputSystem._r.value()), int(64-(len(str(InputSystem._r.value()))/2)), 90, 8)
        # fbuf.rect(59, 100, 10, 10, 12 if encoder[InputSystem.BTN] == 1 else 8, True)
        # fbuf.rect(0, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTLEFT else 8, True)
        # fbuf.rect(118, 100, 10, 10, 12 if encoder[InputSystem.ROT] == InputSystem.ROTRIGHT else 8, True)

        # ssd1327.fill(0)
        # ssd1327.blit(fbuf, 0, 0, 0)
        # ssd1327.show()
        # print(str(BtnOne.value()) + " " + str(BtnTwo.value()) + " " + str(BtnThree.value()) + " " + str(BtnFour.value()) + " ")
        # sleep_ms(1)
