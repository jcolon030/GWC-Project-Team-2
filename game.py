import pygame
from pet import Pet
from scene import Scene, LivingRoomScene, BathroomScene, SupermarketScene, TitleScene  # <-- import scenes
from wallet import Wallet
from inventory import Inventory, ITEMS
import json
from pathlib import Path

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
FPS = 60

SAVE_PATH = Path("savegame.json")

class Game():
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pocket Pet")
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
        self.wallet = Wallet( start_coins=10, income_every=5.0, income_amount=1 )

        # Scene manager
        self.scenes = {
            "living": LivingRoomScene(self),
            "bathroom": BathroomScene(self),
            "shop" : SupermarketScene(self),
            "title" : TitleScene(self)
        }

        self.current_title = "title"
        self.current = self.scenes[self.current_title] # self.current is a Scene class, self.scenes['title']

        self.time_scale = 0.0 # Used to "pause" game
        self.continued = 0 # is "0" if this is first time game is being ran

        save_check = self.load_state()

        if save_check:
            self.continued = 1

    def change_scene(self, name):
        if name in self.scenes:
            self.current = self.scenes[name] 
            self.current_title = name

    def run(self):
        running = True
        while running:
            raw_dt = self.clock.tick(FPS) / 1000
            dt = raw_dt * self.time_scale # 0

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

            # --- Update & Draw via Scene ---
            self.current.update(dt)
            self.current.draw(self.screen)

            pygame.display.flip()

        self.save_state()
        pygame.quit()

    # --------- Save Functions ------------

    def save_state(self):
        data = {
            "pet": {
                "hunger": self.pet.hunger,
                "happiness": self.pet.happiness,
            },
            "wallet": {
                "coins": int(getattr(self.wallet, "coins", 0.0)),
            },
            "inventory": {
                # inventory counts by item name
                item.name: self.inv.count(item) for item in ITEMS
            },
            "scene": "title",
        }

        try:
            with open(SAVE_PATH, "w") as f:
                json.dump(data, f)
            print("Saved game.")
        except Exception as e:
            print("Failed to save:", e)

    def load_state(self):
        if not SAVE_PATH.exists():
            print("No save file yet, starting fresh.")
            return

        try:
            with open(SAVE_PATH, "r") as f:
                data = json.load(f)
        except Exception as e:
            print("Failed to load save:", e)
            return

        # --- pet ---
        pet_data = data.get("pet", {})
        self.pet.hunger = float(pet_data.get("hunger", self.pet.hunger))
        self.pet.happiness = float(pet_data.get("happiness", self.pet.happiness))

        # --- wallet ---
        wallet_data = data.get("wallet", {})
        if hasattr(self.wallet, "coins"):
            self.wallet.coins = int(wallet_data.get("coins", self.wallet.coins))

        # --- inventory ---
        inv_data = data.get("inventory", {})
        # Clear and re-give items based on saved counts
        self.inv.clear()
        for item in ITEMS:
            count = int(inv_data.get(item.name, 0))
            if count > 0:
                self.inv.give(item, count)

        # --- scene ---
        scene_name = data.get("scene", "living")
        if scene_name in self.scenes:
            self.current_name = scene_name
            self.current = self.scenes[scene_name]

        print("Loaded save.")
        return True

if __name__ == "__main__":
    Game().run()
