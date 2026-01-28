import pygame
from rainsystem import RainSystem
from constants import *

def main():
    pygame.init()
    window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Rain with wind")

    system = RainSystem(pygame.image.load("drop.png"))
    clock = pygame.time.Clock()

    mouse_pos = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
    mouse_pressed = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed = False

        dt = clock.get_time() / 1000.0

        window.fill((20, 20, 20))
        system.update(dt, mouse_pos, mouse_pressed)
        system.draw(window)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
