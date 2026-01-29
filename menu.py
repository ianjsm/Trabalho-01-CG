import pygame
from Primitivas import BresenhamReta, Circulo, Elipse, FloodFill, ScanlineFill

ABERTURA = 0
MENU = 1
SAIR = 2
estado_atual = ABERTURA

def desenhar_abertura(superficie, largura, altura):
    # Paleta de Cores
    FUNDO = (15, 0, 0)
    PELE_PALIDA = (200, 200, 200)
    PRETO_TOTAL = (0, 0, 0) 
    VERMELHO_GOLA = (180, 0, 0)
    BRANCO = (255, 255, 255)
    VERMELHO_VIVO = (255, 0, 0)
    VERMELHO_SANGUE = (130, 0, 0)
    
    superficie.fill(FUNDO)

    # --- TÍTULO DO JOGO ---
    fonte_titulo = pygame.font.Font(None, 64)
    texto_titulo = fonte_titulo.render("ECHO", True, (200, 0, 0))
    rect_titulo = texto_titulo.get_rect(center=(largura // 2, 80))
    superficie.blit(texto_titulo, rect_titulo)

    # --- 1. CAPA (SCANLINE) ---
    gola_esq = [(250, 400), (400, 450), (400, 300), (200, 200)]
    ScanlineFill.scanline_fill(superficie, gola_esq, VERMELHO_GOLA)
    gola_dir = [(550, 400), (400, 450), (400, 300), (600, 200)]
    ScanlineFill.scanline_fill(superficie, gola_dir, VERMELHO_GOLA)

    # --- 2. ROSTO E CABELO ---
    # Cabelo (Fundo da cabeça)
    pontos_cabelo = [(300, 380), (300, 200), (350, 150), (450, 150), (500, 200), (500, 380)]
    ScanlineFill.scanline_fill(superficie, pontos_cabelo, PRETO_TOTAL)

    # Rosto
    pontos_rosto = [(320, 220), (480, 220), (500, 380), (400, 520), (300, 380)]
    ScanlineFill.scanline_fill(superficie, pontos_rosto, PELE_PALIDA)
    
    # Bico do cabelo na testa
    bico_cabelo = [(320, 220), (480, 220), (400, 280)]
    ScanlineFill.scanline_fill(superficie, bico_cabelo, PRETO_TOTAL)

    # --- 3. OLHOS COM PUPILAS ---
    # Globo ocular
    Elipse.elipse_ponto_medio(superficie, 365, 310, 25, 12, VERMELHO_VIVO)
    Elipse.elipse_ponto_medio(superficie, 435, 310, 25, 12, VERMELHO_VIVO)
    FloodFill.flood_fill_iterativo(superficie, 365, 310, VERMELHO_SANGUE, VERMELHO_VIVO)
    FloodFill.flood_fill_iterativo(superficie, 435, 310, VERMELHO_SANGUE, VERMELHO_VIVO)

    # Pupilas
    Circulo.Circulo(superficie, 365, 310, 5, PRETO_TOTAL)
    Circulo.Circulo(superficie, 435, 310, 5, PRETO_TOTAL)
    FloodFill.flood_fill_iterativo(superficie, 365, 310, PRETO_TOTAL, PRETO_TOTAL)
    FloodFill.flood_fill_iterativo(superficie, 435, 310, PRETO_TOTAL, PRETO_TOTAL)

    # --- 4. BOCA E PRESAS ---
    # Linha da Boca (Uma reta escura)
    COR_BOCA = (50, 10, 10)
    BresenhamReta.bresenham(superficie, 360, 420, 440, 420, COR_BOCA)

    # Função auxiliar para desenhar a presa saindo da linha da boca
    def desenhar_presa(x, y):
        BresenhamReta.bresenham(superficie, x, y, x+10, y, BRANCO) # Base na boca
        BresenhamReta.bresenham(superficie, x, y, x+5, y+20, BRANCO)   # Lado esquerdo da ponta
        BresenhamReta.bresenham(superficie, x+10, y, x+5, y+20, BRANCO) # Lado direito da ponta
        # Preenchimento branco
        FloodFill.flood_fill_iterativo(superficie, x+5, y+5, BRANCO, BRANCO)

    desenhar_presa(370, 420)
    desenhar_presa(420, 420)

def desenhar_botao(superficie, x, y, w, h, cor_borda, cor_fundo):
    # Borda
    BresenhamReta.bresenham(superficie, x, y, x+w, y, cor_borda)
    BresenhamReta.bresenham(superficie, x, y, x, y+h, cor_borda)
    BresenhamReta.bresenham(superficie, x+w, y, x+w, y+h, cor_borda)
    BresenhamReta.bresenham(superficie, x, y+h, x+w, y+h, cor_borda)

    # Preenchimento
    ScanlineFill.scanline_fill(
        superficie,
        [(x+1,y+1),(x+w-1,y+1),(x+w-1,y+h-1),(x+1,y+h-1)],
        cor_fundo
    )

def mouse_sobre(mx, my, x, y, w, h):
    return x <= mx <= x+w and y <= my <= y+h

def desenhar_menu(superficie, mouse_pos):
    FUNDO = (10, 0, 0)
    BORDA = (255, 0, 0)
    FUNDO_BTN = (60, 0, 0)
    HOVER = (120, 0, 0)
    TEXTO = (255, 255, 255)

    superficie.fill(FUNDO)

    bx, bw, bh = 300, 200, 60
    by_play = 250
    by_quit = 340

    mx, my = mouse_pos

    # PLAY
    cor_play = HOVER if mouse_sobre(mx, my, bx, by_play, bw, bh) else FUNDO_BTN
    desenhar_botao(superficie, bx, by_play, bw, bh, BORDA, cor_play)

    # QUIT
    cor_quit = HOVER if mouse_sobre(mx, my, bx, by_quit, bw, bh) else FUNDO_BTN
    desenhar_botao(superficie, bx, by_quit, bw, bh, BORDA, cor_quit)

    # --- TEXTO (SAME WAY AS GAME TITLE) ---
    fonte = pygame.font.Font(None, 36)

    texto_play = fonte.render("PLAY", True, TEXTO)
    texto_quit = fonte.render("QUIT", True, TEXTO)

    rect_play = texto_play.get_rect(center=(bx + bw // 2, by_play + bh // 2))
    rect_quit = texto_quit.get_rect(center=(bx + bw // 2, by_quit + bh // 2))

    superficie.blit(texto_play, rect_play)
    superficie.blit(texto_quit, rect_quit)

    pygame.display.flip()