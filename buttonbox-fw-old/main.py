from settings import Settings
Settings.LoadSettings()
from machine import Pin
from utime import sleep, sleep_ms
import inputTest
import buttonUI
# pin = Pin("LED", Pin.OUT)

def startBootup():
    inputTestCheckOut = Pin("GP6", Pin.OUT)
    inputTestCheckOut.on()
    inputTestCheckIn = Pin("GP7", Pin.IN, Pin.PULL_DOWN)
    sleep_ms(1)
    if inputTestCheckIn.value() == 1:
        inputTest.startTest()
    buttonUI.StartBUI()
    

if __name__ == "__main__":
    startBootup()