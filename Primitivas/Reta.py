from Primitivas.SetPixel import setPixel


def reta_ingenua(superficie, x0, y0, x1, y1, cor):

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0

    if dx == 0:
        return

    m = (y1 - y0) / dx
    b = y0 - m * x0

    for x in range(x0, x1 + 1):
        y = m * x + b
        setPixel(superficie, x, round(y), cor)
