def drive_robot(saber, speed=35, turn=0):
    saber.drive(speed, turn)


def drive_distance(saber, speed=35, distance=1):
    """
    Drive the robot forward for a specified distance.
    The distance is approximated based on time and speed.
    """
    # Assuming a linear relationship between speed and distance covered per second
    time_to_drive = distance / (speed / 127)  # Scale time based on speed
    saber.drive(speed, 0)  # Drive forward with no turn
    time.sleep(time_to_drive)  # Drive for the calculated time
    saber.stop()  # Stop the robot after driving


def drive_forward(saber, speed=35, duration=1, turn=0):
    """
    Drive the robot forward at a specified speed for a specified duration.
    """
    for i in range(int(duration * 100)):
        saber.drive(speed, turn)  # Forward with no turning
    # stop_robot(saber)  # Stop after the duration


def stop_robot(saber):
    saber.stop()


def turn_robot(saber, direction, speed=45, duration=1):
    if direction == "left":
        for i in range(int(duration * 70)):
            saber.drive(0, -speed)  # Turn left
    elif direction == "right":
        for i in range(int(duration * 85)):
            saber.drive(0, speed)  # Turn right
    stop_robot(saber)

if __name__ == "__main__":
    import time
    from sabertooth import Sabertooth
    print("Initializing Sabertooth...")
    
    saber = Sabertooth()
    saber.set_ramping(15)
    time.sleep(1)
    print("Starting robot movement...")
    drive_forward(saber, speed=35, duration=2)
    print("Turning left...")
    turn_robot(saber, "left", speed=45, duration=1)
    print("Driving forward...")
    drive_distance(saber, speed=35, distance=1)
    print("Stopping robot...")
    stop_robot(saber)

    saber.close()
    print("Robot movement completed.")