import torch
import cv2
import numpy as np
from pathlib import Path
from picamera2 import Picamera2
from models.common import DetectMultiBackend
from utils.augmentations import letterbox
from utils.general import non_max_suppression
from utils.torch_utils import select_device

def rescale_coords(img1_shape, coords, img0_shape):
    """Rescale coords (xyxy) from img1_shape to img0_shape"""
    gain = min(img1_shape[0] / img0_shape[0], img1_shape[1] / img0_shape[1])
    pad = ((img1_shape[1] - img0_shape[1] * gain) / 2, (img1_shape[0] - img0_shape[0] * gain) / 2)
    coords[:, [0, 2]] -= pad[0]  # x padding
    coords[:, [1, 3]] -= pad[1]  # y padding
    coords[:, :4] /= gain
    coords = coords.clamp(min=0)
    return coords

# Initialize model
weights = "best-4.pt"  # make sure this path is correct
device = select_device('cpu')  # or '0' if you're using CUDA

model = DetectMultiBackend(weights, device=device)
stride, names, pt = model.stride, model.names, model.pt
imgsz = (416, 1184)  # Height: 416, Width: 1184 ? both divisible by 32
model.warmup(imgsz=(1, 3, *imgsz))

# Set up camera
picam2 = Picamera2()
picam2.preview_configuration.main.size = (1280, 736)
picam2.preview_configuration.main.format = "RGB888"
picam2.configure("preview")
picam2.start()

while True:
    # Capture and preprocess
    frame = picam2.capture_array()
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
            det[:, :4] = rescale_coords(im.shape[2:], det[:, :4], frame.shape).round()

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
                refined_pred = model(crop_tensor, augment=False)
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



    cv2.imshow("YOLOv5 - Pi Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

picam2.close()
cv2.destroyAllWindows()
