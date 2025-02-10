import cv2
from picamera2 import Picamera2
import time
import os

def main():
    # Initialize Picamera2
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1024, 768)})
    picam2.configure(config)
    
    # Start the camera
    picam2.start()
    time.sleep(1)  # Allow the camera to warm up

    # Load the Haar Cascade for face detection
    haar_cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
    if not os.path.exists(haar_cascade_path):
        raise FileNotFoundError(f"Haar cascade file not found at {haar_cascade_path}")
    face_cascade = cv2.CascadeClassifier(haar_cascade_path)

    pre_processed_images = []
    post_processed_images = []

    # Capture 6 photos and process them
    for i in range(6):
        # Capture an image
        frame = picam2.capture_array()

        # Add the original image to pre-processed list
        pre_processed_images.append(frame)

        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Add the processed image to post-processed list
        post_processed_images.append(frame)

        print(f"Image {i+1}: Detected {len(faces)} face(s)")

    # Stop the camera
    picam2.stop()

    # Display all pre-processed and post-processed images side by side
    for i in range(6):
        pre_image = pre_processed_images[i]
        post_image = post_processed_images[i]

        # Resize images to fit within 512x768 each
        pre_image_resized = cv2.resize(pre_image, (512, 768))
        post_image_resized = cv2.resize(post_image, (512, 768))

        # Combine resized images horizontally
        combined_image = cv2.hconcat([pre_image_resized, post_image_resized])

        # Add text overlay to inform the user
        text = "Press any key to view the next set of images."
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        color = (0, 255, 0)
        thickness = 1
        position = (10, 20)
        cv2.putText(combined_image, text, position, font, font_scale, color, thickness)

        # Force the display window to 1024x768
        cv2.namedWindow(f"Image Set {i+1} (Pre-Processed | Post-Processed)", cv2.WINDOW_NORMAL)
        cv2.resizeWindow(f"Image Set {i+1} (Pre-Processed | Post-Processed)", 1024, 768)

        cv2.imshow(f"Image Set {i+1} (Pre-Processed | Post-Processed)", combined_image)
        cv2.waitKey(0)

    # Close all windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
