from sabertooth import Sabertooth
from usb_sound_controller import USB_SoundController
from led_controller import LEDController
from tft_display import TFTDisplay
import threading, cv2, time, queue
import numpy as np
from detect_signs import initialize
from add_lines import *
from drive import *
from handle_sign import announce_sign, follow_sign

speed = 20
turn_speed = 1


def take_picture(
    result_queue, picam2, screen, model, sound, detect_sign=True, display_img=True
):
    """
    Returns the new steering angle unless a large enough sign is detected
    """
    min_sign_area = 14500

    raw_frame = picam2.capture_array()

    largest_sign = None

    frame, steering_point, slope, is_intersection = process_image_with_steering_overlay(
        raw_frame
    )
    if steering_point[0] == -1 and steering_point[1] == -1 and not is_intersection:
        cv2.imshow("Annotated Steering Overlay", frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        result_queue.put(None)
        return

    # if is_intersection:
    # cv2.imshow("Annotated Steering Overlay", frame)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    if False and detect_sign and is_intersection:
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
            largest_sign = None
        else:
            announce_sign(sound, largest_sign)

    if display_img:
        screen.clear_screen("white")
        screen.display_bmp_image(frame, position=(0, 0))
        # cv2.imshow("Annotated Steering Overlay", frame)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    if largest_sign is not None:
        result_queue.put(largest_sign)
    x, y = steering_point
    # print(frame.shape)
    steering_angle = np.arctan2(y, x - frame.shape[1] // 2)
    if abs(slope) <= 2:
        steering_angle = 7 if slope > 0 else -7
    else:
        steering_angle = 0
    # steering_angle = int(x - (frame.shape[1] // 2))
    result_queue.put(steering_angle)


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
    ready = True
    while 1:
        print(count)
        try:
            count += 1
            # if count % 10 == 0:
            if ready:
                ready = False
                show = False  # count%100==0
                pic_thread = threading.Thread(
                    target=take_picture,
                    args=(result_queue, cam, screen, model, sound, True, show),
                    daemon=True,
                )
                pic_thread.start()
                pic_thread.join()
                if not result_queue.empty():
                    ret = result_queue.get()
                    if ret is None:
                        print("end of road. exiting...")
                        break
                    elif type(ret) == str:
                        follow_sign(saber, ret)
                        ready = True
                    else:
                        ready = True
                        try:
                            turn = (
                                float(ret) * turn_speed
                            )  # Attempt to cast ret to a float
                        except ValueError:
                            print(
                                f"Warning: Unable to cast ret ({ret}) to float. Ignoring this value."
                            )
                            turn = 0  # Default to 0 if casting fails
                else:
                    print("No result from queue. Continuing...")
            # elif count % 10 == 0:
            #     pic_thread = threading.Thread(
            #         target=take_picture,
            #         args=(result_queue, cam, screen, model, sound, False),
            #         daemon=True,
            #     )
            #     pic_thread.start()
            #     pic_thread.join()
            #     if not result_queue.empty():
            #         ret = result_queue.get()
            #         if ret is not None:
            #             turn = float(ret)
            print(f"Steering angle: {turn} ", ready)
            drive_robot(saber, speed=speed, turn=turn)
            turn = 0
        except KeyboardInterrupt:
            print("Exiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    clean(saber, screen, sound)
