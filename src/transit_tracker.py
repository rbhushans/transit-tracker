#!/usr/bin/env python3

import time
from PIL import Image, ImageDraw
from .waveshare_epd import epd4in2_V2

from . import config
from . import constants
from .data.data_fetcher import fetch_trains
from .views import header, train_anim, train_time, footer


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

    last_api_fetch = time.time()
    trains = fetch_trains()

    try:
        while True:
            now = time.time()
            elapsed = int(now - last_api_fetch)

            if elapsed >= config.REFRESH_INTERVAL:
                last_api_fetch = now
                trains = fetch_trains()
                elapsed = 0

            if config.DEBUG:
                trains = fetch_trains()

            refresh_seconds = config.REFRESH_INTERVAL - elapsed
            image = draw_dashboard(epd, trains, refresh_seconds)
            epd.display_Partial(epd.getbuffer(image))  
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting... putting display to sleep")

    finally:
        epd.init()
        epd.Clear() 

        time.sleep(0.5)

        epd.sleep()


if __name__ == "__main__":
    main()