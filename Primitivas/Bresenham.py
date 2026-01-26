import SetPixel

def bresenham(superficie, x0, y0, x1, y1, cor):
    steep = abs(y1 - y0) > abs(x1 - x0)
    if steep:
        x0, y0 = y0, x0
        x1, y1 = y1, x1

    if x0 > x1:
        x0, x1 = x1, x0
        y0, y1 = y1, y0

    dx = x1 - x0
    dy = y1 - y0

    ystep = 1 if dy >= 0 else -1
    dy = abs(dy)

    d = 2 * dy - dx
    incE = 2 * dy
    incNE = 2 * (dy - dx)

    y = y0
    for x in range(x0, x1 + 1):
        if steep:
            SetPixel.setPixel(superficie, y, x, cor)
        else:
            SetPixel.setPixel(superficie, x, y, cor)

        if d > 0:
            y += ystep
            d += incNE
        else:
            d += incE