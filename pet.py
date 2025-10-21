import pygame
import math

class Pet():
    def __init__(self, name, pos):
        self.name = name
        self.pos = pygame.Vector2(pos)

        self.max_hunger = 1
        self.hunger = self.max_hunger

        self.max_happiness = 1
        self.happiness = self.max_happiness

        self.decay_rate = 0.02

    def update(self, dt):
        self.hunger = self.hunger - ((self.decay_rate / 60) * dt)
        self.happiness = self.happiness - ((self.decay_rate / 60) * dt)

        # prevents attributes from going over or under 1 when feeding
        self.hunger = max(0.0, min(1.0, self.hunger))
        self.happiness = max(0.0, min(1.0, self.happiness))

        print(self.hunger)
        print(self.happiness, "\n")
    
    def draw(self, screen):
        s = pygame.Surface((240, 240), pygame.SRCALPHA)
        body_col = (230, 210, 170)
            
        # Body + ears
        pygame.draw.ellipse(s, body_col, (10, 30, 220, 200))
        pygame.draw.polygon(s, body_col, [(50, 50),(80,10),(110,50)])
        pygame.draw.polygon(s, body_col, [(130, 50),(160,10),(190,50)])

        # Eyes
        eye = (30,30,40)
        pygame.draw.circle(s, eye, (90, 120), 8)
        pygame.draw.circle(s, eye, (160,120), 8)

        cx, cy = 125, 155
        pygame.draw.arc(s, eye, (cx-20, cy-8, 40, 24), math.radians(160),  math.radians(20), 3)

        # Center the pet sprite onto the main screen
        rect = s.get_rect(center=self.pos)
        screen.blit(s, rect)

    

