"""
main.py - Ponto de entrada do jogo de luta 2D
Inicializa o Pygame e controla o fluxo principal entre telas.
"""

import pygame
import sys
from game import Game


def main():
    pygame.init()
    pygame.mixer.init()

    # Configurações da janela
    SCREEN_WIDTH = 1024
    SCREEN_HEIGHT = 576
    FPS = 60
    TITLE = "PyFighter 2D"

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Inicia o jogo principal
    game = Game(screen, clock, FPS)
    game.run()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
