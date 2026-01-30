from Primitivas.SetPixel import setPixel


def mapear_textura(superficie, pontos, imagem_textura):

    tex_w, tex_h = imagem_textura.get_size()
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    min_x, max_x = int(min(xs)), int(max(xs))
    min_y, max_y = int(min(ys)), int(max(ys))

    largura_poly = max_x - min_x if max_x != min_x else 1
    altura_poly = max_y - min_y if max_y != min_y else 1

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if ponto_em_poligono(x, y, pontos):
                u = (x - min_x) / largura_poly
                v = (y - min_y) / altura_poly
                tex_x = int(u * (tex_w - 1))
                tex_y = int(v * (tex_h - 1))
                try:
                    cor = imagem_textura.get_at((tex_x, tex_y))
                    setPixel(superficie, x, y, cor)
                except IndexError:
                    pass


def scanline_textura_tiled(superficie, pontos, textura, intensidade=1.0):

    if not pontos or not textura:
        return

    tex_w, tex_h = textura.get_size()
    ys = [int(p[1]) for p in pontos]
    y_min = min(ys)
    y_max = max(ys)
    n = len(pontos)

    intensidade = max(0.0, min(1.0, intensidade))

    for y in range(y_min, y_max + 1):
        intersecoes_x = []
        for i in range(n):
            p1 = pontos[i]
            p2 = pontos[(i + 1) % n]
            x1, y1 = int(p1[0]), int(p1[1])
            x2, y2 = int(p2[0]), int(p2[1])

            if y1 == y2:
                continue
            if y1 > y2:
                x1, y1, x2, y2 = x2, y2, x1, y1

            if y >= y1 and y < y2:
                x = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
                intersecoes_x.append(x)

        intersecoes_x.sort()

        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):
                x_inicio = int(intersecoes_x[i])
                x_fim = int(intersecoes_x[i + 1])
                for x in range(x_inicio, x_fim + 1):

                    u = x % tex_w
                    v = y % tex_h
                    cor_original = textura.get_at((u, v))

                    if intensidade < 1.0:
                        r = int(cor_original[0] * intensidade)
                        g = int(cor_original[1] * intensidade)
                        b = int(cor_original[2] * intensidade)
                        setPixel(superficie, x, y, (r, g, b))
                    else:
                        setPixel(superficie, x, y, cor_original)


def ponto_em_poligono(x, y, pontos):
    n = len(pontos)
    dentro = False
    p1x, p1y = pontos[0]
    for i in range(n + 1):
        p2x, p2y = pontos[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        dentro = not dentro
        p1x, p1y = p2x, p2y
    return dentro
