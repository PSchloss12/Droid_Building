from picamera2 import Picamera2
import time
from ultralytics import YOLO
# import cv2
from ColorPrint import color_print

def initialize():
    '''
    returns camera, model
    '''
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (640, 480), "format": "RGB888"},  # Small but clear resolution, RGB for ML models
    )
    picam2.configure(config)
    picam2.start()
    model = YOLO('yolo11n.tflite')
    return picam2, model

def detect_sign(cam, model):
    '''
    NB: only returns if only one class detected
    '''
    color_print('Analyzing picture',"cyan")
    frame = cam.capture_array()
    results = model(frame)
    detected_classes = []
    for result in results:
        for cls_id in result.boxes.cls:  # Get class indices
            if model.names[int(cls_id)] not in detected_classes:
                detected_classes.append(model.names[int(cls_id)])
    color = 'green' if len(detected_classes)>0 else 'red'
    print("Detected:", end=' ')
    color_print(detected_classes, color)
    if len(detected_classes) == 1:
        return str(detected_classes[0])
    return ""

def detect_sign_new(cam, model):
    '''
    Returns the largest detected object of any class
    '''
    min_area = 400
    color_print('Analyzing picture', "cyan")

    sign = None
    for i in range(2):
        frame = cam.capture_array()
        results = model(frame)
        
        largest_obj = None
        largest_area = 0
        
        for result in results:
            for box in enumerate(result.boxes):  # Get bounding boxes
                print(box)
                print(type(box))
                # Calculate area of the bounding box
                x1, y1, x2, y2 = box[0].xyxy.tolist()
                area = (x2 - x1) * (y2 - y1)
                if area<min_area:
                    color_print('signs too small','red')
                    return ""
                class_name = model.names[int(box.cls)]                
                if area > largest_area:
                    largest_area = area
                    largest_obj = class_name
        if not sign:
            sign = largest_obj
        if largest_obj!=sign:
            color_print(f'[{sign},{largest_obj}]','red')
            return ""
        time.sleep(0.01)
    color = 'green' if largest_obj else 'red'
    print("Detected:", end=' ')
    color_print([sign] if sign else [], color)
    return str(largest_obj) if largest_obj else ""

if __name__ == '__main__':
    # Initialize Picamera2
    print("Configure camera...")
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (640, 480), "format": "RGB888"},  # Small but clear resolution, RGB for ML models
        lores={"size": (320, 240)},  # Optional low-res for faster preview if needed
        display="lores"  # Use low-res for previewing (if using)
    )
    picam2.configure(config)
    picam2.start()
    # load model
    print('Loading YOLO model...')
    version = 'yolo11n.tflite'
    model = YOLO(version)
    print('Model loaded!')

    while 1:
        d_class = detect_sign_new(model,picam2)
        print(d_class)
        # color_print('Analyzing picture',"cyan")
        # frame = picam2.capture_array()
        # results = model(frame)
        # detected_classes = []
        # for result in results:
        #     for cls_id in result.boxes.cls:  # Get class indices
        #         if model.names[int(cls_id)] not in detected_classes:
        #             detected_classes.append(model.names[int(cls_id)])
        # color = 'green' if len(detected_classes)>0 else 'red'
        # print("Detected:", end=' ')
        # color_print(detected_classes, color)

        time.sleep(1)
