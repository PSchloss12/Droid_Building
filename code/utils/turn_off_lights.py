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
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
}

will = [
    {6:1,7:1,8:1},
    {3:1,4:1,5:1},
    {0:1,1:1,2:1},
    {16:1,18:1},
    {15:1,17:1},
    {9:1,14:1},
    {10:1, 13:1},
    {11:1, 12:1},
]

lights = LEDController()
sleep(1)
# set_leds(lights, {3:1, 0:1, 6:1})
# for config in will:
#     set_leds(lights, config)
#     sleep(0.1)
#     set_leds(lights, all_off)
#     sleep(0.1)
set_leds(lights, all_off)
sleep(1)