import pygame
import sys

from Primitivas import SetPixel, BresenhamReta, Reta, RetaDDA, ScanlineFill, FloodFill, Seno

LARGURA, ALTURA = 800, 600
TITULO = "Teste de Primitivas Gráficas"

PRETO = (0, 0, 0)
BRANCO = (255, 255, 255)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)
AMARELO = (255, 255, 0)
CIANO = (0, 255, 255)
MAGENTA = (255, 0, 255)

def desenhar_primitivas(superficie):
    """
    Função central que chama todos os seus scripts para desenhar na tela.
    """
    
    # ---------------------------------------------------------
    # 1. Teste de SENO (Fundo)
    # ---------------------------------------------------------
    print("Desenhando Seno...")
    # O seu script Seno desenha em preto, então vamos mudar o fundo para cinza claro
    # temporariamente ou alterar a cor no script. 
    # Como o script Seno.py força cor (0,0,0), o ideal seria alterar o script,
    # mas aqui vou deixar o fundo cinza escuro para ver o seno preto.
    superficie.fill((50, 50, 50)) 
    Seno.desenhar_seno(superficie, LARGURA, ALTURA, PRETO)

    # ---------------------------------------------------------
    # 2. Teste de RETAS (Canto Superior Esquerdo)
    # ---------------------------------------------------------
    print("Desenhando Retas...")
    # Reta Ingênua (Vermelho)
    Reta.reta_ingenua(superficie, 20, 20, 200, 50, VERMELHO)
    
    # DDA (Verde)
    RetaDDA.dda(superficie, 20, 60, 200, 90, VERDE)
    
    # Bresenham (Azul) - Usando BresenhamReta.py
    BresenhamReta.bresenham(superficie, 20, 100, 200, 130, AZUL)

    # Cria uma "Legenda" visual simples (linhas verticais indicando início)
    BresenhamReta.bresenham(superficie, 10, 20, 10, 130, BRANCO)

    # ---------------------------------------------------------
    # 3. Teste de SCANLINE (Polígono Preenchido)
    # ---------------------------------------------------------
    print("Executando Scanline...")
    # Definindo um pentágono irregular
    pontos_poligono = [
        (400, 50),  # Topo
        (500, 150), # Direita Cima
        (450, 250), # Direita Baixo
        (350, 250), # Esquerda Baixo
        (300, 150)  # Esquerda Cima
    ]
    ScanlineFill.scanline_fill(superficie, pontos_poligono, AMARELO)
    
    # Desenhar contorno do polígono com Bresenham para acabamento
    for i in range(len(pontos_poligono)):
        p1 = pontos_poligono[i]
        p2 = pontos_poligono[(i + 1) % len(pontos_poligono)]
        BresenhamReta.bresenham(superficie, p1[0], p1[1], p2[0], p2[1], BRANCO)

    # ---------------------------------------------------------
    # 4. Teste de FLOOD FILL (Preenchimento de Região)
    # ---------------------------------------------------------
    print("Executando Flood Fill (pode demorar um pouco)...")
    
    # Primeiro, precisamos criar uma "caixa" fechada para pintar dentro.
    # Se houver buracos, o flood fill vai pintar a tela inteira!
    x_box, y_box = 100, 300
    w_box, h_box = 100, 100
    
    # Desenhando as 4 paredes da caixa com Bresenham (Cor da Borda = BRANCO)
    BresenhamReta.bresenham(superficie, x_box, y_box, x_box + w_box, y_box, BRANCO)           # Topo
    BresenhamReta.bresenham(superficie, x_box, y_box + h_box, x_box + w_box, y_box + h_box, BRANCO) # Baixo
    BresenhamReta.bresenham(superficie, x_box, y_box, x_box, y_box + h_box, BRANCO)           # Esquerda
    BresenhamReta.bresenham(superficie, x_box + w_box, y_box, x_box + w_box, y_box + h_box, BRANCO) # Direita

    # Ponto semente no centro da caixa
    centro_x = x_box + 50
    centro_y = y_box + 50
    
    # Chama o Flood Fill
    # Nota: Seu FloodFill.py pede (x, y, cor_preenchimento, cor_borda)
    FloodFill.flood_fill_iterativo(superficie, centro_x, centro_y, MAGENTA, BRANCO)

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA, ALTURA))
    pygame.display.set_caption(TITULO)

    # Desenha tudo UMA vez no buffer inicial
    desenhar_primitivas(tela)
    
    # Atualiza a tela para mostrar o desenho
    pygame.display.flip()

    print("Renderização concluída. Loop principal iniciado.")

    # Loop principal
    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
        
        # Como é uma imagem estática gerada por algoritmos lentos,
        # não precisamos redesenhar a cada frame, apenas manter a janela aberta.
        # Caso precise redesenhar, chame desenhar_primitivas(tela) aqui,
        # mas a performance cairá drasticamente.
        
        pygame.time.wait(100) # Economiza CPU

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()