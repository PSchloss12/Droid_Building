from picamera2 import Picamera2
import time
# from ultralytics import YOLO
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import non_max_suppression
from utils.torch_utils import select_device
import cv2
from detect_signs import initialize

def predict_img(frame, model):
    img = letterbox(frame, imgsz, stride=stride, auto=True)[0]
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)

    im = torch.from_numpy(img).to(device)
    im = im.float() / 255.0
    im = im.unsqueeze(0)

    # Inference
    pred = model(im, augment=False)
    pred = non_max_suppression(pred, conf_thres=0.25, iou_thres=0.45)

    for det in pred:
        if len(det):
            for *xyxy, conf, cls in reversed(det):
                # Original prediction
                orig_label = names[int(cls)]
                orig_conf = float(conf)

                # Crop the bounding box area from the frame
                x1, y1, x2, y2 = map(int, xyxy)
                cropped = frame[y1:y2, x1:x2]

                # Preprocess the cropped image
                crop_img = letterbox(cropped, imgsz, stride=stride, auto=True)[0]
                crop_img = crop_img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
                crop_img = np.ascontiguousarray(crop_img)
                crop_tensor = torch.from_numpy(crop_img).to(device).float() / 255.0
                crop_tensor = crop_tensor.unsqueeze(0)

                # Run model again on cropped image
                refined_pred = model(crop_img)
                refined_pred = non_max_suppression(refined_pred, conf_thres=0.25, iou_thres=0.45)

                # Use first refined detection if available
                if refined_pred and len(refined_pred[0]):
                    refined_box = refined_pred[0][0]
                    refined_conf = float(refined_box[4])
                    refined_cls = int(refined_box[5])
                    refined_label = names[refined_cls]

                    # Apply your confidence-based override rule
                    if refined_label != orig_label and refined_conf >= 0.5 * orig_conf:
                        final_label = refined_label
                        final_conf = refined_conf
                    else:
                        final_label = orig_label
                        final_conf = orig_conf
                else:
                    final_label = orig_label
                    final_conf = orig_conf

                # Draw box and label
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, f"{final_label} ({final_conf:.2f})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                return final_label, frame

if __name__ == "__main__":
    cam, _ = initialize()
    weights = "best-4.pt"  # make sure this path is correct
    device = select_device('cpu')  # or '0' if you're using CUDA

    model = DetectMultiBackend(weights, device=device)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = (416, 1184)  # Height: 416, Width: 1184 ? both divisible by 32

    while True:
        raw_frame = picam2.capture_array()
        label, frame = predict_img(raw_frame, model)
        cv2.imshow("Annotated Steering Overlay", frame)
        key = cv2.waitKey(1) & 0xFF
        time.sleep(1)