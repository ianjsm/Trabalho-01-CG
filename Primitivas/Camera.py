class Camera:
    def __init__(self, largura_mundo, altura_mundo, largura_tela, altura_tela):

        self.mundo_x = 0
        self.mundo_y = 0
        self.largura_janela = largura_tela
        self.altura_janela = altura_tela

        self.viewport_x = 0
        self.viewport_y = 0
        self.viewport_w = largura_tela
        self.viewport_h = altura_tela

    def mundo_para_tela(self, x_mundo, y_mundo):

        x_tela = (x_mundo - self.mundo_x) * (
            self.viewport_w / self.largura_janela
        ) + self.viewport_x
        y_tela = (y_mundo - self.mundo_y) * (
            self.viewport_h / self.altura_janela
        ) + self.viewport_y

        return int(x_tela), int(y_tela)

    def focar(self, x, y):

        self.mundo_x = x - self.largura_janela // 2
        self.mundo_y = y - self.altura_janela // 2
