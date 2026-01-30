import pygame
import sys
import math
from config import LARGURA, ALTURA, COR_INTERFACE_BG, COR_INTERFACE_MANA, COR_ONDA
from texturas import gerar_textura_pedra, gerar_textura_objetivo, gerar_chao_procedural
from fases import get_fases

from menu import desenhar_abertura, desenhar_menu, mouse_sobre
from Funcao import Colisao
from Primitivas import (
    SetPixel,
    Elipse,
    Circulo,
    ScanlineFill,
    BresenhamReta,
    Transform,
    Camera,
    Clipping,
    Texturizador,
    FloodFill,
)


class JogoVampiro:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("ECHO - A Fuga do Vampiro")
        try:
            pygame.display.set_icon(pygame.image.load("Imagens/vampiro.png"))
        except:
            pass

        self.estado = "ABERTURA"
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        self.clock = pygame.time.Clock()
        self.fonte_ui = pygame.font.Font(None, 24)

        self.tex_parede = gerar_textura_pedra(64, 64)
        self.tex_objetivo = gerar_textura_objetivo(64, 64)

        self.sprite_vampiro = self.carregar_imagem("Imagens/vampiro.png", (255, 0, 0))
        self.sprite_morcego = self.carregar_imagem("Imagens/morcego.png", (0, 0, 0))
        self.sprite_atual = self.sprite_vampiro

        self.particulas_chao = gerar_chao_procedural(LARGURA, ALTURA, 5000)

        self.fases_dados = get_fases()
        self.fase_atual = 0
        self.fase_escura = True
        self.carregar_fase(0)

        self.camera = Camera.Camera(LARGURA, ALTURA, LARGURA, ALTURA)

        self.mana = 100.0
        self.ondas = []
        self.boost_timer = 0

        self.transicao_ativa = False
        self.alpha_fade = 0
        self.direcao_fade = 1
        self.overlay_fade = pygame.Surface((LARGURA, ALTURA))
        self.overlay_fade.fill((255, 255, 255))

    def rodar(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            eventos = pygame.event.get()
            self.tratar_eventos_globais(eventos)

            if self.estado == "ABERTURA":
                self.tratar_abertura(eventos)
                desenhar_abertura(self.tela, LARGURA, ALTURA)
            elif self.estado == "MENU":
                self.tratar_menu(eventos, mouse_pos)
                desenhar_menu(self.tela, mouse_pos)
            elif self.estado == "JOGANDO":
                self.tratar_jogo(eventos)
                self.atualizar_jogo()
                self.desenhar_jogo()

                if self.transicao_ativa or self.alpha_fade > 0:
                    self.processar_transicao()

            elif self.estado == "MORTE":
                self.exibir_tela_morte(mouse_pos)

            pygame.display.flip()
            self.clock.tick(60)

    def iniciar_transicao_fase(self):
        self.transicao_ativa = True
        self.direcao_fade = 1

    def processar_transicao(self):
        velocidade_fade = 5
        self.alpha_fade += velocidade_fade * self.direcao_fade

        if self.alpha_fade >= 255:
            self.alpha_fade = 255
            if self.transicao_ativa:
                self.avancar_fase()
                self.direcao_fade = -1
                self.transicao_ativa = False

        elif self.alpha_fade <= 0:
            self.alpha_fade = 0
            self.direcao_fade = 0

        self.overlay_fade.set_alpha(self.alpha_fade)
        self.tela.blit(self.overlay_fade, (0, 0))

    def avancar_fase(self):
        if self.fase_atual < len(self.fases_dados) - 1:
            self.fase_atual += 1
            self.carregar_fase(self.fase_atual)
        else:
            self.fase_atual = 0
            self.carregar_fase(0)
            self.estado = "MENU"

    def tratar_eventos_globais(self, eventos):
        for ev in eventos:
            if ev.type == pygame.QUIT:
                self.sair()

    def tratar_abertura(self, eventos):
        for ev in eventos:
            if ev.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.estado = "MENU"

    def tratar_menu(self, eventos, mouse_pos):
        for ev in eventos:
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if mouse_sobre(*mouse_pos, 300, 250, 200, 60):
                    self.estado = "JOGANDO"
                if mouse_sobre(*mouse_pos, 300, 340, 200, 60):
                    self.sair()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                self.sair()

    def tratar_jogo(self, eventos):
        if self.alpha_fade > 200:
            return

        for ev in eventos:
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    self.estado = "MENU"

                if ev.key == pygame.K_SPACE:
                    if self.fase_escura:

                        if self.mana >= 20:
                            self.ondas.append(0)
                            self.mana -= 20
                    else:

                        if self.mana > 10:
                            self.boost_timer = 25

        self.processar_movimento()
        self.processar_zoom()

    def processar_movimento(self):
        keys = pygame.key.get_pressed()

        if self.fase_escura:
            vel = 2.0
        else:

            if self.boost_timer > 0:
                vel = 10.0
            else:
                vel = 5.0

        px, py = self.pos_x, self.pos_y

        if keys[pygame.K_LEFT]:
            px -= vel
        if keys[pygame.K_RIGHT]:
            px += vel
        if keys[pygame.K_UP]:
            py -= vel
        if keys[pygame.K_DOWN]:
            py += vel

        px = max(20, min(LARGURA - 20, px))
        py = max(20, min(ALTURA - 20, py))

        if self.checar_colisao(px, py):
            self.pos_x, self.pos_y = px, py

    def processar_zoom(self):
        keys = pygame.key.get_pressed()
        fator = 1.0
        if keys[pygame.K_KP_PLUS]:
            fator = 1.01
        if keys[pygame.K_KP_MINUS]:
            fator = 0.99
        if fator != 1.0:
            self.mapa = [
                Transform.Transformador.escalar(
                    p, fator, fator, (self.pos_x, self.pos_y)
                )
                for p in self.mapa
            ]

    def checar_colisao(self, x, y):
        raio = 10
        pontos_teste = [
            (x, y),
            (x + raio, y),
            (x - raio, y),
            (x, y + raio),
            (x, y - raio),
        ]
        for poligono in self.mapa[:-1]:
            for pt in pontos_teste:
                if Colisao.ponto_em_poligono(pt[0], pt[1], poligono):
                    return False
        return True

    def atualizar_jogo(self):
        if self.transicao_ativa:
            return

        if self.boost_timer > 0:
            self.boost_timer -= 1

            self.mana -= 5.0
            if self.mana <= 0:
                self.mana = 0
                self.boost_timer = 0
        else:

            if self.mana < 100:
                self.mana += 0.7

        for ini in self.inimigos:
            dx, dy = self.pos_x - ini["x"], self.pos_y - ini["y"]
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 0:
                vx, vy = (dx / dist) * ini["vel"], (dy / dist) * ini["vel"]
                if not any(
                    Colisao.ponto_em_poligono(ini["x"] + vx, ini["y"], p)
                    for p in self.mapa[:-1]
                ):
                    ini["x"] += vx
                if not any(
                    Colisao.ponto_em_poligono(ini["x"], ini["y"] + vy, p)
                    for p in self.mapa[:-1]
                ):
                    ini["y"] += vy
            if dist < 25:
                self.estado = "MORTE"

        obj = self.mapa[-1]
        cx = sum(p[0] for p in obj) / len(obj)
        cy = sum(p[1] for p in obj) / len(obj)
        if (
            (self.pos_x - cx) ** 2 + (self.pos_y - cy) ** 2
        ) ** 0.5 < 25 or Colisao.ponto_em_poligono(self.pos_x, self.pos_y, obj):
            self.iniciar_transicao_fase()

        self.ondas = [r + 5 for r in self.ondas if r < 250]

        if self.fase_escura and len(self.mapa) > 1:
            self.mapa[0] = Transform.Transformador.rotacionar(
                self.mapa[0], 1, self.mapa[0][0]
            )

    def desenhar_jogo(self):
        if self.fase_escura:
            self.desenhar_modo_escuro()
        else:
            self.desenhar_modo_claro()

        pontos_bg = [(10, 10), (210, 10), (210, 30), (10, 30)]
        ScanlineFill.scanline_fill(self.tela, pontos_bg, COR_INTERFACE_BG)

        largura_mana = int(self.mana * 2)

        if largura_mana > 0:
            xf = 10 + largura_mana
            pontos_mana = [(10, 10), (xf, 10), (xf, 30), (10, 30)]
            ScanlineFill.scanline_fill(self.tela, pontos_mana, COR_INTERFACE_MANA)
        texto_msg = self.fonte_ui.render(
            "Aperte ESPAÇO para ECHO", True, (200, 200, 200)
        )
        self.tela.blit(texto_msg, (10, 35))

        rect = self.sprite_atual.get_rect(center=(self.pos_x, self.pos_y))
        self.tela.blit(self.sprite_atual, rect)

        if self.fase_escura:
            for raio in self.ondas:
                if raio < 250:
                    Circulo.Circulo(self.tela, self.pos_x, self.pos_y, raio, COR_ONDA)

                for i, poligono in enumerate(self.mapa):
                    eh_obj = i == len(self.mapa) - 1
                    cor = (0, 150, 255) if eh_obj else (0, 100, 0)
                    self.revelar_obstaculo(poligono, raio, cor, eh_obj)

                for ini in self.inimigos:
                    if (
                        abs(
                            (
                                (ini["x"] - self.pos_x) ** 2
                                + (ini["y"] - self.pos_y) ** 2
                            )
                            ** 0.5
                            - raio
                        )
                        < 30
                    ):
                        Circulo.Circulo(
                            self.tela, int(ini["x"]), int(ini["y"]), 12, (255, 0, 0)
                        )

    def desenhar_modo_escuro(self):
        self.tela.fill((0, 0, 0))

        if self.ondas:
            maior = max(self.ondas)
            for px, py, cor in self.particulas_chao:
                dist = ((px - self.pos_x) ** 2 + (py - self.pos_y) ** 2) ** 0.5
                if maior - 80 < dist < maior:
                    SetPixel.setPixel(self.tela, px, py, cor)

    def desenhar_modo_claro(self):
        self.tela.fill((200, 230, 255))

        for i, poligono in enumerate(self.mapa):
            pts_t = [self.camera.mundo_para_tela(p[0], p[1]) for p in poligono]
            eh_obj = i == len(self.mapa) - 1
            try:
                tex = self.tex_objetivo if eh_obj else self.tex_parede
                Texturizador.scanline_textura_tiled(self.tela, pts_t, tex, 1.0)
            except:
                cor = (0, 150, 255) if eh_obj else (100, 100, 100)
                ScanlineFill.scanline_fill(self.tela, pts_t, cor)
            if len(pts_t) > 1:
                pygame.draw.lines(self.tela, (0, 0, 0), True, pts_t, 2)

        for ini in self.inimigos:
            self.desenhar_sol(int(ini["x"]), int(ini["y"]), 15)

        if self.boost_timer > 0:
            for i in range(1, 4):
                offset = 5 * i
                Circulo.Circulo(
                    self.tela, self.pos_x, self.pos_y + offset, 5, (255, 255, 255)
                )

    def desenhar_sol(self, x, y, raio):
        Circulo.Circulo(self.tela, x, y, raio, (255, 200, 0))
        FloodFill.flood_fill_iterativo(self.tela, x, y, (255, 255, 0), (255, 200, 0))
        for angulo in range(0, 360, 45):
            rad = math.radians(angulo)
            x_fim = x + int(math.cos(rad) * (raio + 10))
            y_fim = y + int(math.sin(rad) * (raio + 10))
            BresenhamReta.bresenham(self.tela, x, y, x_fim, y_fim, (255, 100, 0))

    def revelar_obstaculo(self, pontos, raio_onda, cor_base, eh_objetivo):
        cx = sum(p[0] for p in pontos) / len(pontos)
        cy = sum(p[1] for p in pontos) / len(pontos)
        dist_c = ((cx - self.pos_x) ** 2 + (cy - self.pos_y) ** 2) ** 0.5
        diff = raio_onda - dist_c
        alcance_fade = 80
        if 0 < diff < alcance_fade:
            intensidade = 1.0 - (diff / alcance_fade)
            if not self.esta_oculto(pontos, (cx, cy)):
                pts_t = [self.camera.mundo_para_tela(p[0], p[1]) for p in pontos]
                try:
                    tex = self.tex_objetivo if eh_objetivo else self.tex_parede
                    Texturizador.scanline_textura_tiled(
                        self.tela, pts_t, tex, intensidade
                    )
                except:
                    c_fade = (
                        int(cor_base[0] * intensidade),
                        int(cor_base[1] * intensidade),
                        int(cor_base[2] * intensidade),
                    )
                    ScanlineFill.scanline_fill(self.tela, pts_t, c_fade)
        for i in range(len(pontos)):
            p1, p2 = pontos[i], pontos[(i + 1) % len(pontos)]
            d_a = (
                (((p1[0] + p2[0]) / 2) - self.pos_x) ** 2
                + (((p1[1] + p2[1]) / 2) - self.pos_y) ** 2
            ) ** 0.5
            diff_a = raio_onda - d_a
            if 0 < diff_a < alcance_fade:
                inten_a = 1.0 - (diff_a / alcance_fade)
                c_fade_a = (
                    int(cor_base[0] * inten_a),
                    int(cor_base[1] * inten_a),
                    int(cor_base[2] * inten_a),
                )
                p1t = self.camera.mundo_para_tela(*p1)
                p2t = self.camera.mundo_para_tela(*p2)
                acc, x1, y1, x2, y2 = Clipping.cohen_sutherland_clip(
                    p1t[0], p1t[1], p2t[0], p2t[1], 0, 0, LARGURA, ALTURA
                )
                if acc:
                    BresenhamReta.bresenham(
                        self.tela, int(x1), int(y1), int(x2), int(y2), c_fade_a
                    )

    def esta_oculto(self, alvo, centro):
        for obst in self.mapa[:-1]:
            if obst == alvo:
                continue
            for j in range(len(obst)):
                if Colisao.interseccionam(
                    (self.pos_x, self.pos_y), centro, obst[j], obst[(j + 1) % len(obst)]
                ):
                    return True
        return False

    def carregar_fase(self, n):
        fase = self.fases_dados[n]
        self.mapa = [list(p) for p in fase["mapa"]]
        self.inimigos = [dict(i) for i in fase["inimigos"]]
        self.ondas = []
        self.mana = 100

        if n == 0:
            self.fase_escura = True
            self.sprite_atual = self.sprite_vampiro
            self.pos_x, self.pos_y = LARGURA // 2, ALTURA // 2
        else:
            self.fase_escura = False
            self.sprite_atual = self.sprite_morcego

            self.pos_x, self.pos_y = 80, 80

    def carregar_imagem(self, caminho, cor_fallback):
        try:
            return pygame.transform.scale(
                pygame.image.load(caminho).convert_alpha(), (40, 40)
            )
        except:
            s = pygame.Surface((32, 32))
            s.fill(cor_fallback)
            return s

    def exibir_tela_morte(self, mouse_pos):
        self.tela.fill((30, 0, 0))
        BRANCO = (255, 255, 255)
        VERMELHO_VIVO = (255, 0, 0)

        clique = pygame.mouse.get_pressed()

        def desenhar_letra(char, x, y, cor):

            if char == "V":
                BresenhamReta.bresenham(self.tela, x, y, x + 5, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 5, y + 15, x + 10, y, cor)
            elif char == "O" or char == "0":
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y + 15, x + 10, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y, x + 10, y + 15, cor)
            elif char == "C":
                BresenhamReta.bresenham(self.tela, x + 10, y, x, y, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y + 15, x + 10, y + 15, cor)
            elif char == "E" or char == "Ê":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y + 7, x + 8, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x, y + 15, x + 10, y + 15, cor)
                if char == "Ê":
                    BresenhamReta.bresenham(self.tela, x + 2, y - 5, x + 5, y - 8, cor)
                    BresenhamReta.bresenham(self.tela, x + 5, y - 8, x + 8, y - 5, cor)
            elif char == "F":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x, y + 7, x + 8, y + 7, cor)
            elif char == "I":
                BresenhamReta.bresenham(self.tela, x + 5, y, x + 5, y + 15, cor)
            elif char == "P":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y, x + 10, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x, y + 7, x + 10, y + 7, cor)
            elif char == "A":
                BresenhamReta.bresenham(self.tela, x, y + 15, x + 5, y, cor)
                BresenhamReta.bresenham(self.tela, x + 5, y, x + 10, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 2, y + 10, x + 8, y + 10, cor)
            elif char == "T":
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x + 5, y, x + 5, y + 15, cor)
            elif char == "U":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y, x + 10, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y + 15, x + 10, y + 15, cor)
            elif char == "R":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x + 10, y, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y, x + 10, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x, y + 7, x + 10, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x + 5, y + 7, x + 10, y + 15, cor)
            elif char == "D":
                BresenhamReta.bresenham(self.tela, x, y, x, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x, y, x + 7, y, cor)
                BresenhamReta.bresenham(self.tela, x + 7, y, x + 10, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y + 7, x + 7, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 7, y + 15, x, y + 15, cor)
            elif char == "S":
                BresenhamReta.bresenham(self.tela, x + 10, y, x, y, cor)
                BresenhamReta.bresenham(self.tela, x, y, x, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x, y + 7, x + 10, y + 7, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y + 7, x + 10, y + 15, cor)
                BresenhamReta.bresenham(self.tela, x + 10, y + 15, x, y + 15, cor)
            elif char == "!":
                BresenhamReta.bresenham(self.tela, x + 5, y, x + 5, y + 10, cor)
                SetPixel.setPixel(self.tela, x + 5, y + 14, cor)

        titulo = "VOCÊ FOI CAPTURADO!"

        for i, l in enumerate(titulo):
            if l != " ":
                desenhar_letra(l, 210 + (i * 18), 200, VERMELHO_VIVO)

        mouse_over_restart = 300 < mouse_pos[0] < 500 and 300 < mouse_pos[1] < 350
        cor_btn1 = VERMELHO_VIVO if mouse_over_restart else BRANCO

        BresenhamReta.bresenham(self.tela, 300, 300, 500, 300, cor_btn1)
        BresenhamReta.bresenham(self.tela, 300, 350, 500, 350, cor_btn1)
        BresenhamReta.bresenham(self.tela, 300, 300, 300, 350, cor_btn1)
        BresenhamReta.bresenham(self.tela, 500, 300, 500, 350, cor_btn1)

        letras_restart = "RESTART"
        for i, l in enumerate(letras_restart):
            desenhar_letra(l, 335 + (i * 18), 318, cor_btn1)

        if mouse_over_restart and clique[0]:
            self.fase_atual = 0
            self.carregar_fase(0)
            self.estado = "JOGANDO"
            pygame.event.clear()

        mouse_over_quit = 300 < mouse_pos[0] < 500 and 400 < mouse_pos[1] < 450
        cor_btn2 = VERMELHO_VIVO if mouse_over_quit else BRANCO

        BresenhamReta.bresenham(self.tela, 300, 400, 500, 400, cor_btn2)
        BresenhamReta.bresenham(self.tela, 300, 450, 500, 450, cor_btn2)
        BresenhamReta.bresenham(self.tela, 300, 400, 300, 450, cor_btn2)
        BresenhamReta.bresenham(self.tela, 500, 400, 500, 450, cor_btn2)

        letras_sair = "SAIR"
        for i, l in enumerate(letras_sair):
            desenhar_letra(l, 365 + (i * 20), 418, cor_btn2)

        if mouse_over_quit and clique[0]:
            pygame.quit()
            sys.exit()

    def sair(self):
        pygame.quit()
        sys.exit()
