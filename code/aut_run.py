from detect_signs import initialize, detect_sign_new
from sabertooth import Sabertooth
import time


def drive_forward(saber, speed=0.5):
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


def follow_sign(saber, sign):
    """
    Follow the direction of the detected sign.
    """
    if sign == "stop":
        print("Sign detected: STOP. Stopping for 10 seconds...")
        stop_robot(saber)
        time.sleep(10)
    elif sign == "left":
        print("Sign detected: LEFT. Turning left...")
        turn_robot(saber, "left")
    elif sign == "right":
        print("Sign detected: RIGHT. Turning right...")
        turn_robot(saber, "right")
    elif sign == "up":
        print("Sign detected: UP. Continuing forward...")
        drive_forward(saber)
    else:
        print(f"Unknown sign detected: {sign}. Ignoring...")


def main():
    # Initialize camera and YOLO model
    cam, model = initialize()

    # Initialize Sabertooth motor controller
    saber = Sabertooth()
    saber.set_ramping(15)  # Set ramping for smooth motor control

    try:
        print("Starting autonomous driving...")
        drive_forward(saber)  # Start driving forward

        while True:
            # Scan for signs every second
            sign = detect_sign_new(cam, model)
            if sign:
                follow_sign(saber, sign)
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


if __name__ == "__main__":
    main()
