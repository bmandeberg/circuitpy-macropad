import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

button_hold_time = 2
button_debounce_time = 0.2

button1 = DigitalInOut(board.D2)
button1.direction = Direction.INPUT
button1.pull = Pull.DOWN
button1_timer = 0
button1_press = False

button2 = DigitalInOut(board.D1)
button2.direction = Direction.INPUT
button2.pull = Pull.DOWN
button2_timer = 0
button2_press = False
holding_command = False
holding_command_timer = 0
holding_command_time = 1

button3 = DigitalInOut(board.D0)
button3.direction = Direction.INPUT
button3.pull = Pull.DOWN
button3_timer = 0
button3_press = False

led_pin1 = DigitalInOut(board.D3)
led_pin1.direction = Direction.INPUT
led_pin2 = DigitalInOut(board.D4)
led_pin2.direction = Direction.INPUT

kbd = Keyboard()

mode = 0


def leds_off():
    led_pin1.switch_to_input()
    led_pin2.switch_to_input()


def led1_on():
    led_pin2.switch_to_output()
    led_pin2.value = True


def led2_on():
    led_pin1.switch_to_output()
    led_pin1.value = True
    led_pin2.switch_to_output()
    led_pin2.value = False


def led3_on():
    led_pin1.switch_to_output()
    led_pin2.value = False


def led_seq(led):
    led_fn = None
    if led == 1:
        led_fn = led1_on
    elif led == 2:
        led_fn = led2_on
    elif led == 3:
        led_fn = led3_on
    led_fn()
    time.sleep(0.25)
    leds_off()
    time.sleep(0.25)
    led_fn()
    time.sleep(0.25)
    leds_off()
    time.sleep(0.25)
    led_fn()
    time.sleep(0.25)
    leds_off()


while True:
    if button1.value:
        if not button1_press:
            button1_press = True
            button1_timer = time.monotonic()
            # do press
            kbd.send(Keycode.COMMAND, Keycode.TAB)
            if mode == 2:
                time.sleep(button_debounce_time)
        elif time.monotonic() > button1_timer + button_hold_time:
            mode = 0
            button1_timer = time.monotonic()
            led_seq(2)
    elif button1_press:
        button1_press = False

    if button2.value:
        if not button2_press:
            button2_press = True
            button2_timer = time.monotonic()
            # do press
            if mode == 0:
                if not holding_command:
                    kbd.press(Keycode.COMMAND)
                    holding_command = True
                    holding_command_timer = time.monotonic()
                kbd.press(Keycode.TAB)
                time.sleep(0.01)
                kbd.release(Keycode.TAB)
                holding_command_timer = time.monotonic()
            elif mode == 1:
                kbd.send(Keycode.COMMAND, Keycode.R)
            elif mode == 2:
                kbd.send(Keycode.COMMAND, Keycode.TAB)
                time.sleep(button_debounce_time)
        elif time.monotonic() > button2_timer + button_hold_time:
            mode = 1
            button2_timer = time.monotonic()
            led_seq(2)
    elif button2_press:
        button2_press = False

    if button3.value:
        if not button3_press:
            button3_press = True
            button3_timer = time.monotonic()
            # do press
            if mode == 0 or mode == 1:
                kbd.send(Keycode.CONTROL, Keycode.TAB)
            elif mode == 2:
                kbd.send(Keycode.COMMAND, Keycode.TAB)
                time.sleep(button_debounce_time)
        elif time.monotonic() > button3_timer + button_hold_time:
            mode = 2
            button3_timer = time.monotonic()
            led_seq(2)
    elif button3_press:
        button3_press = False

    if (
        holding_command
        and time.monotonic() > holding_command_timer + holding_command_time
    ):
        kbd.release(Keycode.COMMAND)
        holding_command = False
