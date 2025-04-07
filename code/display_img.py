from tft_display import TFTDisplay
from picamera2 import Picamera2
import time
import cv2

screen = TFTDisplay()
picam2 = Picamera2()
config = picam2.create_still_configuration(
    main={
        "size": (640, 480),
        "format": "RGB888",
    },  # Small but clear resolution, RGB for ML models
)
picam2.configure(config)
picam2.start()

img = picam2.capture_array()

#screen.clear_screen("black")
#screen.display_bmp_image(img)
#time.sleep(1)
#cv2.imshow("img: ",img)
#cv2.waitKey(0)
#print(img.size)

screen.display_camera_feed(picam2)
