from .. import constants
from PIL import ImageFont


def draw_train_time(draw, y: int, trains: list) -> None:
    if not trains:
        return
    big_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.TIME_BIG_FONT_SIZE)
    min_font = ImageFont.truetype(constants.FONT_PATH_BOLD, constants.TIME_MIN_FONT_SIZE)

    mins = str(trains[0]['minutes'])
    bw = draw.textbbox((0, 0), mins, font=big_font)[2]

    ty = y + constants.SCREEN_HEIGHT - y - constants.TIME_BOTTOM_OFFSET
    draw.text((constants.TIME_LEFT_PADDING, ty), mins, font=big_font, fill=0)
    draw.text((constants.TIME_LEFT_PADDING + bw + 6, ty + 40), "min", font=min_font, fill=0)

    if len(trains) > 1:
        draw.text((constants.TIME_SECONDARY_X, ty + 40), f"{trains[1]['minutes']} min", font=min_font, fill=0)
