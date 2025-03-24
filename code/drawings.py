from time import sleep


def draw_crest(tft_display):
    """
    Draws a simplified version of the 2019-Crest-Navy image using the tft_display functions.
    """
    # Clear the screen
    tft_display.clear_screen("navy")

    # Draw the shield base
    tft_display.draw_box(
        top_left=(20, 20),
        bottom_right=(108, 140),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),  # Navy blue
    )

    # Draw the top battlements
    tft_display.draw_box(
        top_left=(20, 10),
        bottom_right=(40, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )
    tft_display.draw_box(
        top_left=(50, 10),
        bottom_right=(70, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )
    tft_display.draw_box(
        top_left=(80, 10),
        bottom_right=(100, 20),
        line_color=(0, 0, 0),
        fill_color=(0, 0, 128),
    )

    # Draw the vertical and horizontal green cross
    tft_display.draw_box(
        top_left=(60, 20),
        bottom_right=(68, 140),
        line_color=(0, 255, 0),
        fill_color=(0, 255, 0),  # Green
    )
    tft_display.draw_box(
        top_left=(20, 70),
        bottom_right=(108, 78),
        line_color=(0, 255, 0),
        fill_color=(0, 255, 0),  # Green
    )

    # Draw the top-left quadrant (anchor symbol placeholder)
    tft_display.draw_circle(
        center=(40, 50),
        radius=15,
        line_color=(255, 255, 255),
        fill_color=(255, 255, 255),  # White
    )
    tft_display.draw_text(
        "⚓", position=(35, 40), font_size=18, color=(0, 0, 128)
    )  # Anchor symbol

    # Draw the top-right quadrant (striped pattern)
    for i in range(20, 50, 5):
        tft_display.draw_line(
            start=(70 + i, 20),
            end=(70, 20 + i),
            line_width=1,
            color=(192, 192, 192),  # Light gray
        )

    # Draw the bottom-left quadrant (striped pattern)
    for i in range(20, 50, 5):
        tft_display.draw_line(
            start=(20 + i, 78),
            end=(20, 78 + i),
            line_width=1,
            color=(192, 192, 192),  # Light gray
        )

    # Draw the bottom-right quadrant (helmet placeholder)
    tft_display.draw_circle(
        center=(80, 110),
        radius=15,
        line_color=(128, 128, 128),
        fill_color=(128, 128, 128),  # Gray
    )
    tft_display.draw_text(
        "🛡", position=(75, 100), font_size=18, color=(0, 255, 0)
    )  # Helmet symbol

    # Draw the central "D" emblem
    tft_display.draw_circle(
        center=(64, 78),
        radius=10,
        line_color=(192, 192, 192),
        fill_color=(192, 192, 192),  # Light gray
    )
    tft_display.draw_text(
        "D", position=(60, 70), font_size=14, color=(0, 0, 128)
    )  # "D" in the center


def draw_castle(tft_display):
    """
    Draws a simple castle using the drawing functions from tft_display.py.
    """
    # Clear the screen
    tft_display.clear_screen("black")

    # Draw the base of the castle
    tft_display.draw_box(
        top_left=(20, 100),
        bottom_right=(108, 150),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the left tower
    tft_display.draw_box(
        top_left=(20, 60),
        bottom_right=(50, 100),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the right tower
    tft_display.draw_box(
        top_left=(78, 60),
        bottom_right=(108, 100),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw battlements on the left tower
    tft_display.draw_box(
        top_left=(20, 50),
        bottom_right=(30, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )
    tft_display.draw_box(
        top_left=(40, 50),
        bottom_right=(50, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw battlements on the right tower
    tft_display.draw_box(
        top_left=(78, 50),
        bottom_right=(88, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )
    tft_display.draw_box(
        top_left=(98, 50),
        bottom_right=(108, 60),
        line_color=(255, 255, 255),
        fill_color=(128, 128, 128),
    )

    # Draw the castle door
    tft_display.draw_box(
        top_left=(60, 120),
        bottom_right=(80, 150),
        line_color=(255, 255, 255),
        fill_color=(64, 32, 0),
    )

    # Draw a flag on the left tower
    tft_display.draw_line(
        start=(35, 50), end=(35, 30), line_width=2, color=(255, 255, 255)
    )
    tft_display.draw_box(
        top_left=(35, 30),
        bottom_right=(45, 40),
        line_color=(255, 0, 0),
        fill_color=(255, 0, 0),
    )


def draw_crown(tft):
    # Clear the screen with a black background
    tft.clear_screen("black")

    # Draw the base of the crown
    tft.draw_box(
        top_left=(50, 160),
        bottom_right=(190, 180),
        line_color=(255, 215, 0),
        fill_color=(255, 215, 0),
    )  # Gold base

    # Draw the peaks of the crown using lines
    # Left peak
    tft.draw_line(start=(50, 160), end=(70, 120), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(70, 120), end=(90, 160), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(90, 160), end=(50, 160), line_width=1, color=(255, 215, 0))

    # Middle peak
    tft.draw_line(start=(90, 160), end=(120, 100), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(120, 100), end=(150, 160), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(150, 160), end=(90, 160), line_width=1, color=(255, 215, 0))

    # Right peak
    tft.draw_line(start=(150, 160), end=(170, 120), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(170, 120), end=(190, 160), line_width=1, color=(255, 215, 0))
    tft.draw_line(start=(190, 160), end=(150, 160), line_width=1, color=(255, 215, 0))

    # Add jewels to the peaks
    tft.draw_circle(
        center=(70, 115), radius=5, line_color=(255, 0, 0)
    )  # Left jewel (red)
    tft.draw_circle(
        center=(120, 95), radius=5, line_color=(0, 255, 0)
    )  # Middle jewel (green)
    tft.draw_circle(
        center=(170, 115), radius=5, line_color=(0, 0, 255)
    )  # Right jewel (blue)

    # Display some decorative text
    tft.draw_text("Royal Crown", position=(90, 200), font_size=18, color=(0, 255, 255))
    sleep(1)
