import pygame
import random


def gerar_textura_pedra(largura=64, altura=64):
    """Gera textura procedural de pedra (caverna)"""
    textura = pygame.Surface((largura, altura))
    textura.fill((40, 40, 50))  # Base cinza azulado

    # Ruído
    for y in range(altura):
        for x in range(largura):
            var = random.randint(-15, 15)
            r = max(0, min(255, 40 + var))
            g = max(0, min(255, 40 + var))
            b = max(0, min(255, 50 + var))
            textura.set_at((x, y), (r, g, b))

    # Detalhes (manchas)
    for _ in range(40):
        px = random.randint(0, largura - 1)
        py = random.randint(0, altura - 1)
        cor = (20, 20, 30) if random.random() > 0.5 else (70, 70, 80)
        pygame.draw.circle(textura, cor, (px, py), random.randint(1, 3))
    return textura


def gerar_textura_objetivo(largura=64, altura=64):

    textura = pygame.Surface((largura, altura))
    textura.fill((20, 0, 50))
    centro = largura // 2
    for r in range(centro, 0, -2):
        cor = (min(255, 20 + r * 3), 0, min(255, 50 + r * 4))
        pygame.draw.circle(textura, cor, (centro, centro), r, 1)
    return textura


def gerar_chao_procedural(largura_tela, altura_tela, quantidade=4000):

    pontos = []
    for _ in range(quantidade):
        x = random.randint(0, largura_tela - 1)
        y = random.randint(0, altura_tela - 1)

        tipo = random.random()
        if tipo < 0.6:
            cor = (30, 30, 35)
        elif tipo < 0.8:
            cor = (40, 35, 30)
        else:
            cor = (50, 50, 60)

        pontos.append((x, y, cor))
    return pontos
