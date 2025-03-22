from machine import Pin
from utime import sleep_ms, sleep_us
from rotary_irq_rp2 import RotaryIRQ 
class InputSystem:
    LEFT = 0
    RIGHT = 1
    TOP = 0
    MID = 1
    BOT = 2
    SIDE = 3

    ROTLEFT = -1
    ROTRIGHT = 1
    ROT = 0
    BTN = 1

    DOWN = -1
    UP = 1

    _SideButton: Pin
    _BtnMid: Pin
    _BtnBot: Pin
    _BtnTop: Pin
    _bankRightHigh: Pin
    _bankLeftHigh: Pin
    _encoderHigh: Pin
    _encoderLeft: Pin
    _encoderRight: Pin
    _encoderBtn: Pin

    _ButtonState = [[0,0,0,0], [0,0,0,0]]
    _EncoderState = [0, 0]

    ButtonState = [[0,0,0,0], [0,0,0,0]]
    EncoderState = [0, 0]

    _val_old = 0
    _r: RotaryIRQ

    @classmethod
    def initInputs(cls):
        InputSystem._SideButton = Pin("GP10", Pin.IN, Pin.PULL_DOWN)
        InputSystem._BtnMid = Pin("GP11", Pin.IN, Pin.PULL_DOWN)
        InputSystem._BtnBot = Pin("GP13", Pin.IN, Pin.PULL_DOWN)
        InputSystem._BtnTop = Pin("GP12", Pin.IN, Pin.PULL_DOWN)
        InputSystem._bankRightHigh = Pin("GP0", Pin.OUT)
        InputSystem._bankLeftHigh = Pin("GP1", Pin.OUT)
        InputSystem._encoderHigh = Pin("GP6", Pin.OUT)
        InputSystem._encoderHigh.on()
        InputSystem._encoderBtn = Pin("GP7", Pin.IN, Pin.PULL_DOWN)

        # InputSystem._encoderLeft = Pin("GP9", Pin.IN, Pin.PULL_DOWN)
        # InputSystem._encoderRight = Pin("GP8", Pin.IN, Pin.PULL_DOWN)

        InputSystem._r = RotaryIRQ(pin_num_clk="GP9",
              pin_num_dt="GP8",
              min_val=0,
              reverse=True,
              range_mode=RotaryIRQ.RANGE_UNBOUNDED,
              half_step=True)
        InputSystem._val_old = InputSystem._r.value()

        # InputSystem._encoderLeft.irq(trigger=Pin.IRQ_RISING, handler=InputSystem._encoderInterrupt)

    @classmethod
    def updateButtons(cls):
        Outputs = [[0, 0, 0, 0], [0, 0, 0, 0]]
        InputSystem._bankLeftHigh.on()
        Outputs[InputSystem.LEFT][InputSystem.TOP] = InputSystem._BtnTop.value()
        Outputs[InputSystem.LEFT][InputSystem.MID] = InputSystem._BtnMid.value()
        Outputs[InputSystem.LEFT][InputSystem.BOT] = InputSystem._BtnBot.value()
        Outputs[InputSystem.LEFT][InputSystem.SIDE] = InputSystem._SideButton.value()
        InputSystem._bankLeftHigh.off()
        InputSystem._bankRightHigh.on()
        Outputs[InputSystem.RIGHT][InputSystem.TOP] = InputSystem._BtnTop.value()
        Outputs[InputSystem.RIGHT][InputSystem.MID] = InputSystem._BtnMid.value()
        Outputs[InputSystem.RIGHT][InputSystem.BOT] = InputSystem._BtnBot.value()
        Outputs[InputSystem.RIGHT][InputSystem.SIDE] = InputSystem._SideButton.value()
        InputSystem._bankRightHigh.off()
        val_new = InputSystem._r.value()
        if InputSystem._val_old < val_new:
            InputSystem.EncoderState[InputSystem.ROT] = InputSystem.ROTRIGHT
        elif InputSystem._val_old > val_new:
            InputSystem.EncoderState[InputSystem.ROT] = InputSystem.ROTLEFT
        else:
            InputSystem.EncoderState[InputSystem.ROT] = 0

        InputSystem._val_old = val_new

        for i in range(len(cls._ButtonState)):
            for j in range(len(cls._ButtonState[i])):
                old = cls._ButtonState[i][j]
                new = Outputs[i][j]
                if old == new:
                    cls.ButtonState[i][j] = 0
                elif old == 1 and new == 0:
                    cls.ButtonState[i][j] = cls.UP
                else:
                    cls.ButtonState[i][j] = cls.DOWN

        encoderval = InputSystem._encoderBtn.value()

        if cls._EncoderState[cls.BTN] == encoderval:
            cls.EncoderState[cls.BTN] = 0
        elif cls._EncoderState[cls.BTN] == 1 and encoderval == 0:
            cls.EncoderState[cls.BTN] = cls.UP
        else:
            cls.EncoderState[cls.BTN] = cls.DOWN
        InputSystem._EncoderState[cls.BTN] = encoderval
        # sleep_ms(10)

        InputSystem._ButtonState = Outputs
        # return Outputs
