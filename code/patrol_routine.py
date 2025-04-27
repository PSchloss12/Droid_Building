from drive import *
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
from autonomous import clean


def turn_robot(sound, screen, saber, lights, direction, speed=35, duration=1):
    light_on = False
    if direction == "left":
        sound.play_text_to_speech("Turning left")
        screen.draw_arrow(direction="right")
        for i in range(int(duration * 62)):
            if i % 5 == 0:
                if light_on:
                    set_leds(lights, {0: 0, 3: 0, 6: 0})
                    light_on = False
                else:
                    set_leds(lights, {0: 1, 3: 1, 6: 1})
                    light_on = True
            saber.drive(0, -speed)  # Turn left
        set_leds(lights, {0: 0, 3: 0, 6: 0})
    elif direction == "right":
        sound.play_text_to_speech("Turning right")
        screen.draw_arrow(direction="right")
        for i in range(int(duration * 62)):
            if i % 5 == 0:
                if light_on:
                    set_leds(lights, {2: 0, 5: 0, 8: 0})
                    light_on = False
                else:
                    set_leds(lights, {2: 1, 5: 1, 8: 1})
                    light_on = True
            saber.drive(0, speed)  # Turn right
        set_leds(lights, {2: 0, 5: 0, 8: 0})
    stop_robot(saber)


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

        # sound.play_text_to_speech("Starting patrol")
        drive_forward(saber, speed=35, duration=1)
        turn_robot(sound, screen, saber, lights, "left", speed=35, duration=1)
        drive_forward(saber, speed=35, duration=0.8)
        for i in range(3):
            turn_robot(sound, screen, saber, lights, "left", speed=35, duration=1)
            drive_forward(saber, speed=35, duration=1.8)
        turn_robot(sound, screen, saber, lights, "left", speed=35, duration=1)
        drive_forward(saber, speed=35, duration=0.8)
        turn_robot(sound, screen, saber, lights, "left", speed=35, duration=1)
        drive_forward(saber, speed=35, duration=0.8)
        # sound.play_text_to_speech("Patrol complete, Area clear")

    finally:
        saber.close()
        screen.close()
        sound.close()
        lights.close()
