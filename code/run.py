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


def draw_castle(tft_display):
    """
    Draws a simple castle using the drawing functions from tft_display.py.
    """
    # Clear the screen
    tft_display.clear_screen("black")

    # Draw the base of the castle
    tft_display.draw_box(
        top_left=(20, 100),
        bottom_right=(108, 150),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the left tower
    tft_display.draw_box(
        top_left=(20, 60),
        bottom_right=(50, 100),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the right tower
    tft_display.draw_box(
        top_left=(78, 60),
        bottom_right=(108, 100),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw battlements on the left tower
    tft_display.draw_box(
        top_left=(20, 50),
        bottom_right=(30, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )
    tft_display.draw_box(
        top_left=(40, 50),
        bottom_right=(50, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw battlements on the right tower
    tft_display.draw_box(
        top_left=(78, 50),
        bottom_right=(88, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )
    tft_display.draw_box(
        top_left=(98, 50),
        bottom_right=(108, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the castle door
    tft_display.draw_box(
        top_left=(60, 120),
        bottom_right=(80, 150),
        line_color=(255, 255, 255),
        fill_color=(64, 32, 0),
    )

    # Draw a flag on the left tower
    tft_display.draw_line(
        start=(35, 50), end=(35, 30), line_width=2, color=(255, 255, 255)
    )
    tft_display.draw_box(
        top_left=(35, 30),
        bottom_right=(45, 40),
        line_color=(255, 0, 0),
        fill_color=(255, 0, 0),
    )


def draw_crest(tft_display):
    """
    Draws a simplified version of the 2019-Crest-Navy image using the tft_display functions.
    """
    # Clear the screen
    tft_display.clear_screen("navy")

    # Draw the shield base
    tft_display.draw_box(
        top_left=(20, 20),
        bottom_right=(108, 140),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),  # Navy blue
    )

    # Draw the top battlements
    tft_display.draw_box(
        top_left=(20, 10),
        bottom_right=(40, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )
    tft_display.draw_box(
        top_left=(50, 10),
        bottom_right=(70, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )
    tft_display.draw_box(
        top_left=(80, 10),
        bottom_right=(100, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )

    # Draw the vertical and horizontal green cross
    tft_display.draw_box(
        top_left=(60, 20),
        bottom_right=(68, 140),
        line_color=(0, 255, 0),
        fill_color=(0, 255, 0),  # Green
    )
    tft_display.draw_box(
        top_left=(20, 70),
        bottom_right=(108, 78),
        line_color=(0, 255, 0),
        fill_color=(0, 255, 0),  # Green
    )

    # Draw the top-left quadrant (anchor symbol placeholder)
    tft_display.draw_circle(
        center=(40, 50),
        radius=15,
        line_color=(255, 255, 255),
        fill_color=(255, 255, 255),  # White
    )
    tft_display.draw_text(
        "⚓", position=(35, 40), font_size=18, color=(0, 0, 128)
    )  # Anchor symbol

    # Draw the top-right quadrant (striped pattern)
    for i in range(20, 50, 5):
        tft_display.draw_line(
            start=(70 + i, 20),
            end=(70, 20 + i),
            line_width=1,
            color=(192, 192, 192),  # Light gray
        )

    # Draw the bottom-left quadrant (striped pattern)
    for i in range(20, 50, 5):
        tft_display.draw_line(
            start=(20 + i, 78),
            end=(20, 78 + i),
            line_width=1,
            color=(192, 192, 192),  # Light gray
        )

    # Draw the bottom-right quadrant (helmet placeholder)
    tft_display.draw_circle(
        center=(80, 110),
        radius=15,
        line_color=(128, 128, 128),
        fill_color=(128, 128, 128),  # Gray
    )
    tft_display.draw_text(
        "🛡", position=(75, 100), font_size=18, color=(0, 255, 0)
    )  # Helmet symbol

    # Draw the central "D" emblem
    tft_display.draw_circle(
        center=(64, 78),
        radius=10,
        line_color=(192, 192, 192),
        fill_color=(192, 192, 192),  # Light gray
    )
    tft_display.draw_text(
        "D", position=(60, 70), font_size=14, color=(0, 0, 128)
    )  # "D" in the center


def draw_crown(tft_display):
    """
    Draws a simple crown using the drawing functions from tft_display.py.
    """
    # Clear the screen
    tft_display.clear_screen("black")

    # Draw the base of the crown
    tft_display.draw_box(
        top_left=(30, 100),
        bottom_right=(98, 120),
        line_color=(255, 215, 0),  # Gold
        fill_color=(255, 215, 0),  # Gold
    )

    # Draw the left spike
    tft_display.draw_line(
        start=(30, 100), end=(50, 60), line_width=2, color=(255, 215, 0)
    )  # Left side
    tft_display.draw_line(
        start=(50, 60), end=(70, 100), line_width=2, color=(255, 215, 0)
    )  # Right side

    # Draw the middle spike
    tft_display.draw_line(
        start=(60, 100), end=(80, 40), line_width=2, color=(255, 215, 0)
    )  # Left side
    tft_display.draw_line(
        start=(80, 40), end=(100, 100), line_width=2, color=(255, 215, 0)
    )  # Right side

    # Draw the right spike
    tft_display.draw_line(
        start=(90, 100), end=(110, 60), line_width=2, color=(255, 215, 0)
    )  # Left side
    tft_display.draw_line(
        start=(110, 60), end=(130, 100), line_width=2, color=(255, 215, 0)
    )  # Right side

    # Draw jewels on the spikes
    tft_display.draw_circle(
        center=(50, 60),
        radius=5,
        line_color=(0, 0, 255),  # Blue
        fill_color=(0, 0, 255),  # Blue
    )
    tft_display.draw_circle(
        center=(80, 40),
        radius=5,
        line_color=(255, 0, 0),  # Red
        fill_color=(255, 0, 0),  # Red
    )
    tft_display.draw_circle(
        center=(110, 60),
        radius=5,
        line_color=(0, 255, 0),  # Green
        fill_color=(0, 255, 0),  # Green
    )


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
    drawings = [draw_castle, draw_crest, draw_crown]
    while not stop_threads:
        # word = random.choice(words)
        # if len(word) == 1:
        #     tft_display.draw_text(
        #         word, position=(5, 40), font_size=24, color=(255, 0, 255)
        #     )
        # else:
        #     tft_display.draw_text(
        #         word, position=(5, 40), font_size=10, color=(255, 0, 255)
        #     )
        random.choice(drawings)(tft_display)
        time.sleep(3)
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
