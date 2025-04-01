import threading
import time
import signal
import sys  # Added for sys.exit
import numpy as np
import cv2
from detect_signs import initialize, detect_sign_new
from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController

# Use threading.Event for thread-safe signaling
stop_event = threading.Event()
frame_freq = 0.5  # Frequency to check for signs (in seconds)

saber = None
sound_controller = None

# Add a lock for thread-safe access to shared resources
drive_lock = threading.Lock()


def clean(saber, sound_controller, threads):
    """
    Clean up resources, stop all threads, and join them.
    """
    stop_event.set()  # Signal threads to stop
    for thread in threads:
        thread.join()  # Ensure all threads are joined
    if sound_controller:  # Check if sound_controller is initialized
        sound_controller.close()
    if saber:  # Check if saber is initialized
        saber.close()


def kill_signal_handler(sig, frame):
    """
    Handle Ctrl+C signal to clean up and exit.
    """
    print("Interrupt received, cleaning up...")
    global threads  # Ensure threads is accessible
    clean(saber, sound_controller, threads)
    sys.exit(0)  # Use sys.exit for a cleaner exit


def detect_road(hsv):
    """
    Detect the road using HSV color filtering and edge detection.
    """
    h_mean, s_mean, v_mean = (
        np.mean(hsv[:, :, 0]),
        np.mean(hsv[:, :, 1]),
        np.mean(hsv[:, :, 2]),
    )
    lower_bound = np.array([h_mean - 10, s_mean - 50, v_mean - 50])
    upper_bound = np.array([h_mean + 10, s_mean + 50, v_mean + 50])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=10)
    return lines


def calculate_steering_angle(lines):
    """
    Calculate the steering angle based on detected road lines.s
    """
    if lines is None:
        return None  # No road detected
    x_coords = [line[0][0] for line in lines] + [line[0][2] for line in lines]
    avg_x = sum(x_coords) // len(x_coords)
    return avg_x - 320  # Offset from the center of the frame


def calculate_steering_angle_weighted(lines):
    if lines is None:
        return None  # No road detected
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)
    return np.mean(angles)  # Average angle


def drive_robot(saber, speed=35, turn=0):
    """
    Drive the robot forward with a specified speed and turn.
    """
    saber.drive(speed, turn)


def follow_sign(saber, sound_controller, sign):
    """
    Follow the direction of the detected sign and announce it.
    """

    def announce_and_execute():
        if sign == "stop":
            print("Sign detected: STOP. Stopping for 10 seconds...")
            sound_controller.play_text_to_speech("Stopping for 10 seconds.")
            saber.stop()
            time.sleep(10)
        elif sign == "left":
            print("Sign detected: LEFT. Turning left...")
            sound_controller.play_text_to_speech("Turning left.")
            saber.drive(35, -45)  # Turn left
            time.sleep(2)
            saber.stop()
        elif sign == "right":
            print("Sign detected: RIGHT. Turning right...")
            sound_controller.play_text_to_speech("Turning right.")
            saber.drive(35, 45)  # Turn right
            time.sleep(2)
            saber.stop()
        elif sign == "forward":
            print("Sign detected: UP. Continuing forward...")
            sound_controller.play_text_to_speech("Continuing forward.")
        else:
            print(f"Unknown sign detected: {sign}. Ignoring...")
            sound_controller.play_text_to_speech("Unknown sign detected. Ignoring.")

    # Run the announcement and action in a separate thread
    threading.Thread(target=announce_and_execute, daemon=True).start()


def sign_detection_thread(cam, model, saber, sound_controller):
    """
    Thread to detect signs and react accordingly.
    """
    while not stop_event.is_set():
        try:
            sign, area = detect_sign_new(cam, model)
            if area >= 14500:  # Check if the sign is of the correct size
                with drive_lock:  # Ensure thread-safe access
                    follow_sign(saber, sound_controller, sign)
            time.sleep(frame_freq)
        except Exception as e:
            print(f"Error in sign detection thread: {e}")


def main():
    global saber, sound_controller, threads  # Declare threads as global
    # Initialize camera, YOLO model, Sabertooth motor controller, and sound controller
    cam, model = initialize()
    saber = Sabertooth()
    saber.set_ramping(15)
    sound_controller = USB_SoundController()

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, kill_signal_handler)

    # Start the sign detection thread
    sign_thread = threading.Thread(
        target=sign_detection_thread,
        args=(cam, model, saber, sound_controller),
        daemon=True,
    )
    sign_thread.start()

    # Keep track of threads
    threads = [sign_thread]

    try:
        print("Starting autonomous driving...")
        while True:
            try:
                # Capture frame and convert to HSV
                frame = cam.capture_array()
                hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

                # Detect road and calculate steering angle
                lines = detect_road(hsv)
                steering_angle = calculate_steering_angle(lines)

                if steering_angle is None:
                    print("End of road detected.")
                    sound_controller.play_text_to_speech("End of road detected.")
                    break

                # Drive the robot based on the steering angle
                turn = steering_angle / 320 * 45  # Scale turn value
                with drive_lock:  # Ensure thread-safe access
                    drive_robot(saber, speed=35, turn=turn)

                time.sleep(0.1)  # Smooth driving loop
            except Exception as e:
                print(f"Error in main driving loop: {e}")

    except KeyboardInterrupt:
        print("Autonomous driving interrupted by user.")

    finally:
        print("Stopping robot and cleaning up...")
        clean(saber, sound_controller, threads)


if __name__ == "__main__":
    main()
