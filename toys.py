import pygame

class Ball: 
    def __init__(self, item, position,radius):
        self.item = item
        self.position = pygame.Vector2(position)
        self.radius = radius
        self.speed = 0
        self.bouncing = False
        self.happyPending = False
        self.happyBoost = 0.003
    def handle_event(self, event): 
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx,my = event.pos
            if (mx - self.position.x) ** 2 + (my - self.position.y) ** 2 <= self.radius ** 2:
                self.bouncing = True
                self.speed = -200
                self.happyPending = True
    def play(self,pet):
        if self.happyPending:
            pet.happiness = min(1.0, pet.happiness + float(self.happyBoost))
            self.happyPending = False
    def update(self, dt: float): 
        if not self.bouncing:
            return
        self.speed += 600 * dt
        self.position.y += self.speed * dt
        if self.position.y >= 360:
            self.position.y = 360
            self.speed *= -0.45
            if abs(self.speed) < 40:
                self.bouncing = False
    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.item.color, (self.position.x,self.position.y), self.radius)
        pygame.draw.circle(screen, (60,60,80), (self.position.x,self.position.y), self.radius,2)
