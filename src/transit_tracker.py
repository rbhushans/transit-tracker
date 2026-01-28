#!/usr/bin/env python3

import time
from PIL import Image, ImageDraw
from .waveshare_epd import epd4in2_V2
import RPi.GPIO as GPIO
import signal
import traceback

from . import config
from . import constants
from .data.data_fetcher import fetch_trains
from .views import header, train_anim, train_time, footer

def handle_sigterm(signum, frame):
    raise KeyboardInterrupt()

signal.signal(signal.SIGTERM, handle_sigterm)

SLEEP_BUTTON_PIN = 40  
REFRESH_BUTTON_PIN = 33 

GPIO.setmode(GPIO.BOARD)
GPIO.setup(SLEEP_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(REFRESH_BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

display_awake = True
manual_refresh = False
full_refresh = False
epd = None

def draw_dashboard(trains, refresh_seconds):
    image = Image.new(
        '1',
        (constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        255
    )
    draw = ImageDraw.Draw(image)

    y = constants.PADDING

    # header
    y += header.draw_header(draw, y)

    # main animation area
    train_anim.draw_train_anim(draw, y, trains)

    # time elements
    train_time.draw_train_time(draw, y, trains)

    # footer
    footer.draw_footer(draw, refresh_seconds)

    return image

def enter_partial_mode(epd):
    epd.init_Partial()

def sleep_display(epd):
    epd.init()
    epd.Clear()
    time.sleep(0.5)
    epd.sleep()

def wake_display(epd):
    epd.init()
    epd.Clear()
    enter_partial_mode(epd)

def sleep_button_callback(channel):
    global display_awake

    print("Sleep button pressed")
    display_awake = not display_awake
    if not display_awake:
        sleep_display(epd)
    else:
        wake_display(epd)

def refresh_button_callback(channel):
    global manual_refresh

    print("Manual refresh triggered")
    manual_refresh = True

def main():
    global epd
    global display_awake
    global manual_refresh
    global full_refresh

    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()
    enter_partial_mode(epd)

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
            if (elapsed >= config.REFRESH_INTERVAL or manual_refresh) and display_awake:
                print("Refreshing train data...")
                last_api_fetch = now
                trains = fetch_trains()
                full_refresh = True
                elapsed = 0
                manual_refresh = False  # reset after refresh

            refresh_seconds = config.REFRESH_INTERVAL - elapsed

            # Only update display if awake
            if display_awake and iterations == 0:
                image = draw_dashboard(trains, refresh_seconds)
                image = image.rotate(180)
                # full refresh if we've just fetched new train data
                if full_refresh:
                    epd.display(epd.getbuffer(image))
                    enter_partial_mode(epd)
                    full_refresh = False
                else:
                    epd.display_Partial(epd.getbuffer(image))

            iterations = (iterations + 1) % 20 
            time.sleep(0.1) 

    except KeyboardInterrupt:
        print("Exiting... putting display to sleep")

    finally:
        sleep_display(epd)
        GPIO.cleanup()

if __name__ == "__main__":
    main()