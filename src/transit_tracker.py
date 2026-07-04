#!/usr/bin/env python3

import time
import threading
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
toggle_sleep = False
epd = None

# Set by GPIO callbacks to wake the main loop immediately on a button press,
# so the loop can sleep until the next scheduled redraw instead of busy-polling.
wake_event = threading.Event()

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

def sleep_display(epd):
    epd.init()
    epd.Clear()
    time.sleep(0.5)
    epd.sleep()

def wake_display(epd):
    epd.init()
    epd.Clear()

def sleep_button_callback(channel):
    # Only raise a flag here. GPIO callbacks run on a separate thread, and
    # touching the EPD's SPI bus from two threads at once corrupts transfers,
    # so the actual sleep/wake display work is done by the main loop.
    global toggle_sleep

    print("Sleep button pressed")
    toggle_sleep = True
    wake_event.set()

def refresh_button_callback(channel):
    global manual_refresh

    print("Manual refresh triggered")
    manual_refresh = True
    wake_event.set()

def main():
    global epd
    global display_awake
    global manual_refresh
    global full_refresh
    global toggle_sleep

    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()
    # initially, we want a full refresh
    full_refresh = True

    # Setup button event detection
    GPIO.add_event_detect(SLEEP_BUTTON_PIN, GPIO.FALLING,
                          callback=sleep_button_callback, bouncetime=200)
    GPIO.add_event_detect(REFRESH_BUTTON_PIN, GPIO.FALLING,
                          callback=refresh_button_callback, bouncetime=200)

    # last_api_fetch = 0 forces a fetch on the first loop iteration. Keeping the
    # fetch inside the loop (and inside the try below) means a failed fetch can
    # never crash the process before the dashboard is ever drawn.
    last_api_fetch = 0
    last_draw = 0
    partial_count = 0
    trains = []

    try:
        while True:
            try:
                now = time.time()

                # Handle the sleep button here (not in the GPIO callback) so all
                # display/SPI access stays on this single thread.
                if toggle_sleep:
                    toggle_sleep = False
                    display_awake = not display_awake
                    if display_awake:
                        wake_display(epd)
                        full_refresh = True
                        last_draw = 0
                    else:
                        sleep_display(epd)

                # refresh data automatically or manually (only while awake)
                if display_awake and (now - last_api_fetch >= config.REFRESH_INTERVAL or manual_refresh):
                    print("Refreshing train data...")
                    last_api_fetch = now
                    trains = fetch_trains()
                    full_refresh = True
                    manual_refresh = False  # reset after refresh

                # redraw on a fixed cadence (for the progress bar / clock), or
                # immediately after a data refresh or a wake
                if display_awake and (full_refresh or now - last_draw >= config.DRAW_INTERVAL):
                    elapsed = int(now - last_api_fetch)
                    refresh_seconds = max(0, config.REFRESH_INTERVAL - elapsed)
                    image = draw_dashboard(trains, refresh_seconds)
                    image = image.rotate(180)
                    buf = epd.getbuffer(image)

                    # full refresh after new data / on wake, or periodically to
                    # clear the ghosting that builds up from partial refreshes
                    if full_refresh or partial_count >= config.MAX_PARTIAL_REFRESHES:
                        # Re-init first: partial refreshes leave the border /
                        # update-control registers in partial mode, so without
                        # this the "full" refresh doesn't fully clear. display()
                        # also re-seeds the partial base by writing both RAM
                        # banks (0x24 new-frame and 0x26 previous-frame).
                        epd.init()
                        epd.Clear()
                        epd.display(buf)
                        full_refresh = False
                        partial_count = 0
                    else:
                        epd.display_Partial(buf)
                        # display_Partial only writes the new-frame RAM (0x24) and
                        # diffs it against the previous-frame RAM (0x26). Copy this
                        # frame into 0x26 so the NEXT partial diffs against what's
                        # actually on screen — otherwise every partial diffs against
                        # the last full refresh and large changes (the progress bar)
                        # leave ghost trails.
                        epd.send_command(0x26)
                        epd.send_data2(buf)
                        partial_count += 1

                    last_draw = now

                # Sleep until the next scheduled redraw, or until a button press
                # wakes us early. While asleep, wait indefinitely (no busy poll).
                if display_awake:
                    timeout = max(0, config.DRAW_INTERVAL - (time.time() - last_draw))
                else:
                    timeout = None
                wake_event.wait(timeout)
                wake_event.clear()

            except KeyboardInterrupt:
                raise
            except Exception:
                # A transient failure (display glitch, unexpected data, etc.)
                # must not kill the process and trigger a systemd restart loop.
                traceback.print_exc()
                print("Recovered from error; continuing in 2s...")
                time.sleep(2)

    except KeyboardInterrupt:
        print("Exiting... putting display to sleep")

    finally:
        sleep_display(epd)
        GPIO.cleanup()

if __name__ == "__main__":
    main()