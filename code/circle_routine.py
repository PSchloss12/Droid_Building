from drive import *
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
from autonomous import clean
import random
from time import sleep, time
from threading import Thread

sounds = [
    "sounds/whiney.wav",
    "sounds/gallop.wav",
    "sounds/fail.mp3",
    "sounds/regain.wav",
    "sounds/fanfare.mp3",
]

images = [
    "img/2019-Crest-Navy.png",
    "img/newcolor.png",
    "img/sentlogo.png",
    "img/Shieldip2.png",
    "img/smolwill.png",
]


def pizazz(sound, screen, lights):
    clear(sound, screen, lights)
    # Go in order of light, turing on then off
    for i in range(8):
        sound.play_audio(sounds[i % len(sounds)])
        screen.display_bmp(images[i % len(images)], position=(0, 0))
        set_leds(lights, {i: 0.2})
        set_leds(lights, {i: 0.4})
        set_leds(lights, {i: 0.6})
        set_leds(lights, {i: 0.8})
        set_leds(lights, {i: 0.8})
        set_leds(lights, {i: 1})
        sleep(1)
        set_leds(lights, {i: 0})
        sleep(0.5)
        clear(sound, screen, lights)


def brouhaha(sound, screen, lights):
    clear(sound, screen, lights)
    sounds = [
        "sounds/whiney.wav",
        "sounds/gallop.wav",
        "sounds/fail.mp3",
        "sounds/regain.wav",
        "sounds/fanfare.mp3",
    ]
    sound.play_audio(random.choice(sounds))

    images = [
        "img/2019-Crest-Navy.png",
        "img/newcolor.png",
        "img/sentlogo.png",
        "img/Shieldip2.png",
        "img/smolwill.png",
    ]
    screen.display_bmp(random.choice(images), position=(0, 0))

    light_config = {}
    for i in range(8):
        on = random.randint(0, 1)
        light_config[i] = on
    set_leds(lights, light_config)


def clear(sound, screen, lights):
    sound.stop_sound()
    screen.clear_screen("black")
    set_leds(lights, {i: 0 for i in range(9)})


def set_leds(lights, config):
    lights.set_leds(config)
    lights.send()


if __name__ == "__main__":
    try:
        sound = USB_SoundController()
        screen = TFTDisplay()
        lights = LEDController()
        set_leds(lights, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0})
        saber = Sabertooth()
        saber.set_ramping(15)

        tick = time()
        tock = tick

        sound.play_text_to_speech("Begin circle patrol")

        while tock - tick < 10:
            tock = time()
            if int(tock - tick) % 3 == 0:
                Thread(
                    target=brouhaha, args=(sound, screen, lights), daemon=True
                ).start()
            drive_robot(saber, speed=30, turn=10)

    finally:
        saber.close()
        screen.close()
        sound.close()
        lights.close()
