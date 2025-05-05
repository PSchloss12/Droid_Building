import time
from drive import *

def announce_sign(sound_controller, sign):
    """
    Follow the direction of the detected sign and announce it.
    """
    sign = sign.lower()
    if sign == "stop":
        # print("Sign detected: STOP. Stopping for 10 seconds...")
        sound_controller.play_text_to_speech("Stop Sign Detected. Stopping for 10 seconds.")
    elif sign == "left":
        # print("Sign detected: LEFT. Turning left...")
        sound_controller.play_text_to_speech("Left Sign Detected. Turning left.")
    elif sign == "right":
        # print("Sign detected: RIGHT. Turning right...")
        sound_controller.play_text_to_speech("Right Sign Detected. Turning right.")
    elif sign == "forward":
        # print("Sign detected: forward. Continuing forward...")
        sound_controller.play_text_to_speech("Forward Sign Detected. Continuing forward.")
    elif sign == "continue":
        # print("Sign too small. Continuing forward...")
        sound_controller.play_text_to_speech("All signs too small")
    else:
        # print(f"Unknown sign detected: {sign}. Ignoring...")
        sound_controller.play_text_to_speech("Unknown sign detected. Ignoring.")

def follow_sign(saber, sign):
    sign = sign.lower()
    if sign == "stop":
        stop_robot(saber)
        time.sleep(10)
        drive_forward(saber, duration=2)  # Move forward for 2 seconds before stopping
    elif sign == "left":
        drive_forward(saber, duration=1.3)  # Move forward for 2 seconds before turning
        turn_robot(saber, "left")
    elif sign == "right":
        drive_forward(saber, duration=1.4)  # Move forward for 2 seconds before turning
        turn_robot(saber, "right")
    elif sign == "forward":
        drive_forward(saber, duration=0.5)