# draws a small train icon
def draw_train_icon(draw, cx: int, base_y: int) -> None:
    width = 30
    height = 12
    x = int(cx - width / 2)

    draw.rectangle([x, base_y - height, x + width, base_y], fill=0)
    draw.rectangle([x + width - 6, base_y - height + 2, x + width, base_y - 2], fill=0)

    for i in range(3):
        wx = x + 4 + i * 8
        draw.rectangle([wx, base_y - height + 3, wx + 4, base_y - height + 7], fill=255)

    for wx in (x + 4, x + 12, x + 20):
        draw.ellipse([wx, base_y, wx + 4, base_y + 4], fill=0)
