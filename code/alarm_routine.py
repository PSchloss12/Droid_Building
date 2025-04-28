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
    "sounds/fail.wav",
    "sounds/regain.wav",
    "sounds/fanfare.wav",
]

images = [
    "imgs/2019-Crest-Navy.png",
    "imgs/newcolor.png",
    "imgs/sentlogo.png",
    "imgs/Shieldip2.png",
    "imgs/smolwill.png",
]

all_on = {
    0: 1,
    1: 1,
    2: 1,
    3: 1,
    4: 1,
    5: 1,
    6: 1,
    7: 1,
    8: 1,
    9: 1,
    10: 1,
    11: 1,
    12: 1,
}
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


thread_running = False  # Flag to track if pizazz is running


def circle(sound, screen, lights):
    global thread_running
    thread_running = True
    sleep_time = 0.2

    clear(sound, screen, lights)
    try:
        for i in range(3):
            screen.draw_arrow(direction="up")
            sound.play_audio(sounds[1])
            set_leds(lights, {0: 0.2, 1: 0.2, 2: 0.2, 3: 0.2})
            screen.draw_arrow(direction="right")
            sleep(sleep_time)
            set_leds(lights, {0: 0.4, 1: 0.4, 2: 0.4, 3: 0.4})
            sleep(sleep_time)
            set_leds(lights, {0: 0.6, 1: 0.6, 2: 0.6, 3: 0.6})
            screen.draw_arrow(direction="up")
            sleep(sleep_time)
            set_leds(lights, {0: 0.8, 1: 0.8, 2: 0.8, 3: 0.8})
            sleep(sleep_time)
            set_leds(lights, {0: 1, 1: 1, 2: 1, 3: 1})
            screen.draw_arrow(direction="left")
            sleep(sleep_time)
            set_leds(lights, {i: 0})
            sleep(sleep_time)
            screen.draw_arrow(direction="up")
            sleep(sleep_time * 2)
    except Exception as e:
        print(f"Error in pizazz: {e}")
        sleep(0.5)
        clear(sound, screen, lights)
    thread_running = False


def intruder_detected(sound, screen, lights):
    global thread_running
    thread_running = True
    sleep_time = 0.2

    for i in range(3):
        sound.play_audio(sounds[0])
        for i in range(3):
            set_leds(lights, all_on)
            screen.clear_screen("black")
            sleep(sleep_time)
            screen.clear_screen("red")
            sleep(sleep_time)
            set_leds(lights, all_off)
            screen.clear_screen("white")
            sleep(sleep_time)

    clear(sound, screen, lights)
    thread_running = False


def clear(sound, screen, lights):
    try:
        sound.stop_sound()
        if screen.is_open():  # Ensure the screen is open before clearing
            screen.clear_screen("black")
        set_leds(lights, {i: 0 for i in range(9)})
    except Exception as e:
        print(f"Error in clear: {e}")


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

        sleep(1)

        Thread(target=circle, args=(sound, screen, lights), daemon=True).start()
        while thread_running:
            drive_robot(saber, speed=25, turn=15)
        clear(sound, screen, lights)
        stop_robot(saber)

        sound.play_text_to_speech("Intrusion detected!")
        Thread(
            target=intruder_detected, args=(sound, screen, lights), daemon=True
        ).start()

        sleep(1)

        sound.play_text_to_speech("Resuming patrol")
        Thread(target=circle, args=(sound, screen, lights), daemon=True).start()
        while thread_running:
            drive_robot(saber, speed=25, turn=15)
        clear(sound, screen, lights)
        stop_robot(saber)

    finally:
        try:
            # set_leds(lights, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0})
            saber.close()
            if screen.is_open():  # Ensure the screen is open before closing
                screen.close()
            sound.close()
            lights.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")
