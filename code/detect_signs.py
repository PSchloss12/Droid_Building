from picamera2 import Picamera2
import time
from ultralytics import YOLO
# import cv2
from ColorPrint import color_print

def initialize():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (640, 480), "format": "RGB888"},  # Small but clear resolution, RGB for ML models
        lores={"size": (320, 240)},  # Optional low-res for faster preview if needed
        display="lores"  # Use low-res for previewing (if using)
    )
    picam2.configure(config)
    picam2.start()
    model = YOLO('yolo11n.tflite')
    return picam2, model

def detect_sign(cam, model):
    '''
    NB: only returns first detected class atm
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
    return detected_classes[0]

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
    model = YOLO('yolo11n.tflite')
    print('Model loaded!')

    while 1:
        color_print('Analyzing picture',"cyan")
        frame = picam2.capture_array()
        results = model(frame)
        detected_classes = []
        for result in results:
            for cls_id in result.boxes.cls:  # Get class indices
                if model.names[int(cls_id)] not in detected_classes:
                    detected_classes.append(model.names[int(cls_id)])
        color = 'green' if len(detected_classes)>0 else 'red'
        print("Detected:", end=' ')
        color_print(detected_classes, color)

        time.sleep(0.5)