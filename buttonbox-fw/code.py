from settings import Settings
Settings.LoadSettings()
# from machine import Pin
# from utime import sleep, sleep_ms
from time import sleep
import board
import digitalio
import inputTest
# import buttonUI
# pin = Pin("LED", Pin.OUT)

def startBootup():
    inputTestCheckOut = digitalio.DigitalInOut(board.GP6)
    inputTestCheckOut.switch_to_output(True)
    inputTestCheckIn = digitalio.DigitalInOut(board.GP7)
    inputTestCheckIn.pull = digitalio.Pull.DOWN
    val = inputTestCheckIn.value
    inputTestCheckOut.deinit()
    inputTestCheckIn.deinit()
    if val == True:
        inputTest.startTest()
    # buttonUI.StartBUI()
    

if __name__ == "__main__":
    startBootup()
