import cv2
from picamera2 import Picamera2
import time
import sys
import os
import re

def get_next_image_number(directory, base_name, extension="jpg"):
    pattern = re.compile(rf"{re.escape(base_name)}_(\d+)\.{extension}$")

    # Extract numbers from existing files
    numbers = []
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            match = pattern.match(filename)
            if match:
                numbers.append(int(match.group(1)))  # Extract number

    # Find the next available number
    next_number = max(numbers) + 1 if numbers else 0
    return next_number

def help():
    print(f"python3 capture_image.py image_base_name num_images")
    exit()

def main():
    if len(sys.argv) != 3:
        help()
    
    try:
        num_images = int(sys.argv[2])
    except Exception as ex:
        print(ex)
        help()

    out_dir = "data"
    base_name = sys.argv[1]
    extension = "jpg"
    image_number = get_next_image_number(directory=out_dir, base_name=base_name, extension=extension)

    # Initialize Picamera2
    picam2 = Picamera2()
    config = picam2.create_still_configuration(
        main={"size": (1024, 640), "format": "RGB888"},  # Small but clear resolution, RGB for ML models
        lores={"size": (320, 240)},  # Optional low-res for faster preview if needed
        display="lores"  # Use low-res for previewing (if using)
    )
    picam2.configure(config)
    
    # Start the camera
    picam2.start()
    time.sleep(1)  # Allow the camera to warm up

    for i in range(num_images):
        # Capture image
        picam2.capture_file(f"{out_dir}/{base_name}_{image_number+i}.{extension}")
        time.sleep(0.3)

    # Stop the camera
    picam2.stop()

if __name__ == "__main__":
    main()
