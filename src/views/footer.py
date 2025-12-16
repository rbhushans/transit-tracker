from .. import config
from .. import constants

# the footer component, which is just the refresh progress bar
def draw_footer(draw, refresh_seconds: int) -> None:
    padding = constants.PADDING
    bar_y = constants.SCREEN_HEIGHT - padding - constants.FOOTER_BAR_HEIGHT
    bar_w = int((refresh_seconds / config.REFRESH_INTERVAL) * (constants.SCREEN_WIDTH - 2 * padding))

    _draw_footer_bar(draw, padding, bar_y, bar_w)

def _draw_footer_bar(draw, padding: int, bar_y: int, bar_w: int) -> None:
    draw.rectangle([padding, bar_y, padding + bar_w, bar_y + constants.FOOTER_BAR_HEIGHT], fill=0)
    draw.rectangle([padding + bar_w, bar_y, constants.SCREEN_WIDTH - padding, bar_y + constants.FOOTER_BAR_HEIGHT], outline=0)
