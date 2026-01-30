import math


class Transformador:
    @staticmethod
    def transladar(pontos, dx, dy):
        return [(x + dx, y + dy) for x, y in pontos]

    @staticmethod
    def escalar(pontos, sx, sy, pivô=(0, 0)):

        novos_pontos = []
        px, py = pivô
        for x, y in pontos:
            nx = px + (x - px) * sx
            ny = py + (y - py) * sy
            novos_pontos.append((nx, ny))
        return novos_pontos

    @staticmethod
    def rotacionar(pontos, angulo_graus, pivô=(0, 0)):

        angulo_rad = math.radians(angulo_graus)
        cos_a = math.cos(angulo_rad)
        sin_a = math.sin(angulo_rad)
        px, py = pivô

        novos_pontos = []
        for x, y in pontos:

            nx = px + (x - px) * cos_a - (y - py) * sin_a
            ny = py + (x - px) * sin_a + (y - py) * cos_a
            novos_pontos.append((nx, ny))
        return novos_pontos
