import pygame
import sys
from menu import desenhar_abertura
from Primitivas import SetPixel, Elipse, Circulo, ScanlineFill, BresenhamReta
from Primitivas import Transform, Camera, Clipping, Texturizador, FloodFill

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
        
        # O Mapa (Polígonos que o vampiro precisa descobrir)
        # Exemplo: um triângulo e um quadrado (Requisito: Polígonos/Scanline)
        self.mapa = [
            [(100, 100), (200, 100), (150, 200)], # Obstáculo 1
            [(500, 400), (600, 400), (600, 500), (500, 500)] # Obstáculo 2
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
        
        if teclas[pygame.K_LEFT]:  self.pos_x -= velocidade
        if teclas[pygame.K_RIGHT]: self.pos_x += velocidade
        if teclas[pygame.K_UP]:    self.pos_y -= velocidade
        if teclas[pygame.K_DOWN]:  self.pos_y += velocidade
        
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE and self.mana >= 20:
                    self.ondas.append(0) # Inicia nova onda com raio 0
                    self.mana -= 20      # Custo de mana

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

        self.camera.focar(self.pos_x, self.pos_y)

    def desenhar(self):
        self.tela.fill((0, 0, 0)) 

        # 1. Barra de Mana (Lembre-se: use seu Scanline para o 10!)
        pygame.draw.rect(self.tela, (50, 50, 50), (10, 10, 200, 20))
        pygame.draw.rect(self.tela, (0, 0, 255), (10, 10, int(self.mana * 2), 20))

        # 2. Desenhar o Jogador (Sprite centralizada)
        rect = self.sprite_vampiro.get_rect(center=(self.pos_x, self.pos_y))
        self.tela.blit(self.sprite_vampiro, rect)

        # 3. Ondas e Mapa
        for raio in self.ondas:
            Circulo.Circulo(self.tela, self.pos_x, self.pos_y, raio, COR_ONDA)
            for poligono in self.mapa:
                self.revelar_obstaculo(poligono, raio)

        pygame.display.flip()

    def revelar_obstaculo(self, pontos, raio_onda):
        pontos_tela = [self.camera.mundo_para_tela(p[0], p[1]) for p in pontos]
        
        centro_x = sum(p[0] for p in pontos) / len(pontos)
        centro_y = sum(p[1] for p in pontos) / len(pontos)
        dist_centro = ((centro_x - self.pos_x)**2 + (centro_y - self.pos_y)**2)**0.5
            
        # 1. Preenchimento (Efeito Visão Noturna)
        if abs(dist_centro - raio_onda) < 30:
            # Gradiente Verde: (0, 100, 0) topo -> (0, 20, 0) baixo
            # Isso dá o aspecto de fósforo verde dos radares antigos
            ScanlineFill.scanline_fill(self.tela, pontos_tela, (0, 100, 0), (0, 20, 0))

        # 2. Bordas (Contorno brilhante)
        for i in range(len(pontos)):
            p1_mundo = pontos[i]
            dist_p1 = ((p1_mundo[0] - self.pos_x)**2 + (p1_mundo[1] - self.pos_y)**2)**0.5
            
            if abs(dist_p1 - raio_onda) < 15:
                p1_t = pontos_tela[i]
                p2_t = pontos_tela[(i + 1) % len(pontos)]
                
                aceito, x1, y1, x2, y2 = Clipping.cohen_sutherland_clip(
                    p1_t[0], p1_t[1], p2_t[0], p2_t[1], 0, 0, LARGURA, ALTURA
                )
                if aceito:
                    # Contorno em verde neon para destacar a borda que a onda está tocando
                    BresenhamReta.bresenham(self.tela, int(x1), int(y1), int(x2), int(y2), (0, 255, 100))

if __name__ == "__main__":
    jogo = JogoVampiro()
    jogo.rodar()