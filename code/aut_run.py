from detect_signs import initialize, detect_sign_new
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
import time


def drive_forward(saber, speed=50):
    """
    Drive the robot forward at a specified speed.
    """
    saber.drive(speed, 0)  # Forward with no turning


def stop_robot(saber):
    """
    Stop the robot.
    """
    saber.stop()


def turn_robot(saber, direction, speed=0.5, duration=2):
    """
    Turn the robot in a specified direction.
    direction: "left" or "right"
    speed: Speed of the turn
    duration: Duration of the turn in seconds
    """
    if direction == "left":
        saber.drive(0, -speed)  # Turn left
    elif direction == "right":
        saber.drive(0, speed)  # Turn right
    time.sleep(duration)
    stop_robot(saber)


def follow_sign(saber, sound_controller, sign):
    """
    Follow the direction of the detected sign and announce it.
    """
    if sign == "stop":
        print("Sign detected: STOP. Stopping for 10 seconds...")
        sound_controller.play_text_to_speech("Stopping for 10 seconds.")
        stop_robot(saber)
        time.sleep(10)
    elif sign == "left":
        print("Sign detected: LEFT. Turning left...")
        sound_controller.play_text_to_speech("Turning left.")
        drive_forward(saber)
        time.sleep(1)  # Move forward for a second before turning
        stop_robot(saber)  # Stop before turning
        turn_robot(saber, "left")
    elif sign == "right":
        print("Sign detected: RIGHT. Turning right...")
        sound_controller.play_text_to_speech("Turning right.")
        drive_forward(saber)
        time.sleep(1)  # Move forward for a second before turning
        stop_robot(saber)  # Stop before turning
        turn_robot(saber, "right")
    elif sign == "up":
        print("Sign detected: UP. Continuing forward...")
        sound_controller.play_text_to_speech("Continuing forward.")
        drive_forward(saber)
    else:
        print(f"Unknown sign detected: {sign}. Ignoring...")
        sound_controller.play_text_to_speech("Unknown sign detected. Ignoring.")


def main():
    # Initialize camera and YOLO model
    cam, model = initialize()

    # Initialize Sabertooth motor controller
    saber = Sabertooth()
    saber.set_ramping(15)  # Set ramping for smooth motor control

    # Initialize USB Sound Controller
    sound_controller = USB_SoundController()

    try:
        print("Starting autonomous driving...")
        drive_forward(saber)  # Start driving forward

        while True:
            # Scan for signs every second
            sign = detect_sign_new(cam, model)
            sign = sign.lower() if sign else ""
            print("*************")
            print(sign)
            print("*************")
            if sign:
                follow_sign(saber, sound_controller, sign)
                # Resume driving forward after handling the sign
                drive_forward(saber)
            time.sleep(1)

    except KeyboardInterrupt:
        print("Autonomous driving interrupted by user.")

    finally:
        print("Stopping robot and cleaning up...")
        stop_robot(saber)
        cam.stop()
        saber.close()
        sound_controller.close()


if __name__ == "__main__":
    print("hello world")
    saber = Sabertooth()
    saber.set_ramping(15)
    drive_forward(saber)  # Start driving forward
    time.sleep(1)  # Drive forward for 5 seconds
    stop_robot(saber)  # Stop the robot after 5 seconds
    print("goodbye")
    # main()
