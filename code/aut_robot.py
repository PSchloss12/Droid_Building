import time
from smbus2 import SMBus
import serial
import threading
from detect_signs import initialize, detect_sign

# Setup I2C comms channel for PS5 Controller
I2C_BUS = 1  # I2C bus number (typically 1 on Raspberry Pi)
I2C_ADDRESS = 0x08  # I2C address of the Arduino Mega ADK

# Setup serial comms for all other messages
serial_port = "/dev/ttyAMA0"    # Points to the serial PINs on Raspberry Pi
baud_rate = 115200              # Set baud rate

stop_event = threading.Event() # Used to gracefully stop threads on program exit

# Initialize the serial connection for all non-PS5 comms
try:
    ser = serial.Serial(serial_port, baud_rate, timeout=1)
    print(f"Serial port {serial_port} opened at {baud_rate} baud.")
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

# Used to send all non-PS5 data to the Arduino - appends '%' to all messages for consistent terminator
def send_serial_message(ser, message):
    try:
        # Add the terminator '%'
        full_message = message + "%"

        # Send the message over serial
        ser.write(full_message.encode('utf-8'))
        print(f"Sent via Serial: {full_message}")

    except serial.SerialException as e:
        print(f"Error sending message: {e}")

def inbound_serial_loop():
    global stop_event
    inboundBuffer = ""

    while True:
        data = ser.read().decode('utf-8', errors='ignore')
        if data:
            inboundBuffer += data
            # Check if the message ends with '%'
            if inboundBuffer.endswith('%'):
                print("Received message:", inboundBuffer[:-1])  # Print message without '%'

                # Check for Arduino send back mesage
                if inboundBuffer[: -1] == "SysLive":
                    print("Arduino is live and sending back data")
                                
                # Check your additional messages here and set your state variables

                inboundBuffer = ""  # Clear the buffer for the next message
                
        if stop_event.is_set():
            break


def camera_loop(ser):
    global stop_event
    camera, model = initialize() # initialize camera
    last_check_time = time.time()
    loop_interval = 1  # 20ms interval  
    while True:
        current_time = time.time()
        if current_time - last_check_time >= loop_interval:
            last_check_time = current_time
            direction = detect_sign(camera, model)
            print(direction)
            if direction:
                send_serial_message(ser, direction.upper())
        if stop_event.is_set():
            break

def main():
    try:
        # Let the Arduino know we are running
        send_serial_message(ser, "SysLive")
        time.sleep(1)
        global stop_event
                   
        camera_process_thread = threading.Thread(target = camera_loop, args=(ser,), daemon=True)
        inbound_serial_thread = threading.Thread(target = inbound_serial_loop, daemon=True)

        camera_process_thread.start()
        inbound_serial_thread.start()
        
        while True:
           # Waiting while robotic thread routines run
           do_nothing = True
            
    except KeyboardInterrupt:
        print("Exiting program...")

    finally:
        # Cleanup
        stop_event.set()
        camera_process_thread.join()
        inbound_serial_thread.join()
        ser.close()
        print("PS5 controller disconnected.")


if __name__ == "__main__":
    main()
