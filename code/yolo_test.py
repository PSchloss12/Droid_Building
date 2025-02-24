from ultralytics import YOLO
import cv2

def preprocess_image(frame):
    frame = cv2.imread(frame)
    if frame is None:
        print("❌ OpenCV failed to load the image.")
    ret = cv2.resize(frame, (640, 480))
    cv2.imshow("Displayed Image", ret)
    cv2.waitKey(0)  # Wait indefinitely until a key is pressed
    cv2.destroyAllWindows()  # Close the window
    return ret

model = YOLO('yolo11n.tflite')  # best_float32
# model.train(data='mnist160', epochs=3)  # train the model
print('Press enter to process...')
frame = preprocess_image('data\\left_1.jpg')
results = model(frame)  # predict on an image

detected_class_names = []
for result in results:
    for cls_id in result.boxes.cls:  # Get class indices
        if model.names[int(cls_id)] not in detected_class_names:
            detected_class_names.append(model.names[int(cls_id)])

print("Detected objects:", detected_class_names)


# detections = results[0].boxes.xyxy
# print(detections)