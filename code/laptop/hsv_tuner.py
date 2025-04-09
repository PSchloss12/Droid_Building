import cv2
import numpy as np


def nothing(x):
    pass

def hsv_tuner_image(image_path):
    cv2.namedWindow("HSV Tuner")

    # Create trackbars for HSV range
    cv2.createTrackbar("H Min", "HSV Tuner", 20, 179, nothing)
    cv2.createTrackbar("H Max", "HSV Tuner", 35, 179, nothing)
    cv2.createTrackbar("S Min", "HSV Tuner", 100, 255, nothing)
    cv2.createTrackbar("S Max", "HSV Tuner", 255, 255, nothing)
    cv2.createTrackbar("V Min", "HSV Tuner", 100, 255, nothing)
    cv2.createTrackbar("V Max", "HSV Tuner", 255, 255, nothing)

    frame = cv2.imread(image_path)
    if frame is None:
        print(f"Error: Could not read image {image_path}")
        return

    frame = cv2.resize(frame, (640, 480))

    while True:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Get current positions of all trackbars
        h_min = cv2.getTrackbarPos("H Min", "HSV Tuner")
        h_max = cv2.getTrackbarPos("H Max", "HSV Tuner")
        s_min = cv2.getTrackbarPos("S Min", "HSV Tuner")
        s_max = cv2.getTrackbarPos("S Max", "HSV Tuner")
        v_min = cv2.getTrackbarPos("V Min", "HSV Tuner")
        v_max = cv2.getTrackbarPos("V Max", "HSV Tuner")

        # Mask with current HSV range
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Stack images for display
        stacked = np.hstack((frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), result))
        cv2.imshow("HSV Tuner", stacked)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):  # Quit tuning
            break
        elif key == ord("p"):  # Print current HSV range
            print(f"Lower HSV: {lower.tolist()}")
            print(f"Upper HSV: {upper.tolist()}")

    cv2.destroyAllWindows()

def hsv_tuner():
    cap = cv2.VideoCapture(0)  # Laptop webcam (use 1 if external camera)

    cv2.namedWindow("HSV Tuner")

    # Create trackbars for HSV range
    cv2.createTrackbar("H Min", "HSV Tuner", 20, 179, nothing)
    cv2.createTrackbar("H Max", "HSV Tuner", 35, 179, nothing)
    cv2.createTrackbar("S Min", "HSV Tuner", 100, 255, nothing)
    cv2.createTrackbar("S Max", "HSV Tuner", 255, 255, nothing)
    cv2.createTrackbar("V Min", "HSV Tuner", 100, 255, nothing)
    cv2.createTrackbar("V Max", "HSV Tuner", 255, 255, nothing)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Get current positions of all trackbars
        h_min = cv2.getTrackbarPos("H Min", "HSV Tuner")
        h_max = cv2.getTrackbarPos("H Max", "HSV Tuner")
        s_min = cv2.getTrackbarPos("S Min", "HSV Tuner")
        s_max = cv2.getTrackbarPos("S Max", "HSV Tuner")
        v_min = cv2.getTrackbarPos("V Min", "HSV Tuner")
        v_max = cv2.getTrackbarPos("V Max", "HSV Tuner")

        # Mask with current HSV range
        lower = np.array([h_min, s_min, v_min])
        upper = np.array([h_max, s_max, v_max])
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        # Stack images for display
        stacked = np.hstack((frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), result))
        cv2.imshow("HSV Tuner", stacked)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("p"):
            print(f"Lower HSV: {lower.tolist()}")
            print(f"Upper HSV: {upper.tolist()}")

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    # hsv_tuner()
    hsv_tuner_image("../data/road_0.jpg")
