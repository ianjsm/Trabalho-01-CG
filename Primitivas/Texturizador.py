from Primitivas.SetPixel import setPixel

def mapear_textura(superficie, pontos, imagem_textura):
    """
    Preenche um polígono com uma textura de imagem.
    imagem_textura: um objeto pygame.Surface carregado.
    """
    # 1. Obter dimensões da textura
    tex_w, tex_h = imagem_textura.get_size()
    
    # 2. Achar a Bounding Box do polígono na tela
    xs = [p[0] for p in pontos]
    ys = [p[1] for p in pontos]
    min_x, max_x = int(min(xs)), int(max(xs))
    min_y, max_y = int(min(ys)), int(max(ys))
    
    largura_poly = max_x - min_x if max_x != min_x else 1
    altura_poly = max_y - min_y if max_y != min_y else 1

    # 3. Percorrer a Bounding Box (Otimizável com Scanline, mas aqui é mais didático)
    for y in range(min_y, max_y + 1):
        # Aqui poderíamos usar a lógica do seu Scanline para achar o x_inicio e x_fim
        # Para simplificar e garantir o mapeamento:
        for x in range(min_x, max_x + 1):
            if ponto_em_poligono(x, y, pontos):
                # 4. Calcular coordenadas U, V (0.0 a 1.0) baseadas na posição do polígono
                u = (x - min_x) / largura_poly
                v = (y - min_y) / altura_poly
                
                # 5. Pegar a cor da textura (coordenadas da imagem)
                tex_x = int(u * (tex_w - 1))
                tex_y = int(v * (tex_h - 1))
                cor = imagem_textura.get_at((tex_x, tex_y))
                
                setPixel(superficie, x, y, cor)

def ponto_em_poligono(x, y, pontos):
    """Algoritmo de Ray Casting para checar se o pixel está dentro do polígono"""
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