from .. import constants
from PIL import ImageFont


def draw_train_time(draw, y: int, trains: list) -> None:
    if not trains:
        return
    big_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.TIME_BIG_FONT_SIZE)
    min_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.TIME_MIN_FONT_SIZE)

    mins = str(trains[0]['minutes'])
    bw = draw.textbbox((0, 0), mins, font=big_font)[2]

    main_h = constants.SCREEN_HEIGHT - y - constants.MAIN_BOTTOM_PADDING
    ty = y + main_h - constants.TIME_BOTTOM_OFFSET
    left_x = constants.PADDING + constants.TIME_LEFT_PADDING
    draw.text((left_x, ty), mins, font=big_font, fill=0)
    draw.text((left_x + bw + 6, ty + 40), "min", font=min_font, fill=0)

    if len(trains) > 1:
        secondary_x = constants.PADDING + constants.TIME_SECONDARY_X
        draw.text((secondary_x, ty + 40), f"{trains[1]['minutes']} min", font=min_font, fill=0)
