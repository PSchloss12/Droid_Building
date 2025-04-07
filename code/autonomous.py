from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
import threading, cv2, time, queue
import numpy as np
from detect_signs import initialize


def announce_sign(sound_controller, sign):
    """
    Follow the direction of the detected sign and announce it.
    """
    if sign == "stop":
        print("Sign detected: STOP. Stopping for 10 seconds...")
        sound_controller.play_text_to_speech("Stopping for 10 seconds.")
    elif sign == "left":
        print("Sign detected: LEFT. Turning left...")
        sound_controller.play_text_to_speech("Turning left.")
    elif sign == "right":
        print("Sign detected: RIGHT. Turning right...")
        sound_controller.play_text_to_speech("Turning right.")
    elif sign == "forward":
        print("Sign detected: forward. Continuing forward...")
        sound_controller.play_text_to_speech("Continuing forward.")
    elif sign == "continue":
        print("Sign too small. Continuing forward...")
        sound_controller.play_text_to_speech("All signs too small")
    else:
        print(f"Unknown sign detected: {sign}. Ignoring...")
        sound_controller.play_text_to_speech("Unknown sign detected. Ignoring.")


def take_picture(
    result_queue, picam2, screen, model, sound, detect_sign=False, display_img=True
):
    """
    Returns the new steering angle unless a large enough sign is detected
    """
    min_sign_area = 14500

    raw_frame = picam2.capture_array()

    frame = None
    if display_img:
        frame = raw_frame.copy()

    largest_sign = None
    steering_angle = None
    if detect_sign:
        results = model(raw_frame)
        largest_area = 0
        for result in results:
            for box in result.boxes:  # Get bounding boxes
                x1, y1, x2, y2 = box.xyxy[0]
                class_name = model.names[int(box.cls)]
                if display_img:
                    cv2.rectangle(
                        frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 0), 2
                    )
                    cv2.putText(
                        frame,
                        f"{class_name} {box.conf[0]:.2f}",
                        (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 0),
                        2,
                    )
                area = (x2 - x1) * (y2 - y1)
                if area > largest_area:
                    largest_area = area
                    largest_sign = class_name
        if largest_area < min_sign_area:
            largest_sign = "continue"
        announce_sign(sound, largest_sign)
    if not detect_sign or not largest_sign or largest_sign == "continue":
        # Calculate lines to follow
        hsv = cv2.cvtColor(raw_frame, cv2.COLOR_RGB2HSV)
        h_mean, s_mean, v_mean = (
            np.mean(hsv[:, :, 0]),
            np.mean(hsv[:, :, 1]),
            np.mean(hsv[:, :, 2]),
        )
        lower_bound = np.array([h_mean - 10, s_mean - 50, v_mean - 50])
        upper_bound = np.array([h_mean + 10, s_mean + 50, v_mean + 50])
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        edges = cv2.Canny(mask, 50, 150)
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=10
        )
        if len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
                angles.append(angle)
                if display_img:
                    cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            steering_angle = np.mean(angles) * 0.14
        if steering_angle and display_img:
            line_length = 50
            x_center = int(frame.shape[1] / 2)
            y_bottom = int(frame.shape[0])
            x_end = int(x_center + line_length * np.sin(np.radians(steering_angle)))
            y_end = int(y_bottom - line_length * np.cos(np.radians(steering_angle)))
            cv2.line(
                frame,
                (x_center, y_bottom),  # Start point (bottom center of the frame)
                (x_end, y_end),  # End point (based on steering angle)
                (255, 255, 0),  # Cyan color (BGR format)
                2,  # Line thickness
            )

    if display_img:
        screen.clear_screen("white")
        screen.display_bmp_image(frame, position=(0, 0))

    if steering_angle:
        result_queue.put(steering_angle)
    result_queue.put(largest_sign)


def drive_robot(saber, speed=35, turn=0):
    saber.drive(speed, turn)


def drive_distance(saber, speed=35, distance=1):
    """
    Drive the robot forward for a specified distance.
    The distance is approximated based on time and speed.
    """
    # Assuming a linear relationship between speed and distance covered per second
    time_to_drive = distance / (speed / 127)  # Scale time based on speed
    saber.drive(speed, 0)  # Drive forward with no turn
    time.sleep(time_to_drive)  # Drive for the calculated time
    saber.stop()  # Stop the robot after driving


def drive_forward(saber, speed=35, duration=1):
    """
    Drive the robot forward at a specified speed for a specified duration.
    """
    for i in range(int(duration * 100)):
        saber.drive(speed, 0)  # Forward with no turning
    stop_robot(saber)  # Stop after the duration


def stop_robot(saber):
    saber.stop()


def turn_robot(saber, direction, speed=45, duration=1):
    if direction == "left":
        for i in range(int(duration * 75)):
            saber.drive(0, -speed)  # Turn left
    elif direction == "right":
        for i in range(int(duration * 75)):
            saber.drive(0, speed)  # Turn right
    stop_robot(saber)


def follow_sign(saber, sign):
    if sign == "stop":
        stop_robot(saber)
        time.sleep(2)
    elif sign == "left":
        drive_forward(saber, duration=1.25)  # Move forward for 2 seconds before turning
        turn_robot(saber, "left")
    elif sign == "right":
        drive_forward(saber, duration=1.3)  # Move forward for 2 seconds before turning
        turn_robot(saber, "right")


def clean(saber, screen, sound):
    """
    Clean up the resources and stop the robot.
    """
    saber.close()
    screen.close()
    sound.close()


if __name__ == "__main__":
    cam, model = initialize()
    sound = USB_SoundController()
    saber = Sabertooth()
    screen = TFTDisplay()
    saber.set_ramping(15)
    result_queue = queue.Queue()

    count = 0
    turn = 0
    while 1:
        try:
            count += 1
            if count % 100 == 0:
                pic_thread = threading.Thread(
                    target=take_picture,
                    args=(result_queue, cam, screen, model, sound, True),
                    daemon=True,
                )
                pic_thread.start()
                pic_thread.join()
                if not result_queue.empty():
                    ret = result_queue.get()
                    if not ret:
                        print("end of road. exiting...")
                        break
                    elif type(ret) == str:
                        follow_sign(saber, ret)
                    else:
                        turn = ret
            elif count % 10 == 0:
                pic_thread = threading.Thread(
                    target=take_picture,
                    args=(result_queue, cam, screen, model, sound, False),
                    daemon=True,
                )
                pic_thread.start()
                pic_thread.join()
                if not result_queue.empty():
                    ret = result_queue.get()
                    turn = float(ret)
            drive_robot(saber, speed=20, turn=turn)
            turn = 0
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    clean(saber, screen, sound)
