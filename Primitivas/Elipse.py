from Primitivas.SetPixel import setPixel


def elipse_ponto_medio(superficie, xc, yc, rx, ry, cor):
    x = 0
    y = ry

    d1 = (ry**2) - (rx**2 * ry) + (0.25 * rx**2)
    dx = 2 * ry**2 * x
    dy = 2 * rx**2 * y

    while dx < dy:
        setPixel(superficie, xc + x, yc + y, cor)
        setPixel(superficie, xc - x, yc + y, cor)
        setPixel(superficie, xc + x, yc - y, cor)
        setPixel(superficie, xc - x, yc - y, cor)
        if d1 < 0:
            x += 1
            dx = dx + (2 * ry**2)
            d1 = d1 + dx + (ry**2)
        else:
            x += 1
            y -= 1
            dx = dx + (2 * ry**2)
            dy = dy - (2 * rx**2)
            d1 = d1 + dx - dy + (ry**2)

    d2 = ((ry**2) * ((x + 0.5) ** 2)) + ((rx**2) * ((y - 1) ** 2)) - (rx**2 * ry**2)
    while y >= 0:
        setPixel(superficie, xc + x, yc + y, cor)
        setPixel(superficie, xc - x, yc + y, cor)
        setPixel(superficie, xc + x, yc - y, cor)
        setPixel(superficie, xc - x, yc - y, cor)
        if d2 > 0:
            y -= 1
            dy = dy - (2 * rx**2)
            d2 = d2 + (rx**2) - dy
        else:
            y -= 1
            x += 1
            dx = dx + (2 * ry**2)
            dy = dy - (2 * rx**2)
            d2 = d2 + dx - dy + (rx**2)
