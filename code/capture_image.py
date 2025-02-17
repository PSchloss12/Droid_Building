import cv2
from picamera2 import Picamera2
import time
import sys

def help():
    print(f"python3 capture_image.py num_images")
    exit()

def main():
    if len(sys.argv) != 2:
        help()
    
    try:
        num_images = int(num_images)
    except Exception as ex:
        print(ex)
        help()

    # Initialize Picamera2
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (640, 480), "format": "RGB888"},  # Small but clear resolution, RGB for ML models
        lores={"size": (320, 240)},  # Optional low-res for faster preview if needed
        display="lores"  # Use low-res for previewing (if using)
    )
    picam2.configure(config)
    
    # Start the camera
    picam2.start()
    time.sleep(1)  # Allow the camera to warm up

    for i in range(num_images):
        # Capture image
        picam2.capture_file("image.jpg")
        time.sleep(0.3)

    # Stop the camera
    picam2.stop()

if __name__ == "__main__":
    main()
