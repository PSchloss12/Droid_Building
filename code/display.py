    def display_camera_feed(self, camera, delay=0.1):
        """
        Continuously display the camera feed on the TFT screen.

        :param camera: An instance of Picamera2.
        :param delay: Time delay between frames in seconds.
        """
        try:
            while True:
                # Capture a frame from the camera
                frame = camera.capture_array()

                # Ensure the frame is resized to fit the screen dimensions
                if frame.shape[:2] != (SCREEN_HEIGHT, SCREEN_WIDTH):
                    frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))

                # Convert the frame to RGB format and display it
                self.display_bmp_image(frame)

                # Add a small delay to control the frame rate
                time.sleep(delay)
        except KeyboardInterrupt:
            print("Camera feed display interrupted.")
        except Exception as e:
            print("Error displaying camera feed:", e)