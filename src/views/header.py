import config
import constants
from PIL import ImageFont
import datetime

def _draw_line_logo(draw, cx: int, cy: int) -> None:
    n_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.HEADER_N_FONT_SIZE)
    bbox = draw.textbbox((0, 0), config.HEADER_N_LABEL, font=n_font)
    ascent, _ = n_font.getmetrics()
    text_h = bbox[3] - bbox[1]

    draw.ellipse([
        cx - constants.CIRCLE_RADIUS,
        cy - constants.CIRCLE_RADIUS,
        cx + constants.CIRCLE_RADIUS,
        cy + constants.CIRCLE_RADIUS,
    ], outline=0, width=2)

    draw.text(
        (cx - (bbox[2] - bbox[0]) // 2,
         cy - text_h // 2 - ascent // 6 - 2),
    config.HEADER_N_LABEL,
        font=n_font,
        fill=0,
    )

def _draw_destination(draw, x: int, y: int) -> None:
    small_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.HEADER_SMALL_FONT_SIZE)
    draw.text((x + constants.CIRCLE_RADIUS + 10, y + 8), config.HEADER_DESTINATION_LABEL, font=small_font, fill=0)

def _draw_now_local(draw, y: int) -> None:
    small_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.HEADER_SMALL_FONT_SIZE)
    now_local = datetime.datetime.now().strftime("%-I:%M %p")
    tw = draw.textbbox((0, 0), now_local, font=small_font)[2]
    draw.text((constants.SCREEN_WIDTH - constants.PADDING - tw - 5, y + 8), now_local, font=small_font, fill=0)

def draw_header(draw, y: int) -> int:
    padding = constants.PADDING
    header_h = constants.HEADER_HEIGHT

    cx = padding + 25
    cy = y + header_h // 2

    draw.rectangle([padding, y, constants.SCREEN_WIDTH - padding, y + header_h], outline=0)

    _draw_line_logo(draw, cx, cy)
    _draw_destination(draw, cx, y)
    _draw_now_local(draw, y)

    return header_h + 6
