import pygame
from pet import Pet

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480

FPS = 60

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Our Pet Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        self.pet = Pet("Bob", (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 20))
        self.bg_color = (247, 239, 218)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.pet.update(dt)

            self.screen.fill(self.bg_color)
            self.pet.draw(self.screen)
            pygame.display.flip()
        pygame.quit()

if __name__ == "__main__":
    Game().run()