import pygame
from pet import Pet
from scene import Scene, LivingRoomScene, BathroomScene, SupermarketScene, TitleScene  # <-- import scenes
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

        # Shared Inventory and Wallet
        self.inv = Inventory()
        self.wallet = Wallet( start_coins=10, income_every=6.0, income_amount=1 )

        # Scene manager
        self.scenes = {
            "living": LivingRoomScene(self),
            "bathroom": BathroomScene(self),
            "shop" : SupermarketScene(self),
            "title" : TitleScene(self)
        }

        self.current = self.scenes["title"] # self.current is a Scene class

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
                        self.change_scene("shop")

                # pass all events to active scene (room-specific input later)
                self.current.handle_event(event)

            # Update each object
            self.pet.update(dt)
            self.wallet.update(dt)

            # --- UPDATE & DRAW via SCENE ---
            # Let the scene update the pet and draw the room + pet
            self.current.update(dt)
            self.current.draw(self.screen)

            # --- GLOBAL OVERLAYS (draw AFTER scene so they sit on top) ---
            #self.draw_bar(40, 40, 200, 20, self.pet.hunger, "Hunger", (255, 100, 100))
            #self.draw_bar(40, 100, 200, 20, self.pet.happiness, "Happiness", (100, 180, 255))

            # Draw Wallet
            #self._draw_coin_hud()

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    Game().run()
