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
        screen.blit(self.img, anchor)

    # inside class Pet
    def feed(self, amount: float):
        self.hunger = min(1.0, self.hunger + float(amount))

    def get_rect(self, center=None) -> pygame.Rect:
        """
        Returns the rect used when drawing the pet.
        Use the same center you pass to draw().
        """
        cx, cy = center if center is not None else (self.pos.x, self.pos.y)
        rect = self.img.get_rect()
        rect.center = (int(cx), int(cy))
        return rect




    

