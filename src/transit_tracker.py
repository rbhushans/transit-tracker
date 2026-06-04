#!/usr/bin/env python3

import time
import traceback
from PIL import Image, ImageDraw
from .waveshare_epd import epd4in2_V2
import signal

from . import config
from . import constants
from .data.data_fetcher import fetch_trains
from .views import header, train_anim, train_time, footer

def handle_sigterm(signum, frame):
    raise KeyboardInterrupt()

signal.signal(signal.SIGTERM, handle_sigterm)

def draw_dashboard(epd, trains, refresh_seconds):
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


def main():
    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()

    # last_api_fetch = 0 forces a fetch on the first loop iteration. Keeping the
    # fetch inside the loop (and inside the try below) means a failed fetch can
    # never crash the process before the dashboard is ever drawn.
    last_api_fetch = 0
    trains = []

    try:
        while True:
            try:
                now = time.time()
                elapsed = int(now - last_api_fetch)

                if elapsed >= config.REFRESH_INTERVAL:
                    last_api_fetch = now
                    trains = fetch_trains()
                    elapsed = 0

                if config.DEBUG:
                    trains = fetch_trains()

                refresh_seconds = max(0, config.REFRESH_INTERVAL - elapsed)
                image = draw_dashboard(epd, trains, refresh_seconds)
                epd.display_Partial(epd.getbuffer(image))
                time.sleep(2)

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
        epd.init()
        epd.Clear() 

        time.sleep(0.5)

        epd.sleep()


if __name__ == "__main__":
    main()