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


thread_running = False  # Flag to track if pizazz is running

def pizazz(sound, screen, lights):
    global thread_running
    thread_running = True
    clear(sound, screen, lights)
    for i in range(5):
        try:
            sound.play_audio(sounds[i % len(sounds)])
            screen.display_bmp(images[i % len(images)], position=(0, 0))
            set_leds(lights, {i: 0.2})
            set_leds(lights, {i: 0.4})
            set_leds(lights, {i: 0.6})
            set_leds(lights, {i: 0.8})
            set_leds(lights, {i: 0.8})
            set_leds(lights, {i: 1})
            sleep(3)
            set_leds(lights, {i: 0})
            sleep(3)
            clear(sound, screen, lights)
        except Exception as e:
            print(f"Error in pizazz: {e}")
            sleep(0.5)
            clear(sound, screen, lights)
            continue
    thread_running = False


def brouhaha(sound, screen, lights):
    global thread_running
    thread_running = True
    try:
        clear(sound, screen, lights)
        sound.play_audio(random.choice(sounds))
        screen.display_bmp(random.choice(images), position=(0, 0))

        light_config = {}
        for i in range(8):
            on = random.randint(0, 1)
            light_config[i] = on
        set_leds(lights, light_config)
        sleep(3)
    except Exception as e:
        print(f"Error in brouhaha: {e}")
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
        sleep(2)

        while tock - tick < 10:
            tock = time()
            if int(tock - tick) % 3 == 0 and not thread_running:
                Thread(
                    target=brouhaha, args=(sound, screen, lights), daemon=True
                ).start()
            drive_robot(saber, speed=25, turn=15)
        while thread_running:
            drive_robot(saber, speed=25, turn=15)
        clear(sound, screen, lights)

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
