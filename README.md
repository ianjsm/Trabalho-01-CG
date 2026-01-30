# ECHO – Jogo 2D de Exploração por Ecolocalização

## Descrição do Projeto
ECHO é um jogo 2D de exploração no qual o jogador controla um morcego que deve atravessar um ambiente totalmente escuro. O mapa do jogo não é visível de forma contínua, sendo revelado apenas temporariamente por meio de ondas de eco emitidas pelo personagem, simulando o processo de ecolocalização utilizado por morcegos na natureza.

O jogo foi desenvolvido como parte da disciplina de Computação Gráfica, utilizando exclusivamente manipulação direta de pixels, sem o uso de bibliotecas gráficas avançadas.

---

## Objetivo do Jogo
O objetivo do jogo é guiar o morcego até o ponto final do mapa, utilizando estrategicamente o sistema de eco para revelar o caminho, evitando colisões com paredes invisíveis e fugindo de um vilão que o persegue durante a execução do jogo.

O jogador vence ao alcançar o objetivo antes que sua barra de vida se esgote ou que o vilão consiga capturá-lo.

---

## Mecânicas Principais
- Movimentação do morcego por meio das setas do teclado
- Sistema de eco que revela temporariamente o mapa
- Barra de vida que limita a quantidade de ecos emitidos
- Vilão que persegue o jogador pelo mapa
- Ambiente invisível baseado em memória espacial

---

## Representação Gráfica
Todos os elementos do jogo são desenhados pixel a pixel utilizando apenas funções básicas de manipulação de pixels (`setpixel`).  
Não são utilizados sprites prontos ou bibliotecas gráficas além das permitidas.

As cores representam semanticamente os elementos do jogo:
- Branco: morcego (personagem principal)
- Cinza: paredes e obstáculos
- Vermelho: vilão
- Verde: objetivo final
- Azul: ondas de eco


---

## Como Executar o Projeto

### Pré-requisitos
- Python 3.x
- Biblioteca PyGame instalada

### Instalação do PyGame
```bash
pip install pygame
```
## Caso o repositório já esteja clonado e você queira apenas atualizar:
```bash
git pull
```

## Em seguida, acesse a pasta do projeto:
```bash
cd Trabalho-01-CG
```
---

## Instalação das Dependências

O projeto utiliza a biblioteca PyGame.

Instale com:
```bash
pip install pygame
```
Caso esteja utilizando Linux ou MacOS:
```bash
pip3 install pygame
```
---

## 4. Execução do Jogo

Após a instalação das dependências, execute:
```bash
python main.py
```
ou
```bash
python3 main.py
```

Ao executar o comando, a janela do jogo será aberta e o jogador poderá interagir utilizando o teclado.

---

## Controles

Setas do teclado: movimentação do morcego

Espaço: emissão do eco

---

## Observações Finais

Este projeto foi desenvolvido com fins acadêmicos para a disciplina de Computação Gráfica, respeitando as restrições propostas, com foco na aplicação de conceitos fundamentais, organização do código e criatividade no design do jogo.
