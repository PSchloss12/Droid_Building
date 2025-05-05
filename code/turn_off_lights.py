from led_controller import LEDController
from time import sleep


def set_leds(lights, config):
    lights.set_leds(config)
    lights.send()

all_off = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 0,
    9: 0,
    10: 0,
    11: 0,
    12: 0,
}

lights = LEDController()
sleep(1)
set_leds(lights, all_off)