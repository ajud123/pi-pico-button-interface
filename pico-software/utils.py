import microcontroller
import digitalio

def Pin(id: microcontroller.Pin, mode: digitalio.Direction = digitalio.Direction.INPUT, value: bool = False, pull: digitalio.Pull = None, drive: digitalio.DriveMode = digitalio.DriveMode.PUSH_PULL):
    obj = digitalio.DigitalInOut(id)
    obj.direction = mode
    if obj.direction == digitalio.Direction.OUTPUT:
        obj.value = value
        obj.drive_mode = drive
    else:
        obj.pull = pull
    return obj
