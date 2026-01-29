import pygame
import sys
from menu import desenhar_abertura
from Primitivas import SetPixel, Elipse, Circulo, ScanlineFill, BresenhamReta
from Primitivas import Transform, Camera, Clipping, Texturizador, FloodFill
from Funcao import Colisao

# Configurações
LARGURA, ALTURA = 800, 600
COR_ONDA = (0, 255, 255)  # Ciano para o som
COR_VAMPIRO = (200, 0, 0) # Vermelho escuro

class JogoVampiro:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        
        # Estado do Jogador
        self.pos_x, self.pos_y = LARGURA // 2, ALTURA // 2
        self.mana = 100.0
        
        # Estado da Onda (Ecolocalização)
        self.ondas = [] # Lista de raios das ondas ativas
        
        # Labirinto simples com corredores estreitos
        self.mapa = [
            # 1. BLOCO CENTRAL (Onde o vampiro nasce - paredes ao redor)
            [(350, 250), (450, 250), (450, 260), (350, 260)], # Norte
            [(350, 340), (450, 340), (450, 350), (350, 350)], # Sul
            [(350, 250), (360, 250), (360, 350), (350, 350)], # Oeste
            [(440, 250), (450, 250), (450, 350), (440, 350)], # Leste (Deixe uma abertura se preferir)

            # 2. ANEL INTERMEDIÁRIO (Com abertura no sul para passagem)
            [(250, 150), (550, 150), (550, 170), (250, 170)], # Superior (Fechado)
            [(250, 170), (270, 170), (270, 430), (250, 430)], # Esquerda (Fechada)
            [(530, 170), (550, 170), (550, 430), (530, 430)], # Direita (Fechada)
            
            # Parede Inferior QUEBRADA (Cria o corredor de saída)
            [(250, 430), (400, 430), (400, 450), (250, 450)], # Parte 1
            [(450, 430), (550, 430), (550, 450), (450, 450)], # Parte 2

            # 3. PAREDES DE DESVIO (Zigue-zague)
            [(150, 50), (170, 50), (170, 300), (150, 300)],   # Divisória Vertical NW
            [(630, 300), (650, 300), (650, 550), (630, 550)], # Divisória Vertical SE
            [(100, 100), (300, 100), (300, 120), (100, 120)], # Divisória Horizontal N
            [(500, 480), (700, 480), (700, 500), (500, 500)], # Divisória Horizontal S

            # 4. BORDAS EXTERNAS (Limites do mapa)
            [(40, 40), (760, 40), (760, 50), (40, 50)],       # Teto
            [(40, 550), (760, 550), (760, 560), (40, 560)],   # Chão
            [(40, 40), (50, 40), (50, 560), (40, 560)],       # Parede Esq
            [(750, 40), (760, 40), (760, 560), (750, 560)],   # Parede Dir
            
            # --- O "ALGO" PARA ENCONTRAR (OBJETIVO) ---
            # Um pequeno losango escondido no canto superior direito
            [(700, 80), (720, 100), (700, 120), (680, 100)]
        ]

        self.camera = Camera.Camera(LARGURA, ALTURA, LARGURA, ALTURA)

        self.textura_pedra = None

        try:
            self.sprite_vampiro = pygame.image.load("Imagens/vampiro.png").convert_alpha()
            # Se a imagem for muito grande, redimensione via código:
            self.sprite_vampiro = pygame.transform.scale(self.sprite_vampiro, (40, 40))
        except:
            print("Erro: Não achei o arquivo vampiro.png!")
            # Cria uma superfície vermelha de fallback caso a imagem falte
            self.sprite_vampiro = pygame.Surface((32, 32))
            self.sprite_vampiro.fill((255, 0, 0))

        self.estado = "MENU"
        self.menu_renderizado = False

    def rodar(self):
        while True:
            if self.estado == "MENU":
                if not self.menu_renderizado:
                    desenhar_abertura(self.tela, LARGURA, ALTURA)
                    self.menu_renderizado = True
                    pygame.display.flip()
                        
                # Tratamento de eventos no Menu
                for evento in pygame.event.get():
                    if evento.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if evento.type == pygame.KEYDOWN:
                        self.estado = "JOGANDO"
            
            elif self.estado == "JOGANDO":
                self.processar_input()
                self.atualizar()
                self.desenhar()
                self.clock.tick(60)

    def processar_input(self):
        teclas = pygame.key.get_pressed()
        velocidade = 4

        proximo_x = self.pos_x
        proximo_y = self.pos_y
        
        if teclas[pygame.K_LEFT]:  proximo_x -= velocidade
        if teclas[pygame.K_RIGHT]: proximo_x += velocidade
        if teclas[pygame.K_UP]:    proximo_y -= velocidade
        if teclas[pygame.K_DOWN]:  proximo_y += velocidade

        # 1. TRAVA DE BORDA DA TELA (Limite do Monitor)
        # Considera que o boneco tem 40x40 (raio 20)
        if proximo_x < 20: proximo_x = 20
        if proximo_x > LARGURA - 20: proximo_x = LARGURA - 20
        if proximo_y < 20: proximo_y = 20
        if proximo_y > ALTURA - 20: proximo_y = ALTURA - 20

        # 2. CHECAGEM DE IMPACTO NOS OBJETOS
        pode_mover = True
        for poligono in self.mapa:
            if Colisao.ponto_em_poligono(proximo_x, proximo_y, poligono):
                pode_mover = False
                break
        
        if pode_mover:
            self.pos_x = proximo_x
            self.pos_y = proximo_y
        # ---------------------------

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and self.mana >= 20:
                    self.ondas.append(0)
                    self.mana -= 20

    def atualizar(self):
        # Animação das ondas (Requisito: Animação)
        novas_ondas = []
        for raio in self.ondas:
            if raio < 300: # Alcance máximo da onda
                novas_ondas.append(raio + 5) # Velocidade da onda
        self.ondas = novas_ondas
        
        # Recuperação passiva de mana
        if self.mana < 100:
            self.mana += 0.2

        # Vamos girar o primeiro obstáculo em seu próprio eixo
        pivô = self.mapa[0][0] # Usa o primeiro vértice como pivô
        self.mapa[0] = Transform.Transformador.rotacionar(self.mapa[0], 1, pivô)

        #(Zoom da Câmera com as teclas + e -)
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_KP_PLUS]:
            for i in range(len(self.mapa)):
                self.mapa[i] = Transform.Transformador.escalar(self.mapa[i], 1.01, 1.01, (self.pos_x, self.pos_y))
        if teclas[pygame.K_KP_MINUS]:
            for i in range(len(self.mapa)):
                self.mapa[i] = Transform.Transformador.escalar(self.mapa[i], 0.99, 0.99, (self.pos_x, self.pos_y))


    def desenhar(self):
        self.tela.fill((0, 0, 0)) 

        # 1. BARRA DE MANA
        pygame.draw.rect(self.tela, (50, 50, 50), (10, 10, 200, 20))
        pygame.draw.rect(self.tela, (0, 0, 255), (10, 10, int(self.mana * 2), 20))

        # 2. DESENHAR O JOGADOR (Coordenadas diretas = Tela Fixa)
        rect = self.sprite_vampiro.get_rect(center=(self.pos_x, self.pos_y))
        self.tela.blit(self.sprite_vampiro, rect)

        # 3. ONDAS E MAPA
        for raio in self.ondas:
            # Desenha a onda na posição real do boneco na tela
            Circulo.Circulo(self.tela, self.pos_x, self.pos_y, raio, COR_ONDA)
            
            for poligono in self.mapa:
                # O mapa ainda usa revelar_obstaculo para o efeito de visão noturna
                self.revelar_obstaculo(poligono, raio)

        pygame.display.flip()

    def revelar_obstaculo(self, pontos, raio_onda):
        centro_x = sum(p[0] for p in pontos) / len(pontos)
        centro_y = sum(p[1] for p in pontos) / len(pontos)
        p_centro = (centro_x, centro_y)
        p_vampiro = (self.pos_x, self.pos_y)
        
        dist_centro = ((centro_x - self.pos_x)**2 + (centro_y - self.pos_y)**2)**0.5

        if abs(dist_centro - raio_onda) < 30:
            oculto = False
            # Verifica se algum polígono bloqueia a visão do centro deste objeto
            for p_bloqueio in self.mapa:
                if p_bloqueio == pontos: continue
                
                # Checa cada aresta do polígono bloqueador
                for j in range(len(p_bloqueio)):
                    b1 = p_bloqueio[j]
                    b2 = p_bloqueio[(j + 1) % len(p_bloqueio)]
                    
                    if Colisao.interseccionam(p_vampiro, p_centro, b1, b2):
                        oculto = True
                        break
                if oculto: break
            
            if not oculto:
                pontos_tela = [self.camera.mundo_para_tela(p[0], p[1]) for p in pontos]
                ScanlineFill.scanline_fill(self.tela, pontos_tela, (0, 100, 0), (0, 20, 0))

        # 2. Bordas (Desenha apenas se a aresta estiver visível)
        for i in range(len(pontos)):
            p1 = pontos[i]
            p2 = pontos[(i + 1) % len(pontos)]
            p_meio_aresta = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
            dist_aresta = ((p_meio_aresta[0] - self.pos_x)**2 + (p_meio_aresta[1] - self.pos_y)**2)**0.5
            
            if abs(dist_aresta - raio_onda) < 15:
                # Mesmo teste de oclusão para a aresta
                aresta_oculta = False
                for p_bloqueio in self.mapa:
                    if p_bloqueio == pontos: continue
                    for j in range(len(p_bloqueio)):
                        if Colisao.interseccionam(p_vampiro, p_meio_aresta, p_bloqueio[j], p_bloqueio[(j+1)%len(p_bloqueio)]):
                            aresta_oculta = True; break
                    if aresta_oculta: break
                
                if not aresta_oculta:
                    p1_t = self.camera.mundo_para_tela(p1[0], p1[1])
                    p2_t = self.camera.mundo_para_tela(p2[0], p2[1])
                    acc, x1, y1, x2, y2 = Clipping.cohen_sutherland_clip(p1_t[0], p1_t[1], p2_t[0], p2_t[1], 0, 0, LARGURA, ALTURA)
                    if acc: BresenhamReta.bresenham(self.tela, int(x1), int(y1), int(x2), int(y2), (0, 255, 100))

if __name__ == "__main__":
    jogo = JogoVampiro()
    jogo.rodar()