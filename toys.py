import pygame

class Ball:
    def __init__(self, item, pos=(200, 360), radius=20):
        self.item = item
        self.pos = pygame.Vector2(pos)
        self.radius = radius
        self.vy = 0.0
        self.bouncing = False

        # Track pending happiness reward
        self._happy_pending = False
        self._happy_boost = 0.003  # small boost per click (~0.3%)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # detect click inside circle
            if (mx - self.pos.x)**2 + (my - self.pos.y)**2 <= self.radius**2:
                self.bouncing = True
                self.vy = -260
                self._happy_pending = True  # give reward once per click

    def update(self, dt):
        if not self.bouncing:
            return

        # simple gravity and bounce
        self.vy += 600 * dt
        self.pos.y += self.vy * dt
        if self.pos.y >= 360:
            self.pos.y = 360
            self.vy *= -0.45
            if abs(self.vy) < 40:
                self.bouncing = False

    def resolve_rewards(self, pet):
        if self._happy_pending:
            pet.happiness = min(1.0, pet.happiness + self._happy_boost)
            self._happy_pending = False

    def draw(self, screen):
        pygame.draw.circle(screen, self.item.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(screen, (60, 60, 80), (int(self.pos.x), int(self.pos.y)), self.radius, 2)
