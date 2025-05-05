from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
import threading, cv2, time, queue
import numpy as np
from detect_signs import initialize
from add_lines import *
from drive import *
from autonomous import clean
from handle_sign import announce_sign, follow_sign

def is_on_grass(cam):
    frame = cam.capture_array()
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([35, 100, 130])
    upper_green = np.array([60, 155, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    total_pixels = mask.size
    green_pixels = cv2.countNonZero(mask)
    print(f"Green pixels/Total pixels: {total_pixels}/{green_pixels}, {100*green_pixels/total_pixels:.2f}")
    if green_pixels > 0.02 * total_pixels:
        print(f"Detected grass with {green_pixels} green pixels")
        return True
    else:
        return False

def recenter_on_road(saber, picam2, turn_speed=1.5):
    slope = 0
    count = 0
    while abs(slope) <= 3 and count < 3:
        raw_frame = picam2.capture_array()
        frame, steering_point, slope, is_intersection = process_image_with_steering_overlay(
            raw_frame
        )
        cv2.imshow("Annotated Steering Overlay", frame)
        key = cv2.waitKey(1) & 0xFF
        # # key = cv2.waitKey(0)
        time.sleep(1)

        # turn = float(slope) * turn_speed *2
        # drive_forward(saber, speed=speed, duration=1, turn=turn)
        # drive_forward(saber, speed=speed*-1, duration=1, turn=turn)
        drive_forward(saber, speed=20, duration=1, turn=1)
        print(f"slope: {slope}, turn: {turn}")

def take_picture(picam2, screen, model, sound, detect_sign=True, display_img=True):
    """
    Returns the new steering angle unless a large enough sign is detected
    """
    min_sign_area = 13000
    min_stop_sign_area = 18000
    # min_sign_area = 0

    raw_frame = picam2.capture_array()

    largest_sign = ""

    frame, steering_point, slope, is_intersection = process_image_with_steering_overlay(
        raw_frame
    )
    if steering_point[0] == -1 and steering_point[1] == -1 and not is_intersection:
        cv2.imshow("Annotated Steering Overlay", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    # if is_intersection:
    # cv2.imshow("Annotated Steering Overlay", frame)
    # key = cv2.waitKey(1) & 0xFF

    if detect_sign:
        results = model(raw_frame)
        largest_area = 0
        for result in results:
            if len(result.boxes) > 1:
                print("Warning: More than one sign detected. Ignoring all signs.")
                continue
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
        # NB: stop sign bounding boxes produced by the model are larger than the others
        if largest_sign.lower == "stop" and largest_area < min_stop_sign_area:
            largest_sign = ""
        elif largest_sign.lower != "stop" and largest_area < min_sign_area:
            largest_sign = ""
        else:
            announce_sign(sound, largest_sign)
        print(
            f"largest sign: {largest_sign}, area: {largest_area}, min_sign_area: {min_sign_area}"
        )

    if display_img:
        # screen.clear_screen("white")
        # screen.display_bmp_image(frame, position=(0, 0))
        cv2.imshow("Annotated Steering Overlay", frame)
        key = cv2.waitKey(1) & 0xFF

    if largest_sign != "":
        return largest_sign.lower()

    # x, y = steering_point
    # steering_angle = np.arctan2(y, x - frame.shape[1] // 2)
    if abs(slope) <= 3:
        steering_angle = -10 if slope > 0 else 7
    else:
        steering_angle = 0
    # steering_angle = int(x - (frame.shape[1] // 2))
    return steering_angle


if __name__ == "__main__":
    cam, model = initialize()
    sound = USB_SoundController()
    saber = Sabertooth()
    screen = TFTDisplay()
    saber.set_ramping(15)

    speed = 25
    turn_speed = 1.2

    try:
        turn = 0
        speed = 25
        while 1:
            ret = take_picture(cam, screen, model, sound)
            # print(ret, type(ret))
            if ret is None:
                if not is_on_grass(cam):
                    print("end of road. exiting...")
                    break
                else:
                    turn_robot(saber, "left", duration=0.3)
            elif type(ret) == str:
                print(f"Detected sign: {ret}")
                follow_sign(saber, ret)
                # sound.play_text_to_speech(f"Recentering on road")
                # recenter_on_road(saber, cam, turn_speed=turn_speed)
            else:
                try:
                    turn = float(ret) * turn_speed  # Attempt to cast ret to a float
                except ValueError:
                    print(
                        f"Warning: Unable to cast ret ({ret}) to float. Ignoring this value."
                    )
                    turn = 0
            # drive_robot(saber, speed=speed, turn=turn)
            drive_forward(saber, speed=speed, duration=0.5, turn=turn)
            turn = 0
    except Exception as e:
        print(e)
    finally:
        clean(saber, screen, sound)
