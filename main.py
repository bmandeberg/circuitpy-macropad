import board
import usb_hid
from digitalio import DigitalInOut, Direction, Pull
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import time

pressed_pins = set()
button_press_time = 0
button_debounce_time = 0.1
holding_command = False
holding_command_timer = 0
holding_command_time = 0.85
command_executed = False

time.sleep(1)
kbd = Keyboard(usb_hid.devices)


class Button:
    def __init__(self, pin):
        self.pin = pin
        self.input = DigitalInOut(pin)
        self.input.direction = Direction.INPUT
        self.input.pull = Pull.DOWN


class CommandMap:
    """Mapping a Set of pins to a list of key commands and optional held key command."""
    def __init__(self, pins, commands, hold_command=None):
        self.pins = pins
        self.commands = commands
        self.hold_command = hold_command


button_pins = [board.D2, board.D1, board.D0]
buttons = [Button(pin) for pin in button_pins]

commands_maps = [
    CommandMap({button_pins[0]}, [Keycode.COMMAND, Keycode.TAB]),
    CommandMap({button_pins[1]}, [Keycode.TAB], Keycode.COMMAND),
    CommandMap({button_pins[2]}, [Keycode.CONTROL, Keycode.TAB]),
    CommandMap({button_pins[0], button_pins[1]}, [Keycode.SHIFT, Keycode.COMMAND, Keycode.LEFT_BRACKET]),
    CommandMap({button_pins[1], button_pins[2]}, [Keycode.COMMAND, Keycode.GRAVE_ACCENT]),
    CommandMap({button_pins[0], button_pins[1], button_pins[2]}, [Keycode.COMMAND, Keycode.R]),
]

while True:
    pressing_pins = {button.pin for button in buttons if button.input.value}
    if len(pressing_pins):
        if len(pressed_pins) == 0:
            button_press_time = time.monotonic()
        pressed_pins.update(pressing_pins)
    elif command_executed:
        pressed_pins.clear()
        command_executed = False

    if len(pressed_pins) > 0 and time.monotonic() > button_press_time + button_debounce_time:
        for command_map in [c for c in commands_maps if c.pins == pressed_pins]:
            if command_map.hold_command:
                if not holding_command:
                    kbd.press(command_map.hold_command)
                    holding_command = True
                if not command_executed:
                    kbd.press(*command_map.commands)
                    time.sleep(0.01)
                    kbd.release(*command_map.commands)
                    command_executed = True
                holding_command_timer = time.monotonic()
            elif not command_executed:
                kbd.send(*command_map.commands)
                command_executed = True

    if holding_command and time.monotonic() > holding_command_timer + holding_command_time:
        kbd.release_all()
        holding_command = False
