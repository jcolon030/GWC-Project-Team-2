import pygame
import math

class Pet():
    def __init__(self, name, pos):
        self.name = name
        self.pos = pygame.Vector2(pos)

        self.img = pygame.image.load("assets/cat.png").convert_alpha()
        self.img = pygame.transform.scale(self.img, (200,200))

        # Hunger Variable
        self.max_hunger = 1
        self.hunger = self.max_hunger

        # Happiness Variable
        self.max_happiness = 1
        self.happiness = self.max_happiness

        self.decay_rate = 0.1

    def update(self, dt):
        self.hunger = self.hunger - ((self.decay_rate / 60) * dt)
        self.happiness = self.happiness - ((self.decay_rate / 60) * dt)

        # prevents attributes from going over or under 1 when feeding
        self.hunger = max(0.0, min(1.0, self.hunger))
        self.happiness = max(0.0, min(1.0, self.happiness))

        print(self.hunger)
        print(self.happiness, "\n")
    
    def draw(self, screen, anchor):
        rect = self.img.get_rect()
        rect.center = (int(anchor[0]), int(anchor[1]))
        screen.blit(self.img, rect)

    def feed(self, amount: float):
        self.hunger = min(1.0, self.hunger + float(amount))

    def get_rect(self, center=None) -> pygame.Rect:
        """Return the same rect used in draw()."""
        if center is None:
            center = (self.pos.x, self.pos.y)

        rect = self.img.get_rect()
        rect.center = (int(center[0]), int(center[1]))
        return rect




    

