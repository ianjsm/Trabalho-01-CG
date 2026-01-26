import SetPixel

def dda(superficie, x0, y0, x1, y1, cor):
    dx = x1 - x0
    dy = y1 - y0

    passos = max(abs(dx), abs(dy))

    if passos == 0:
        SetPixel.setPixel(superficie, x0, y0, cor)
        return

    x_inc = dx / passos
    y_inc = dy / passos

    x = x0
    y = y0

    for _ in range(passos + 1):
        SetPixel.setPixel(superficie, round(x), round(y), cor)
        x += x_inc
        y += y_inc