import pygame
import random
from Primitivas import Circulo, FloodFill, ScanlineFill, SetPixel


def gerar_textura_pedra(largura=64, altura=64):
    textura = pygame.Surface((largura, altura))
    for y in range(altura):
        for x in range(largura):
            var = random.randint(-15, 15)
            r = max(0, min(255, 40 + var))
            g = max(0, min(255, 40 + var))
            b = max(0, min(255, 50 + var))
            SetPixel.setPixel(textura, x, y, (r, g, b))

    for _ in range(40):
        px = random.randint(2, largura - 3) 
        py = random.randint(2, altura - 3)
        cor = (20, 20, 30) if random.random() > 0.5 else (70, 70, 80)
        raio = random.randint(1, 3)
        Circulo.Circulo(textura, px, py, raio, cor)
        FloodFill.flood_fill_iterativo(textura, px, py, cor, cor)

    return textura

def gerar_textura_objetivo(largura=64, altura=64):
    textura = pygame.Surface((largura, altura))
    cor_fundo = (20, 0, 50)
    pontos_fundo = [(0, 0), (largura-1, 0), (largura-1, altura-1), (0, altura-1)]
    ScanlineFill.scanline_fill(textura, pontos_fundo, cor_fundo)
    centro = largura // 2
    for r in range(centro, 0, -2):
        px = random.randint(5, largura - 5)
        py = random.randint(5, altura - 5)
        cor = (min(255, 20 + r * 3), 0, min(255, 50 + r * 4))
        raio = random.randint(1, 3)
        Circulo.Circulo(textura, px, py, raio, cor)
        FloodFill.flood_fill_iterativo(textura, px, py, cor, cor)
        
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
