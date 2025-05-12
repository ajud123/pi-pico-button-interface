from settings import Settings
from utils import Pin
Settings.LoadSettings()
# from machine import Pin
# from utime import sleep, sleep_ms
# from time import sleep
import board
import digitalio
import inputTest
import buttonUI
import supervisor
# pin = Pin("LED", Pin.OUT)

def startBootup():
    # inputTestCheckOut = digitalio.DigitalInOut(board.GP6)
    # inputTestCheckOut.direction = digitalio.Direction.OUTPUT
    # inputTestCheckOut.value = False
    inputTestCheckOut = Pin(board.GP6, digitalio.Direction.OUTPUT, False)
    # inputTestCheckIn = digitalio.DigitalInOut(board.GP7)
    # inputTestCheckIn.pull = digitalio.Pull.UP
    inputTestCheckIn = Pin(board.GP7, digitalio.Direction.INPUT, pull=digitalio.Pull.UP)
    val = inputTestCheckIn.value
    inputTestCheckOut.deinit()
    inputTestCheckIn.deinit()
    if val == False:
        inputTest.startTest()

    supervisor.runtime.autoreload = False
    buttonUI.StartBUI()


if __name__ == "__main__":
    startBootup()
