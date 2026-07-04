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
    partial_count = 0
    fetch_count = 0
    full_refresh = True
    trains = []

    try:
        while True:
            try:
                now = time.time()

                # refresh data on the fetch interval
                if now - last_api_fetch >= config.REFRESH_INTERVAL:
                    last_api_fetch = now
                    trains = fetch_trains()
                    fetch_count += 1
                    # full-refresh only every Nth fetch; the rest redraw with
                    # (ghost-free) partial refreshes to save the panel and avoid
                    # the flash
                    if (fetch_count - 1) % config.FULL_REFRESH_EVERY_N_FETCHES == 0:
                        full_refresh = True

                if config.DEBUG:
                    trains = fetch_trains()

                elapsed = int(now - last_api_fetch)
                refresh_seconds = max(0, config.REFRESH_INTERVAL - elapsed)
                image = draw_dashboard(epd, trains, refresh_seconds)
                buf = epd.getbuffer(image)

                if full_refresh or partial_count >= config.MAX_PARTIAL_REFRESHES:
                    # Re-init first: partial refreshes leave the border /
                    # update-control registers in partial mode, so without this
                    # the "full" refresh doesn't fully clear. display() also
                    # re-seeds the partial base by writing both RAM banks
                    # (0x24 new-frame and 0x26 previous-frame).
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
                    # the last full refresh and large changes leave ghost trails.
                    epd.send_command(0x26)
                    epd.send_data2(buf)
                    partial_count += 1

                time.sleep(config.DRAW_INTERVAL)

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