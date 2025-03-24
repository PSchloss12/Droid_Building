from ups import *
import robot_controller
from usb_sound_controller import USB_SoundController
from tft_display import TFTDisplay

# from led_controller import
import signal
import random


def clean():
    sound_controller.close()


def kill_signal_handler(sig, frame):
    print("Interrupt received, cleaning up...")
    clean()
    exit(0)


def random_sound(sound_controller):
    sounds = [
        "sounds/whiney.wav",
        "sounds/gallop.wav",
        "sounds/fail.mp3",
        "sounds/regain.wav",
        "sounds/fall.mp3",
    ]
    sound_controller.play_audio(random.choice(sounds))


def random_image(tft_display):
    words = [
        "Castle",
        "King",
        "Bridge",
        "Sword",
        "Peasant",
        "Crown",
        "Bow before your king",
        "Kneel at the thrown",
        "On your knees",
        "For the motherland",
    ]
    tft_display.draw_text(
        random.choice(words), position=(5, 40), font_size=24, color=(255, 0, 255)
    )


# Register the signal handler
signal.signal(signal.SIGINT, kill_signal_handler)

# Initialize the USB Sound Controller
sound_controller = USB_SoundController()

# Initialize the TFT Display
tft_display = TFTDisplay()

# Initialize the LED Controller
# led_controller = LED_Controller()

# initialize power monitor
if check_initial_power_state():
    monitor_power()

robot_controller.main()
random_image(tft_display)
random_sound(sound_controller)
