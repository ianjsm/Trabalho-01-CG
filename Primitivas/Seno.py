import math
from Primitivas.SetPixel import setPixel

def desenhar_seno(superficie, largura, altura, cor,):
    amplitude = altura // 4
    centro_y = altura // 2
    frequencia = 2*math.pi / largura
    
    for x in range(largura):
        y = centro_y - int(math.sin(x*frequencia)*amplitude)
        
        setPixel(superficie, x, y, (0, 0, 0))