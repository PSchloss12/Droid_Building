from drive import *
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
from servo import Servo
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
    "sounds/alarm_bells.wav",
    "sounds/Boss Battle.mp3",
    "sounds/old_zelda_theme.wav",
    "sounds/Small Item Catch.mp3",
    "sounds/omnisis_gate.wav",
]

images = [
    "imgs/2019-Crest-Navy.png",
    "imgs/newcolor.png",
    "imgs/sentlogo.png",
    "imgs/Shieldip2.png",
    "imgs/smolwill.png",
    "imgs/alarm.jpg",
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
    13: 1,
    14: 1,
    15: 1,
    16: 1,
    17: 1,
    18: 1,
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
    13: 0,
    14: 0,
    15: 0,
    16: 0,
    17: 0,
    18: 0,
}

led_order = [13, 14, 15, 16, 17, 3, 2, 1, 19, 18, 10, 11, 12]


thread_running = False  # Flag to track if pizazz is running


def fight(sound, screen, lights):
    global thread_running
    thread_running = True
    sleep_time = 0.2
    clear(sound, screen, lights)
    try:
        sound.play_audio(sounds[6])
        for i in range(3):
            screen.display_bmp(images[i], position=(0, 0))
            for offby1 in led_order:
                num = offby1-1
                if num == 0:
                    set_leds(lights, {num: 1, 3: 1, 6: 1})
                    sleep(sleep_time)
                    set_leds(lights, {num: 0, 3: 0, 6: 0})
                elif num == 2:
                    set_leds(lights, {num: 1, 5: 1, 8: 1})
                    sleep(sleep_time)
                    set_leds(lights, {num: 0, 5: 0, 8: 0})
                elif num == 1:
                    set_leds(lights, {num: 1, 4: 1, 7: 1})
                    sleep(sleep_time)
                    set_leds(lights, {num: 0, 4: 0, 7: 0})
                else:
                    set_leds(lights, {num: 1})
                    sleep(sleep_time)
                    set_leds(lights, {num: 0})
                    sleep(sleep_time)

    except Exception as e:
        print(f"Error in fight: {e}")
        sleep(0.1)
        clear(sound, screen, lights)
    thread_running = False


def sound_alarm(sound, screen, lights):
    global thread_running
    thread_running = True
    sleep_time = 0.2
    screen.display_bmp(images[5], position=(0, 0))
    set_leds(lights, all_off)
    sound.play_audio(sounds[5])
    tick = time()
    while time() - tick < 6:
        set_leds(lights, all_on)
        sleep(sleep_time)
        set_leds(lights, all_off)
    sleep(sleep_time)
    set_leds(lights, all_on)
    thread_running = False


def clear(sound, screen, lights):
    try:
        sound.stop_sound()
        if screen.is_open():  # Ensure the screen is open before clearing
            screen.clear_screen("black")
        set_leds(lights, all_off)
    except Exception as e:
        print(f"Error in clear: {e}")


def set_leds(lights, config):
    lights.set_leds(config)
    lights.send()

def open_doors(left_servo, right_servo):
    global thread_running
    thread_running = True
    for i in range(90, 0, -1):
        if i % 5 == 0:
            left_servo.move_to(i)
            right_servo.move_to(90-i)
            sleep(0.3)

    right_servo.move_to(90)
    left_servo.move_to(0)
    thread_running = False

def close_doors(left_servo, right_servo):
    global thread_running
    thread_running = True
    print("Closing doors")
    for i in range(90):
        if i % 5 == 0:
            left_servo.move_to(i)
            right_servo.move_to(90-i)
            sleep(0.3)

    right_servo.move_to(0)
    left_servo.move_to(90)
    thread_running = False

def main():
    try:
        sound = USB_SoundController()
        screen = TFTDisplay()
        lights = LEDController()
        left_servo = Servo(pin=20)
        right_servo = Servo(pin=21)
        set_leds(lights, {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0})
        saber = Sabertooth()
        saber.set_ramping(15)
        sleep(1)

        screen.display_bmp(images[3], position=(0, 0))
        right_servo.move_to(90)
        left_servo.move_to(0)
        sleep(2)
        sound.play_text_to_speech("Prepare for battle!")
        sleep(2)

        sound.play_text_to_speech("Lock the doors!")
        sleep(2)
        door_thread = Thread(target=close_doors, args=(left_servo, right_servo), daemon=True)
        door_thread.start()
        sound.play_audio(sounds[9])
        door_thread.join()
        sleep(1)

        sound.play_text_to_speech("Sound the alarm!")
        sleep(2)
        Thread(target=sound_alarm, args=(sound, screen, lights), daemon=True).start()
        while thread_running:
            drive_forward(saber, speed=30, duration=2)
            sleep(0.2)
            drive_forward(saber, speed=-30, duration=2)
            sleep(0.2)

        Thread(target=fight, args=(sound, screen, lights), daemon=True).start()
        count = 0
        while thread_running:
            if count < 10:
                turn_robot(saber, "left", speed=40, duration=0.5)
            else:
                turn_robot(saber, "right", speed=40, duration=0.5)
            count += 1

        sound.play_text_to_speech("The enemy has been routed!")
        sleep(2)
        sound.play_audio(sounds[4])
        sleep(2)
        door_thread = Thread(target=open_doors, args=(left_servo, right_servo), daemon=True)
        door_thread.start()
        sound.play_audio(sounds[9])
        door_thread.join()
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


if __name__ == "__main__":
    main()
