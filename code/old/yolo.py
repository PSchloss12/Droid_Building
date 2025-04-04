import cv2
import numpy as np
import serial
from ultralytics import YOLO

# Initialize serial communication with Arduino
arduino = serial.Serial('/dev/ttyUSB0', 9600)  # Adjust port and baud rate

# Load YOLO model
model = YOLO("best.pt")

# Preprocess the frame
def preprocess_image(frame):
    frame = cv2.resize(frame, (640, 480))
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return hsv

# Detect road signs
def detect_sign(frame):
    results = model(frame)
    detections = results[0].boxes.xyxy
    if len(detections) > 0:
        return detections
    return None

# Detect the road
def detect_road(hsv):
    lower_bound = np.array([20, 100, 100])  # Adjust based on road color
    upper_bound = np.array([30, 255, 255])
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, minLineLength=50, maxLineGap=10)
    return lines

# Calculate steering angle
def calculate_steering_angle(lines):
    if lines is None:
        return 0  # Default angle
    x_coords = [line[0][0] for line in lines] + [line[0][2] for line in lines]
    avg_x = sum(x_coords) // len(x_coords)
    return avg_x - 320

# Send command to Arduino
def send_command(command):
    arduino.write((command + "\n").encode())
    print("Sent:", command)

# Main function
def main():
    cap = cv2.VideoCapture(0)  # Replace with your camera index
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        hsv = preprocess_image(frame)
        
        # Check for road signs
        detections = detect_sign(frame)
        if detections is not None:
            send_command("STOP")  # Example: Send stop command if sign detected
        else:
            # Detect the road
            lines = detect_road(hsv)
            steering_angle = calculate_steering_angle(lines)
            
            if steering_angle < -10:
                send_command("LEFT")
            elif steering_angle > 10:
                send_command("RIGHT")
            else:
                send_command("FORWARD")

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
