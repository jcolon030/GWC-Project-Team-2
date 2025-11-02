# scene.py
import pygame
from inventory import Inventory, ITEMS, ItemDef
from ui import Hotbar
from toys import Ball

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480

class Scene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.font = game.font
        self.small_font = game.small_font
        self.title_font = game.title_font

    def handle_event(self, event): 
        pass

    def update(self, dt: float): 
        pass

    def draw(self, screen: pygame.Surface): 
        pass

    def draw_shadow(self, y=SCREEN_HEIGHT//2 + 80, width=300, height=80, alpha=30):
        s = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (0,0,0,alpha), (0,0,width,height))
        self.screen.blit(s, (SCREEN_WIDTH//2 - width//2, y))

    # Used for Drawing Room Name and Instructions
    def _draw_title_right(self, text: str, x_margin=20, y=14, color=(25,35,60)):
        lbl = self.title_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

    def _draw_hint_right(self, text: str, x_margin=20, y=48, color=(40,50,80)):
        lbl = self.small_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

class LivingRoomScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (247, 239, 218)

        # --- inventory ---
        self.inv = Inventory()
        self.toys = []



        # --- UI ---
        self.hotbar = Hotbar(
            inventory=self.inv,
            items=ITEMS,
            origin=(20, SCREEN_HEIGHT - 64),
            slot_w=85, slot_h=44, pad=10,
            font=self.font, small_font=self.small_font, screen=self.screen,
            on_click_item=self._on_click_item
        )

        # --- hotbar layout ---
        self.slot_w, self.slot_h = 85, 44
        self.slot_pad = 10
        self.hotbar_origin = (20, SCREEN_HEIGHT - 64)

        self._slots = [] # Should include list[tuple[pygame.Rect, ItemDef]]
        self._hover_i = None  # which slot is hovered

    def _on_click_item(self, item):
        if item.kind == "toy":
            if self.inv.consume(item):
                if item.name == "Ball":
                    x = 260 + 40 * (len(self.toys)%5)
                self.toys.append(Ball(item,(x, 360), 20))
                
        if item.kind == "food":
            if self.inv.consume(item):
                if item.name == "Cookie":
                    self.game.pet.happiness = min(1.0, self.game.pet.happiness + 0.05)
                self.game.pet.feed(item.nutrition)

    # ---------- input ----------
    def handle_event(self, event):
        self.hotbar.handle_event(event)
        for t in self.toys:
            t.handle_event(event)

    # ---------- logic ----------
    def update(self, dt: float):
        self.game.pet.update(dt)
        for t in self.toys:
            t.update(dt)
            t.play(self.game.pet)

    # ---------- drawing ----------
    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        self.draw_shadow()
        self.game.pet.draw(screen)

        self.hotbar.draw()

        # right-aligned labels
        self._draw_title_right("Living Room")
        self._draw_hint_right("Click an item to feed the pet")

        for t in self.toys:
            t.draw(screen)


class BathroomScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (220, 240, 255)

    def handle_event(self, event): 
        pass

    def update(self, dt: float): 
        self.game.pet.update(dt)

    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        self.draw_shadow()
        self.game.pet.draw(screen)
        self._draw_title_right("Bathroom")
        self._draw_hint_right("Press L = Living Room, B = Bathroom")
