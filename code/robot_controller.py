##########################################################################
# Main Robot Controller for ND Robotics Course
# 3-7-2025
# Professor McLaughlin
##########################################################################
import pygame
import time
from sabertooth import Sabertooth
from ps5_controller import PS5_Controller
# import alarm_routine


start = False

def move_robot(saber, control_request, direction):
    # Sends motor commands to the Sabertooth motor controller.
    speed = control_request["reqLeftJoyYValue"] * -1 * direction
    turn = control_request["reqLeftJoyXValue"]  # * direction
    saber.drive(speed * 2 / 3, turn / 2)


def main():
    direction = 1
    try:
        # Initialize the PS5 Controller class
        ps5 = PS5_Controller()
        ps5.initialize_controller()

        # Initialize Sabertooth motor controller
        saber = Sabertooth()
        saber.set_ramping(40)  # Fast Ramping 1-10, Slow 11-20, Intermediate 21-80
        isMoving = False

        ps5_last_check_time = time.time()
        ps5_loop_interval = 0.02  # 20ms interval

        motor_controller_last_check_time = time.time()
        motor_controller_loop_interval = 0.04  # 40ms interval

        while True:
            current_time = time.time()

            # Check PS5 controller state
            if current_time - ps5_last_check_time >= ps5_loop_interval:
                pygame.event.pump()
                ps5.check_controls()
                ps5_last_check_time = current_time

            # Example: Use Arrow Up as a function call trigger
            if ps5.control_request["reqArrowUp"]:
                print("This should call by function tied to Arrow Up")
                direction *= -1
                # alarm_routine.main()
                

            # Move the robot if left joystick is moved
            if ps5.control_request["reqLeftJoyMade"]:
                if (
                    current_time - motor_controller_last_check_time
                    >= motor_controller_loop_interval
                ):
                    move_robot(saber, ps5.control_request, direction)
                    isMoving = True
                    motor_controller_last_check_time = time.time()
            else:
                if isMoving:
                    isMoving = False
                    saber.stop()

            # Reset PS5 request variables for next loop
            if ps5.control_request["reqMade"]:
                ps5.reset_controller_state()

            # Provide a brief sleep to allow worker threads to catch up to main loop
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("Exiting program...")

    finally:
        pygame.joystick.quit()
        pygame.quit()
        saber.close()
        print("PS5 controller disconnected.")


if __name__ == "__main__":
    main()
