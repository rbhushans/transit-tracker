
from .. import constants
from .. import config
import datetime
from ..utils.draw_utils import draw_train_icon


def _compute_rounded_minutes(now: datetime.datetime, expected: datetime.datetime) -> int:
    delta = (expected - now).total_seconds()
    if delta <= 0:
        return 0
    mins = int(delta // 60)
    secs = delta - (mins * 60)
    if secs >= 30:
        mins += 1
    return mins


def draw_train_anim(draw, y: int, trains: list) -> int:
    padding = constants.PADDING
    main_h = constants.SCREEN_HEIGHT - y - constants.MAIN_BOTTOM_PADDING
    draw.rectangle([padding, y, constants.SCREEN_WIDTH - padding, y + main_h], outline=0)

    now = datetime.datetime.now(datetime.timezone.utc)
    for t in trains:
        t['minutes'] = _compute_rounded_minutes(now, t['expected_arrival'])

    line_y = y + constants.LINE_Y_OFFSET
    start_x = padding + constants.START_X_OFFSET
    end_x = constants.SCREEN_WIDTH - padding - constants.END_X_OFFSET

    draw.line([start_x, line_y, end_x, line_y], fill=0, width=3)
    draw.ellipse([end_x - 5, line_y - 5, end_x + 5, line_y + 5], fill=0)

    for x in range(end_x + 8, end_x + 30, 6):
        draw.line([x, line_y, x + 2, line_y], fill=0)

    for t in trains:
        if t['minutes'] > config.MAX_TRAIN_MINUTES:
            continue
        ratio = t['minutes'] / config.MAX_TRAIN_MINUTES
        cx = end_x - ratio * (end_x - start_x)
        cx = max(start_x + constants.TRAIN_ICON_BASE_OFFSET, min(cx, end_x))
        draw_train_icon(draw, cx, line_y - constants.TRAIN_ICON_BASE_OFFSET)

    return main_h
