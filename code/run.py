from ups import *
import robot_controller
from usb_sound_controller import USB_SoundController
from tft_display import TFTDisplay
import signal
import random
import time
import threading

# Add a global flag to signal threads to stop
stop_threads = False


def clean():
    global stop_threads
    stop_threads = True  # Signal threads to stop
    sound_controller.close()


def kill_signal_handler(sig, frame):
    print("Interrupt received, cleaning up...")
    clean()
    exit(0)


def random_sound(sound_controller):
    global stop_threads
    sounds = [
        "sounds/whiney.wav",
        "sounds/gallop.wav",
        "sounds/fail.mp3",
        "sounds/regain.wav",
        "sounds/fall.mp3",
    ]
    while not stop_threads:
        sound_controller.play_audio(random.choice(sounds))
        time.sleep(3)


def random_image(tft_display):
    global stop_threads
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
    while not stop_threads:
        word = random.choice(words)
        if len(word) == 1:
            tft_display.draw_text(
                word, position=(5, 40), font_size=24, color=(255, 0, 255)
            )
        else:
            tft_display.draw_text(
                word, position=(5, 40), font_size=10, color=(255, 0, 255)
            )
        time.sleep(1)
        tft_display.clear_screen("black")


def run_robot_controller():
    global stop_threads
    while not stop_threads:
        robot_controller.main()


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

# Create threads for sounds, images, and robot_controller
sound_thread = threading.Thread(target=random_sound, args=(sound_controller,))
image_thread = threading.Thread(target=random_image, args=(tft_display,))
robot_thread = threading.Thread(target=run_robot_controller)

# Start the threads
sound_thread.start()
image_thread.start()
robot_thread.start()

# Wait for threads to finish (if necessary)
sound_thread.join()
image_thread.join()
robot_thread.join()
