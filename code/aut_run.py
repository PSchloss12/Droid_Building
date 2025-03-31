from detect_signs import initialize, detect_sign_new
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
import time


def drive_forward(saber, speed=35, duration=1):
    """
    Drive the robot forward at a specified speed for a specified duration.
    """
    for i in range(int(duration * 100)):
        saber.drive(speed, 0)  # Forward with no turning
    stop_robot(saber)  # Stop after the duration


def stop_robot(saber):
    """
    Stop the robot.
    """
    saber.stop()


def turn_robot(saber, direction, speed=40, duration=1):
    """
    Turn the robot in a specified direction.
    direction: "left" or "right"
    speed: Speed of the turn
    duration: Duration of the turn in seconds
    """
    if direction == "left":
        for i in range(int(duration * 75)):
            saber.drive(0, -speed)  # Turn left
    elif direction == "right":
        for i in range(int(duration * 75)):
            saber.drive(0, speed)  # Turn right
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
        drive_forward(saber, duration=1.2)  # Move forward for 2 seconds before turning
        turn_robot(saber, "left")
    elif sign == "right":
        print("Sign detected: RIGHT. Turning right...")
        sound_controller.play_text_to_speech("Turning right.")
        drive_forward(saber, duration=1.2)  # Move forward for 2 seconds before turning
        turn_robot(saber, "right")
    elif sign == "forward":
        print("Sign detected: forward. Continuing forward...")
        sound_controller.play_text_to_speech("Continuing forward.")
        drive_forward(saber, duration=2)  # Continue forward for 2 seconds
    elif sign == "continue":
        print("Sign too small. Continuing forward...")
        sound_controller.play_text_to_speech("Continuing forward.")
        drive_forward(saber, duration=2)  # Continue forward for 2 seconds
    else:
        print(f"Unknown sign detected: {sign}. Ignoring...")
        sound_controller.play_text_to_speech("Unknown sign detected. Ignoring.")
        drive_forward(saber, duration=0.5)


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
        drive_forward(saber, duration=1)  # Start driving forward for 1 second

        while True:
            # Scan for signs every second
            sign, area = detect_sign_new(cam, model)
            if area < 30000:
                sign = "continue"
            sign = sign.lower() if sign else ""
            print("*************")
            print(sign)
            print("*************")
            if sign:
                follow_sign(saber, sound_controller, sign)
                # Resume driving forward after handling the sign
                drive_forward(saber, duration=1)
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
    main()
