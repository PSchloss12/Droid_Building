from drive import *
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
from servo import Servo
from time import sleep, time
from threading import Thread
from alarm_routine import set_leds
from drawings import *

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

def open_left_gate(sound, lights, left_servo):
    print("Opening left gate")
    sound.play_text_to_speech("Lower the left drawbridge")
    on = 1
    for i in range(90):
        if i % 10 == 0:
            if on == 1:
                on = 0
            else:
                on = 1
            set_leds(lights, {17: on})
            left_servo.move_to(i)
            sleep(0.3)
    left_servo.move_to(90)

def send_out_scouts(sound, lights):
    sound.play_text_to_speech("Sending out scouts")
    sleep(2)
    sound.play_audio("sounds/gallop.wav")
    for _ in range(10):
        set_leds(lights, {2: 1, 4: 1, 0: 1})
        sleep(0.3)
        set_leds(lights, {2: 0, 4: 0, 0: 0})
        set_leds(lights, {5: 1, 7: 1, 3: 1})
        sleep(0.3)
        set_leds(lights, {5: 0, 7: 0, 3: 0})

def raise_left_gate(sound, lights, left_servo):
    print("Raising left gate")
    sound.play_text_to_speech("Raising the left drawbridge")
    on = 1
    for i in range(90, 0, -1):
        if i % 10 == 0:
            if on == 1:
                on = 0
            else:
                on = 1
            set_leds(lights, {18: on})
            left_servo.move_to(i)
            sleep(0.3)
    left_servo.move_to(0)

def scout_search(sound, saber, lights):
    sound.play_text_to_speech("Scouts are searching")
    sleep(2)
    sound.play_audio("sounds/old_zelda_theme.wav")
    for _ in range(5):
        drive_forward(saber, speed=30, duration=1)
        set_leds(lights, {12: 1, 13: 1, 14: 1, 9: 1, 10: 1, 11: 1})
        sleep(0.5)
        drive_forward(saber, speed=-30, duration=1)
        set_leds(lights, {12: 0, 13: 0, 14: 0, 9: 0, 10: 0, 11: 0})
        sleep(0.5)
        turn_robot(saber, "left", speed=40, duration=1)

def return_of_the_king(sound, lights):
    sound.play_text_to_speech("Scouts returning!")
    sleep(2)
    sound.play_audio("sounds/Small Item Catch.mp3")
    set_leds(lights, {3:1, 0:1, 6:1})
    for config in will:
        set_leds(lights, config)
        sleep(0.3)
        set_leds(lights, all_off)
        sleep(0.3)
    sound.play_audio("sounds/fanfare.wav")
    sleep(2)
    sound.play_text_to_speech("The king's guard returns")
    sleep(2)
    sound.play_audio("sounds/Small Item Catch.wav")
    sleep(2)

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

def lower_both_drawbridges(sound, lights, left_servo, right_servo):
    print("Lowering both drawbridges")
    sound.play_text_to_speech("Lowering both drawbridges")
    on = 1
    for i in range(90):
        if i % 10 == 0:
            if on == 1:
                on = 0
            else:
                on = 1
            set_leds(lights, {17: on})
            set_leds(lights, {15: on})
            left_servo.move_to(i)
            right_servo.move_to(90-i)
            sleep(0.3)
    left_servo.move_to(90)  # Open left gate
    right_servo.move_to(0)  # Open right gate

def main():
    try:
        sound = USB_SoundController()
        lights = LEDController()
        screen = TFTDisplay()
        left_servo = Servo(pin=21)
        right_servo = Servo(pin=20)
        saber = Sabertooth()
        saber.set_ramping(15)
        right_servo.move_to(90)
        left_servo.move_to(0)
        sleep(1)

        # Routine steps
        screen.display_bmp("images/smolwill.png", position=(0, 0))
        open_left_gate(sound, lights, left_servo)
        sleep(0.5)
        screen.display_bmp("images/sentlogo.png", position=(0, 0))
        send_out_scouts(sound, lights)
        sleep(0.5)
        raise_left_gate(sound, lights, left_servo)
        sleep(0.5)
        draw_castle(screen)
        scout_search(sound, saber, lights)
        sleep(0.5)
        lower_both_drawbridges(sound, lights, left_servo, right_servo)
        sleep(0.5)
        draw_crown(screen)
        return_of_the_king(sound, lights)
        sleep(0.5)

    finally:
        try:
            saber.close()
            sound.close()
            lights.close()
        except Exception as e:
            print(f"Error during cleanup: {e}")

if __name__ == "__main__":
    main()