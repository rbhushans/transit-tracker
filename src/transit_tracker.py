#!/usr/bin/env python3

import time
from PIL import Image, ImageDraw
from .waveshare_epd import epd4in2_V2
import RPi.GPIO as GPIO



from . import config
from . import constants
from .data.data_fetcher import fetch_trains
from .views import header, train_anim, train_time, footer

SLEEP_BUTTON_PIN = 40  
REFRESH_BUTTON_PIN = 33 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SLEEP_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(REFRESH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

display_awake = True
manual_refresh = False

def draw_dashboard(trains, refresh_seconds):
    image = Image.new('1', (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT), 255)
    draw = ImageDraw.Draw(image)

    padding = constants.PADDING
    y = padding

    # header
    y += header.draw_header(draw, y)

    # main animation area
    main_h = train_anim.draw_train_anim(draw, y, trains)

    # time elements
    train_time.draw_train_time(draw, y, trains)

    # footer
    footer.draw_footer(draw, refresh_seconds)

    return image

def sleep_display(epd):
    epd.init()
    epd.Clear()
    time.sleep(0.5)
    epd.sleep()

def sleep_button_callback(channel):
    global display_awake
    display_awake = not display_awake
    if not display_awake:
        sleep_display(epd)
    else:
        epd.init() 

def refresh_button_callback(channel):
    global manual_refresh
    manual_refresh = True

def main():
    global epd
    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()

    # Setup button event detection
    GPIO.add_event_detect(SLEEP_BUTTON_PIN, GPIO.FALLING,
                          callback=sleep_button_callback, bouncetime=200)
    GPIO.add_event_detect(REFRESH_BUTTON_PIN, GPIO.FALLING,
                          callback=refresh_button_callback, bouncetime=200)

    last_api_fetch = time.time()
    trains = fetch_trains()
    iterations = 0

    try:
        while True:
            now = time.time()
            elapsed = int(now - last_api_fetch)

            # refresh automatically or manually (but only if display is awake)
            if elapsed >= config.REFRESH_INTERVAL or (manual_refresh and display_awake):
                print("Refreshing train data...")
                last_api_fetch = now
                trains = fetch_trains()
                elapsed = 0
                manual_refresh = False  # reset after refresh

            refresh_seconds = config.REFRESH_INTERVAL - elapsed

            # Only update display if awake
            if display_awake and iterations == 0:
                print("Updating display...")
                image = draw_dashboard(trains, refresh_seconds)
                epd.display_Partial(epd.getbuffer(image))

            iterations = (iterations + 1) % 5 
            time.sleep(0.1) 

    except KeyboardInterrupt:
        print("Exiting... putting display to sleep")

    finally:
        sleep_display(epd)
        GPIO.cleanup()

if __name__ == "__main__":
    main()