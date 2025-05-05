from picamera2 import Picamera2
import time
from ultralytics import YOLO
import cv2

# import cv2
from ColorPrint import color_print


def initialize():
    """
    returns camera, model
    """
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={
            # "size": (480, 320),
            "size": (1020, 320),
            "format": "RGB888",
        },  # Small but clear resolution, RGB for ML models
    )
    time.sleep(1)
    picam2.configure(config)
    picam2.start()
    model = YOLO("models/best.pt")  # Load a model
    # model = YOLO("models/4_29.tflite")  # Load a model
    # model = YOLO("models/yolo11n.tflite")  # Load a model
    # model = YOLO('best_float32_old.tflite')
    return picam2, model


def detect_sign(frame, model):
    """
    NB: only returns if only one class detected.
    Returns the detected class and the area of the detected box.
    """
    results = model(frame)
    detected_class = None
    largest_area = 0

    for result in results:
        for box in result.boxes:  # Get bounding boxes
            x1, y1, x2, y2 = box.xyxy[0]
            area = (x2 - x1) * (y2 - y1)
            if area > largest_area:
                largest_area = area
                detected_class = model.names[int(box.cls)]
    color = "green" if detected_class else "red"
    print("Detected:", end=" ")
    color_print(detected_class, color)
    return str(detected_class), largest_area


def annotate_frame(frame, results):
    """
    Annotate the frame with bounding boxes and labels
    """
    for result in results:
        for box in result.boxes:  # Get bounding boxes
            x1, y1, x2, y2 = box.xyxy[0]
            class_name = model.names[int(box.cls)]
            confidence = box.conf[0]
            # Draw bounding box and label on the frame
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
            cv2.putText(
                frame,
                f"{class_name} {confidence:.2f}",
                (int(x1), int(y1) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2,
            )
    return frame


def detect_sign_new(cam, model):
    """
    Returns the largest detected object of any class
    """
    min_area = 30000
    color_print("Analyzing picture", "cyan")

    sign = None
    area = 0
    frame = None
    results = None
    for i in range(2):
        frame = cam.capture_array()
        results = model(frame)

        largest_obj = None
        largest_area = 0
        for result in results:
            for box in result.boxes:  # Get bounding boxes
                # Calculate area of the bounding box
                x1, y1, x2, y2 = box.xyxy[0]
                area = (x2 - x1) * (y2 - y1)
                class_name = model.names[int(box.cls)]
                if area > largest_area:
                    largest_area = area
                    largest_obj = class_name
        print(largest_area)
        area = max(largest_area, area)
        if not sign:
            sign = largest_obj
        if largest_obj != sign:
            color_print(f"[{sign},{largest_obj}]", "red")
            return ("", 0, None)
        time.sleep(0.01)
    frame = annotate_frame(frame, results)
    color = "green" if largest_obj else "red"
    print("Detected:", end=" ")
    color_print([sign] if sign else [], color)
    return (str(sign), area, frame) if sign else ("", 0, None)


if __name__ == "__main__":
    # Initialize Picamera2
    picam2, model = initialize()
    frame = picam2.capture_array()

    print('model loaded successfully')
    time.sleep(1)
    print()
    results = model(frame)
    largest_area = 0
    for result in results:
        if len(result.boxes) > 1:
            print("Warning: More than one sign detected. Ignoring all signs.")
            continue
        for box in result.boxes:  # Get bounding boxes
            x1, y1, x2, y2 = box.xyxy[0]
            class_name = model.names[int(box.cls)]
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
    cv2.imshow("Annotated Steering Overlay", frame)
    key = cv2.waitKey(0)