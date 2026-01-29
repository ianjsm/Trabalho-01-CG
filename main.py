import pygame
import sys
from menu import desenhar_abertura, desenhar_botao, desenhar_menu, mouse_sobre
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
        self.estado = "ABERTURA"
        self.menu_renderizado = False
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        
        # Sistema de Fases
        self.fase_atual = 0
        self.definir_fases()
        
        # Estado do Jogador
        self.pos_x, self.pos_y = LARGURA // 2, ALTURA // 2
        self.mana = 100.0
        self.ondas = []
        
        # Inicializa a primeira fase
        self.carregar_fase(0)

        self.camera = Camera.Camera(LARGURA, ALTURA, LARGURA, ALTURA)

        self.sprite_vampiro = self.carregar_assets()
    
    def definir_fases(self):
        # Cada fase tem seu mapa, spawn de inimigos e o índice do objetivo (último polígono)
        self.dados_fases = [
            { # FASE 1
                "mapa": [
                    [(350, 250), (450, 250), (450, 260), (350, 260)], # Bloco Central
                    [(350, 340), (450, 340), (450, 350), (350, 350)],
                    [(350, 250), (360, 250), (360, 350), (350, 350)],
                    [(440, 250), (450, 250), (450, 350), (440, 350)],
                    [(250, 150), (550, 150), (550, 170), (250, 170)], # Anel
                    [(250, 170), (270, 170), (270, 430), (250, 430)],
                    [(530, 170), (550, 170), (550, 430), (530, 430)],
                    [(250, 430), (400, 430), (400, 450), (250, 450)],
                    [(450, 430), (550, 430), (550, 450), (450, 450)],
                    [(150, 50), (170, 50), (170, 300), (150, 300)],   # Zigue-zague
                    [(630, 300), (650, 300), (650, 550), (630, 550)],
                    [(100, 100), (300, 100), (300, 120), (100, 120)],
                    [(500, 480), (700, 480), (700, 500), (500, 500)],
                    [(40, 40), (760, 40), (760, 50), (40, 50)],       # Bordas
                    [(40, 550), (760, 550), (760, 560), (40, 560)],
                    [(40, 40), (50, 40), (50, 560), (40, 560)],
                    [(750, 40), (760, 40), (760, 560), (750, 560)],
                    [(700, 80), (720, 100), (700, 120), (680, 100)]   # OBJETIVO (Porta)
                ],
                "inimigos": [
                    {"x": 60, "y": 200, "vel": 0.3},
                    {"x": 400, "y": 60, "vel": 2}
                ]
            },
            { # FASE 2
                "mapa": [
                    # Obstáculos Internos
                    [(100, 100), (150, 100), (150, 500), (100, 500)], # Pilar Lateral L
                    [(650, 100), (700, 100), (700, 500), (650, 500)], # Pilar Lateral R
                    [(300, 50), (500, 50), (500, 100), (300, 100)],   # Bloqueio Top
                    [(300, 500), (500, 500), (500, 550), (300, 550)], # Bloqueio Bot
                    
                    # Bordas Externas (Separadas para não preencher o centro)
                    [(30, 30), (770, 30), (770, 40), (30, 40)],    # Parede Norte
                    [(30, 560), (770, 560), (770, 570), (30, 570)], # Parede Sul
                    [(30, 30), (40, 30), (40, 570), (30, 570)],    # Parede Oeste
                    [(760, 30), (770, 30), (770, 570), (760, 570)], # Parede Leste
                    
                    # OBJETIVO (Último da lista)
                    [(700, 80), (740, 80), (740, 120), (700, 120)]  
                ],
                "inimigos": [
                    {"x": 60, "y": 60, "vel": 1.5},   # Canto superior esquerdo
                    {"x": 740, "y": 540, "vel": 2.0}, # Canto inferior direito
                    {"x": 60, "y": 540, "vel": 1.2},  # Canto inferior esquerdo 
                    {"x": 400, "y": 40, "vel": 1.8},
                    {"x": 240, "y": 340, "vel": 2.0},   
                ]
            }
        ]

    def rodar(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()

            # ---------------- EVENTS ----------------
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # -------- ABERTURA --------
                if self.estado == "ABERTURA":
                    if evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        self.estado = "MENU"

                # -------- MENU --------
                elif self.estado == "MENU":
                    if evento.type == pygame.MOUSEBUTTONDOWN:
                        bx, bw, bh = 300, 200, 60

                        if mouse_sobre(*mouse_pos, bx, 250, bw, bh):
                            self.estado = "JOGANDO"

                        if mouse_sobre(*mouse_pos, bx, 340, bw, bh):
                            pygame.quit()
                            sys.exit()

                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

                # -------- JOGANDO --------
                elif self.estado == "JOGANDO":
                    if evento.type == pygame.KEYDOWN:
                        if evento.key == pygame.K_ESCAPE:
                            self.estado = "MENU"

                        if evento.key == pygame.K_SPACE and self.mana >= 20:
                            self.ondas.append(0)
                            self.mana -= 20

            # ---------------- STATES ----------------
            if self.estado == "ABERTURA":
                desenhar_abertura(self.tela, LARGURA, ALTURA)

            elif self.estado == "MENU":
                desenhar_menu(self.tela, mouse_pos)

            elif self.estado == "JOGANDO":
                self.processar_input()
                self.atualizar()
                self.desenhar()

            elif self.estado == "MORTE":
                self.exibir_tela_morte() 

            pygame.display.flip()
            self.clock.tick(60)

    def carregar_fase(self, n):
        fase = self.dados_fases[n]
        self.mapa = fase["mapa"]
        self.inimigos = [dict(i) for i in fase["inimigos"]] # Copia os dados
        self.pos_x, self.pos_y = LARGURA // 2, ALTURA // 2
        self.ondas = []
        self.mana = 100

    def carregar_assets(self):
        try:
            sprite = pygame.image.load("Imagens/vampiro.png").convert_alpha()
            return pygame.transform.scale(sprite, (40, 40))
        except:
            s = pygame.Surface((32, 32)); s.fill((255, 0, 0))
            return s

    def processar_input(self):
        teclas = pygame.key.get_pressed()
        velocidade = 3

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

    def atualizar(self):
        # 1. Movimentação de TODOS os inimigos da fase
        for inimigo in self.inimigos:
            dx = self.pos_x - inimigo["x"]
            dy = self.pos_y - inimigo["y"]
            dist = (dx**2 + dy**2)**0.5
            
            if dist > 0:
                vx = (dx / dist) * inimigo["vel"]
                vy = (dy / dist) * inimigo["vel"]
                
                # Tenta mover no eixo X
                pode_x = True
                for poli in self.mapa:
                    if Colisao.ponto_em_poligono(inimigo["x"] + vx, inimigo["y"], poli):
                        pode_x = False; break
                if pode_x: inimigo["x"] += vx

                # Tenta mover no eixo Y
                pode_y = True
                for poli in self.mapa:
                    if Colisao.ponto_em_poligono(inimigo["x"], inimigo["y"] + vy, poli):
                        pode_y = False; break
                if pode_y: inimigo["y"] += vy

            # 2. Condição de Derrota
            if dist < 25:
                self.estado = "MORTE"
                return 

        # 3. Transição de Fase
        objetivo = self.mapa[-1]

        # Calcula o centro do polígono objetivo dinamicamente
        centro_obj_x = sum(p[0] for p in objetivo) / len(objetivo)
        centro_obj_y = sum(p[1] for p in objetivo) / len(objetivo)

        # Calcula a distância real do jogador até o centro do objetivo
        dist_objetivo = ((self.pos_x - centro_obj_x)**2 + (self.pos_y - centro_obj_y)**2)**0.5

        # Se estiver a menos de 25 pixels do centro OU o ponto central colidir
        if dist_objetivo < 25 or Colisao.ponto_em_poligono(self.pos_x, self.pos_y, objetivo):
            if self.fase_atual < len(self.dados_fases) - 1:
                self.fase_atual += 1 
                print(f"Mudando para a fase {self.fase_atual + 1}")
                self.carregar_fase(self.fase_atual)
                return 
            else:
                print("VITÓRIA FINAL!")
                self.estado = "MENU"
                self.fase_atual = 0
                self.carregar_fase(0)
                return

        # 4. Animação das ondas e Mana
        self.ondas = [r + 5 for r in self.ondas if r < 250]
        if self.mana < 100: 
            self.mana += 0.2

        # 5. Transformações Geométricas
        if len(self.mapa) > 0:
            pivô = self.mapa[0][0]
            self.mapa[0] = Transform.Transformador.rotacionar(self.mapa[0], 1, pivô)

        # Zoom
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_KP_PLUS]:
            for i in range(len(self.mapa)):
                self.mapa[i] = Transform.Transformador.escalar(self.mapa[i], 1.01, 1.01, (self.pos_x, self.pos_y))
        if teclas[pygame.K_KP_MINUS]:
            for i in range(len(self.mapa)):
                self.mapa[i] = Transform.Transformador.escalar(self.mapa[i], 0.99, 0.99, (self.pos_x, self.pos_y))

    def exibir_tela_morte(self):
        self.tela.fill((30, 0, 0)) # Fundo vinho escuro
        BRANCO = (255, 255, 255)
        VERMELHO_VIVO = (255, 0, 0)
        
        mouse_pos = pygame.mouse.get_pos()
        clique = pygame.mouse.get_pressed()

        # --- FUNÇÃO AUXILIAR PARA LETRAS RÚSTICAS ---
        def desenhar_letra(char, x, y, cor):
            # Letras baseadas em uma grade de 10x15
            if char == 'V':
                BresenhamReta.bresenham(self.tela, x, y, x+5, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+5, y+15, x+10, y, cor)
            elif char == 'O' or char == '0':
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y+15, x+10, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+10, y, x+10, y+15, cor)
            elif char == 'C':
                BresenhamReta.bresenham(self.tela, x+10, y, x, y, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y+15, x+10, y+15, cor)
            elif char == 'E' or char == 'Ê':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y+7, x+8, y+7, cor)
                BresenhamReta.bresenham(self.tela, x, y+15, x+10, y+15, cor)
                if char == 'Ê': # Acento circunflexo rústico
                    BresenhamReta.bresenham(self.tela, x+2, y-5, x+5, y-8, cor)
                    BresenhamReta.bresenham(self.tela, x+5, y-8, x+8, y-5, cor)
            elif char == 'F':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y+7, x+8, y+7, cor)
            elif char == 'I':
                BresenhamReta.bresenham(self.tela, x+5, y, x+5, y+15, cor)
            elif char == 'P':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x+10, y, x+10, y+7, cor)
                BresenhamReta.bresenham(self.tela, x, y+7, x+10, y+7, cor)
            elif char == 'A':
                BresenhamReta.bresenham(self.tela, x, y+15, x+5, y, cor)
                BresenhamReta.bresenham(self.tela, x+5, y, x+10, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+2, y+10, x+8, y+10, cor)
            elif char == 'T':
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x+5, y, x+5, y+15, cor)
            elif char == 'U':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+10, y, x+10, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y+15, x+10, y+15, cor)
            elif char == 'R':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x+10, y, cor)
                BresenhamReta.bresenham(self.tela, x+10, y, x+10, y+7, cor)
                BresenhamReta.bresenham(self.tela, x, y+7, x+10, y+7, cor)
                BresenhamReta.bresenham(self.tela, x+5, y+7, x+10, y+15, cor)
            elif char == 'D':
                BresenhamReta.bresenham(self.tela, x, y, x, y+15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x+7, y, cor)
                BresenhamReta.bresenham(self.tela, x+7, y, x+10, y+7, cor)
                BresenhamReta.bresenham(self.tela, x+10, y+7, x+7, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+7, y+15, x, y+15, cor)
            elif char == 'S':
                BresenhamReta.bresenham(self.tela, x+10, y, x, y, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y+7, cor)
                BresenhamReta.bresenham(self.tela, x, y+7, x+10, y+7, cor)
                BresenhamReta.bresenham(self.tela, x+10, y+7, x+10, y+15, cor)
                BresenhamReta.bresenham(self.tela, x+10, y+15, x, y+15, cor)
            elif char == '!':
                BresenhamReta.bresenham(self.tela, x+5, y, x+5, y+10, cor)
                SetPixel.setPixel(self.tela, x+5, y+14, cor)

        # --- TÍTULO PRINCIPAL ---
        titulo = "VOCÊ FOI CAPTURADO!"
        # Centralizando o título (Aprox. x=230 para ficar no meio)
        for i, l in enumerate(titulo):
            if l != ' ':
                desenhar_letra(l, 210 + (i * 18), 200, VERMELHO_VIVO)

        # --- BOTÃO RESTART ---
        cor_btn1 = VERMELHO_VIVO if (300 < mouse_pos[0] < 500 and 300 < mouse_pos[1] < 350) else BRANCO
        BresenhamReta.bresenham(self.tela, 300, 300, 500, 300, cor_btn1)
        BresenhamReta.bresenham(self.tela, 300, 350, 500, 350, cor_btn1)
        BresenhamReta.bresenham(self.tela, 300, 300, 300, 350, cor_btn1)
        BresenhamReta.bresenham(self.tela, 500, 300, 500, 350, cor_btn1)
        
        letras_restart = "RESTART"
        for i, l in enumerate(letras_restart):
            desenhar_letra(l, 335 + (i * 18), 318, cor_btn1)

        if cor_btn1 == VERMELHO_VIVO and clique[0]:
            # 1. Volta para a primeira fase (índice 0)
            self.fase_atual = 0 
            
            # 2. Usa a função que já tem para resetar mapa, inimigos e posição
            self.carregar_fase(0) 
            
            # 3. Muda o estado para voltar ao jogo
            self.estado = "JOGANDO"
            
            # Pequeno delay ou reset de eventos para não disparar cliques acidentais
            pygame.event.clear()

        # --- BOTÃO SAIR ---
        cor_btn2 = VERMELHO_VIVO if (300 < mouse_pos[0] < 500 and 400 < mouse_pos[1] < 450) else BRANCO
        BresenhamReta.bresenham(self.tela, 300, 400, 500, 400, cor_btn2)
        BresenhamReta.bresenham(self.tela, 300, 450, 500, 450, cor_btn2)
        BresenhamReta.bresenham(self.tela, 300, 400, 300, 450, cor_btn2)
        BresenhamReta.bresenham(self.tela, 500, 400, 500, 450, cor_btn2)

        letras_sair = "SAIR"
        for i, l in enumerate(letras_sair):
            desenhar_letra(l, 365 + (i * 20), 418, cor_btn2)

        if cor_btn2 == VERMELHO_VIVO and clique[0]:
            pygame.quit()
            sys.exit()

        pygame.display.flip()

    def desenhar(self):
        self.tela.fill((0, 0, 0)) 
        # Mana
        pygame.draw.rect(self.tela, (50, 50, 50), (10, 10, 200, 20))
        pygame.draw.rect(self.tela, (0, 0, 255), (10, 10, int(self.mana * 2), 20))
        # Vampiro
        rect = self.sprite_vampiro.get_rect(center=(self.pos_x, self.pos_y))
        self.tela.blit(self.sprite_vampiro, rect)

        for raio in self.ondas:
            Circulo.Circulo(self.tela, self.pos_x, self.pos_y, raio, COR_ONDA)
            
            for i, poligono in enumerate(self.mapa):
                # Se for o último polígono da lista, mandamos a cor AZUL
                if i == len(self.mapa) - 1:
                    self.revelar_obstaculo(poligono, raio, (0, 150, 255))
                else:
                    self.revelar_obstaculo(poligono, raio, (0, 100, 0))
            
            for inimigo in self.inimigos:
                dist_i = ((inimigo["x"] - self.pos_x)**2 + (inimigo["y"] - self.pos_y)**2)**0.5
                if abs(dist_i - raio) < 30:
                    Circulo.Circulo(self.tela, int(inimigo["x"]), int(inimigo["y"]), 12, (255, 0, 0))
                    
        # SÓ PARA TESTE: Desenha a porta de saída em azul o tempo todo
        #saida = self.mapa[-1]
        #pts_saida = [self.camera.mundo_para_tela(p[0], p[1]) for p in saida]
        #pygame.draw.polygon(self.tela, (0, 0, 255), pts_saida)

        pygame.display.flip()

    def revelar_obstaculo(self, pontos, raio_onda, cor): 
            centro_x = sum(p[0] for p in pontos) / len(pontos)
            centro_y = sum(p[1] for p in pontos) / len(pontos)
            p_centro = (centro_x, centro_y)
            p_vampiro = (self.pos_x, self.pos_y)
            
            dist_centro = ((centro_x - self.pos_x)**2 + (centro_y - self.pos_y)**2)**0.5

            if abs(dist_centro - raio_onda) < 30:
                oculto = False
                for p_bloqueio in self.mapa:
                    if p_bloqueio == pontos: continue
                    for j in range(len(p_bloqueio)):
                        b1 = p_bloqueio[j]
                        b2 = p_bloqueio[(j + 1) % len(p_bloqueio)]
                        if Colisao.interseccionam(p_vampiro, p_centro, b1, b2):
                            oculto = True
                            break
                    if oculto: break
                
                if not oculto:
                    pontos_tela = [self.camera.mundo_para_tela(p[0], p[1]) for p in pontos]
                    # USANDO A COR PASSADA POR ARGUMENTO
                    ScanlineFill.scanline_fill(self.tela, pontos_tela, cor, (0, 20, 0))

            # 2. Bordas
            for i in range(len(pontos)):
                p1 = pontos[i]
                p2 = pontos[(i + 1) % len(pontos)]
                p_meio_aresta = ((p1[0] + p2[0])/2, (p1[1] + p2[1])/2)
                dist_aresta = ((p_meio_aresta[0] - self.pos_x)**2 + (p_meio_aresta[1] - self.pos_y)**2)**0.5
                
                if abs(dist_aresta - raio_onda) < 15:
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
                        # USANDO A COR PARA A BORDA TAMBÉM (ou uma variação mais clara dela)
                        if acc: BresenhamReta.bresenham(self.tela, int(x1), int(y1), int(x2), int(y2), cor)

if __name__ == "__main__":
    jogo = JogoVampiro()
    jogo.rodar()