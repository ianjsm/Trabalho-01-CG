from Primitivas.SetPixel import setPixel


def Circulo(superficie, xc, yc, r, cor):
    x = 0
    y = r
    d = 3 - 2 * r

    def desenhar_pontos(xc, yc, x, y):

        setPixel(superficie, xc + x, yc + y, cor)
        setPixel(superficie, xc - x, yc + y, cor)
        setPixel(superficie, xc + x, yc - y, cor)
        setPixel(superficie, xc - x, yc - y, cor)
        setPixel(superficie, xc + y, yc + x, cor)
        setPixel(superficie, xc - y, yc + x, cor)
        setPixel(superficie, xc + y, yc - x, cor)
        setPixel(superficie, xc - y, yc - x, cor)

    desenhar_pontos(xc, yc, x, y)
    while y >= x:
        x += 1
        if d > 0:
            y -= 1
            d = d + 4 * (x - y) + 10
        else:
            d = d + 4 * x + 6
        desenhar_pontos(xc, yc, x, y)
