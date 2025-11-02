import pygame
from pet import Pet
from scene import Scene, LivingRoomScene, BathroomScene,  StoreScene  # <-- import scenes
from wallet import Wallet
from inventory import Inventory

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
FPS = 60

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Our Pet Game")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts
        self.title_font = pygame.font.SysFont(None, 36)
        self.font = pygame.font.SysFont(None, 22)
        self.small_font = pygame.font.SysFont(None, 20)

        # Shared pet (scenes will update/draw this)
        self.pet = Pet("Bob", (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 20))
        self.wallet = Wallet()

        # --- inventory ---
        self.inv = Inventory()

        # Scene manager
        self.scenes = {
            "living": LivingRoomScene(self),
            "bathroom": BathroomScene(self),
            "store": StoreScene(self),
        }

        self.current = self.scenes["living"] # self.current is a Scene class

    def change_scene(self, name):
        if name in self.scenes:
            self.current = self.scenes[name]

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # record key for on-screen debug
                    try:
                        self._last_key = f"KEYDOWN: {pygame.key.name(event.key)}"
                    except Exception:
                        self._last_key = f"KEYDOWN: {event.key}"

                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_b:
                        self.change_scene("bathroom")
                    elif event.key == pygame.K_l:
                        self.change_scene("living")
                    elif event.key == pygame.K_s:
                        self.change_scene("store")

                # pass all events to active scene (room-specific input later)
                self.current.handle_event(event)

            # Update our Wallet
            self.wallet.update(dt)

            # --- UPDATE & DRAW via SCENE ---
            # Let the scene update the pet and draw the room + pet
            self.current.update(dt)
            self.current.draw(self.screen)

            # --- GLOBAL OVERLAYS (draw AFTER scene so they sit on top) ---
            self.draw_bar(40, 40, 200, 20, self.pet.hunger, "Hunger", (255, 100, 100))
            self.draw_bar(40, 100, 200, 20, self.pet.happiness, "Happiness", (100, 180, 255))

            # Draw Wallet
            self._draw_coin_hud()

            pygame.display.flip()

        pygame.quit()

    # ---------- Helpers ----------
    def draw_bar(self, x, y, w, h, value, label, color):
        value = max(0, min(1, value))
        bg_rect = pygame.Rect(x, y, w, h)
        inner_rect = pygame.Rect(x + 3, y + 3, int((w - 6) * value), h - 6)

        # Draws rectangles to the screen
        pygame.draw.rect(self.screen, (60, 60, 80), bg_rect, 2, border_radius=6) # border
        pygame.draw.rect(self.screen, color, inner_rect, border_radius=6) # fill

        # label
        text = self.font.render(f"{label}: {int(value * 100)}%", True, (30, 30, 50))
        self.screen.blit(text, (x, y - 22)) # Renders text to screen

    def _draw_coin_hud(self, x=40, y=140):
        label = self.font.render(f"Coins: {self.wallet.coins}", True, (30,30,50))
        self.screen.blit(label, (x, y))

if __name__ == "__main__":
    Game().run()
