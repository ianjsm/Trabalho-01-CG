from Primitivas.SetPixel import setPixel

def lerp_cor(cor1, cor2, t):
    """Mistura duas cores baseado em um fator t (0.0 a 1.0)"""
    r = int(cor1[0] + (cor2[0] - cor1[0]) * t)
    g = int(cor1[1] + (cor2[1] - cor1[1]) * t)
    b = int(cor1[2] + (cor2[2] - cor1[2]) * t)
    return (r, g, b)

def scanline_fill(superficie, pontos, cor_inicio, cor_fim=None):
    """
    Se cor_fim for fornecido, faz um gradiente vertical.
    Se não, faz preenchimento sólido com cor_inicio.
    """
    if not pontos: return
    
    ys = [p[1] for p in pontos]
    y_min = int(min(ys))
    y_max = int(max(ys))
    n = len(pontos)
    
    altura_total = y_max - y_min if y_max != y_min else 1

    for y in range(y_min, y_max + 1):
        intersecoes_x = []

        for i in range(n):
            x0, y0 = pontos[i]
            x1, y1 = pontos[(i + 1) % n]

            if y0 == y1: continue

            if y0 > y1:
                x0, y0, x1, y1 = x1, y1, x0, y0

            if y < y0 or y >= y1:
                continue

            x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            intersecoes_x.append(x)

        intersecoes_x.sort()

        # Define a cor da linha (Sólida ou Gradiente)
        if cor_fim:
            t = (y - y_min) / altura_total
            cor_atual = lerp_cor(cor_inicio, cor_fim, t)
        else:
            cor_atual = cor_inicio

        for i in range(0, len(intersecoes_x), 2):
            if i + 1 < len(intersecoes_x):
                x_inicio = int(round(intersecoes_x[i]))
                x_fim = int(round(intersecoes_x[i + 1]))

                for x in range(x_inicio, x_fim + 1):
                    setPixel(superficie, x, y, cor_atual)