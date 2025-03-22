#!./.venv/bin/python3
import tkinter as tk
import socket
import asyncio
import math

# command reference
# first byte is the command
# one byte long arguments are marked with [argument name]
# text arguments are marked with "text argument name"

# Screen setup commands:
# 0x00 [offset]         top offset
# 0x01 [offset]         bottom offset
# 0x02 [index] "text"   set button label

# Drawing commands
# all drawing commands have [index] as their first parameter, allowing you to edit the type of drawable object at runtime
# to edit the type and parameters, just run the command and it will automatically update the object with new values
# currently theres no argument decoding or specification, meaning that you cannot send arguments in any order
# or simply updating objects with just the changed values.
# 0x03 [index]                          retrieve object and its properties at index
# 0x04 [index] [type] [x] [y] [xAnchor] [yAnchor] "text"    create text centered at the coordinates. 
#                                                           if type is set to 0x00, the text will be white with no box below. 
#                                                           if type is set to 0x01, the text will be white and it will be surrounded by a black box
#                                                           if type is set to 0x02, the text will be black with no box below
#                                                           if type is set to 0x03, the text will be black and it will be surrounded by a white box

# 0x05 [index] [type] [x] [y] [xAnchor] [yAnchor] [scrollSpeedSeconds] [scrollSpeedSecondFraction] [max_chars] "text"
#                                                           create scrolling text centered at the coordinates. Arguments same as for text except with extras
#                                                           scrollSpeedSeconds determines how many seconds between scrolling frames
#                                                           scrollSpeedSecondFraction is the fractional part of the argument (1/[arg]).
#                                                           max_chars determines how many characters will be shown at once


# 0x06 [index] [x] [y] [width] [height] [outlineColor] [fillColor] [stroke]     draw rectangle at given coordinates. X and Y are the top left of rect

# 0xFE                                  clears the screen
# 0xFF                                  initialize the connection with raspberry pi pico

class EmulatorTransport(asyncio.BaseTransport):
    def write(self, data: bytes):
        # parts = data[].decode().split(' ')
        match data[0]:
            case 0x00:
                if len(data) < 2:
                    print("Not enough supplied args")
                    return
                Emulator.topOffset = data[1]
            case 0x01:
                if len(data) < 2:
                    print("Not enough supplied args")
                    return
                Emulator.bottomOffset = data[1]
            case 0x02:
                if len(data) < 3:
                    print("Not enough supplied args")
                    return
                parts = data[2:].decode().split(' ')
                Emulator.TextLabel(int(data[1]), ' '.join(parts))
            case 0x03:
                if len(data) < 5:
                    print("Not enough supplied args")
                    return
                parts = data[4:].decode().split(' ')
                Emulator.TextBox(int(data[1]), int(data[2]), int(data[3]), ' '.join(parts))


            case _:
                return
        # print(data)

class Emulator:
    canvas: tk.Canvas = None
    btnLabels = ["", "", "", "", "", ""]
    topOffset = 0
    bottomOffset = 0
    async def _updateTask():
        while True:
            Emulator.canvas.update()
            await asyncio.sleep(1)

    def Start():
        print("Starting emulator.")
        Emulator.canvas = tk.Canvas(background="black", width=128, height=128)
        Emulator.canvas.pack()
        # Emulator.canvas.update()
        asyncio.get_running_loop().create_task(Emulator._updateTask())

    def Stop():
        print("Stopping emulator")
        Emulator.canvas.destroy()
        Emulator.canvas.quit()

    def _updateLabels():
        for idx in range(len(Emulator.btnLabels)):
            label = Emulator.btnLabels[idx]
            vertPos = (idx % 3)
            horPos = math.floor(idx / 3)
            offset = 15
            lineOffset = 10
            spacing = math.floor((128-Emulator.topOffset-Emulator.bottomOffset)/2)
            x = 0+offset if horPos == 0 else 128-offset
            xL = 0+lineOffset if horPos == 0 else 128-lineOffset
            y = Emulator.topOffset+spacing*vertPos
            Emulator.canvas.create_text(x, y, text=label, fill="white", anchor="w" if horPos == 0 else "e")
            Emulator.canvas.create_line(xL, y, 0 if horPos == 0 else 128, y, fill="white")
            # print(f"updated button {idx} with text '{label}'")
        Emulator.canvas.update()

    def _update():
        Emulator.canvas.delete("all")
        Emulator._updateLabels()

    def TextLabel(idx, label):
        Emulator.btnLabels[idx] = label
        Emulator._update()
    
    def TextBox(type: int, x: int, y: int, label):
        Emulator.canvas.create_text(x, y, text=label, anchor="center", fill="white" if type < 2 else "black")
        # Emulator._update()
        

