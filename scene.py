# scene.py
import pygame
from inventory import Inventory, ITEMS, ItemDef

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480

class Scene:
    def __init__(self, game):
        self.game = game
        self.screen: pygame.Surface = game.screen
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


class LivingRoomScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (247, 239, 218)

        # --- inventory ---
        self.inv = Inventory()

        # --- hotbar layout ---
        self.slot_w, self.slot_h = 85, 44
        self.slot_pad = 10
        self.hotbar_origin = (20, SCREEN_HEIGHT - 64)

        self._slots = [] # Should include list[tuple[pygame.Rect, ItemDef]]
        self._rebuild_slots()
        self._hover_i: int | None = None  # which slot is hovered

    # ---------- input ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._hover_i = None
            for i, (rect, _) in enumerate(self._slots):
                if rect.collidepoint((mx, my)):
                    self._hover_i = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_i is not None:
                rect, item = self._slots[self._hover_i]
                # click = use one item (if available), feed pet immediately
                if self.inv.consume(item):
                    # small happiness bump for cookie example (optional)
                    if item.name == "Cookie":
                        self.game.pet.happiness = min(1.0, self.game.pet.happiness + 0.05)
                    # always add hunger from item nutrition
                    if hasattr(self.game.pet, "feed"):
                        self.game.pet.feed(item.nutrition)
                    else:
                        self.game.pet.hunger = min(1.0, self.game.pet.hunger + item.nutrition)

    # ---------- logic ----------
    def update(self, dt: float):
        self.game.pet.update(dt)

    # ---------- drawing ----------
    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        self.draw_shadow()
        self.game.pet.draw(screen)

        self._draw_hotbar(screen)

        # right-aligned labels
        self._draw_title_right("Living Room")
        self._draw_hint_right("Click an item to feed the pet")

    # ---------- helpers ----------
    def _rebuild_slots(self):
        self._slots.clear()
        x0, y0 = self.hotbar_origin
        for i, item in enumerate(ITEMS):
            x = x0 + i * (self.slot_w + self.slot_pad)
            rect = pygame.Rect(x, y0, self.slot_w, self.slot_h)
            self._slots.append((rect, item))

    def _draw_hotbar(self, screen: pygame.Surface):
        # background strip (optional)
        total_w = len(ITEMS)*(self.slot_w+self.slot_pad) - self.slot_pad
        strip = pygame.Rect(self.hotbar_origin[0]-10, self.hotbar_origin[1]-8,
                            total_w+20, self.slot_h+16)
        pygame.draw.rect(screen, (238, 240, 245), strip, border_radius=10)
        pygame.draw.rect(screen, (70, 90, 130), strip, width=2, border_radius=10)

        for i, (rect, item) in enumerate(self._slots):
            # "puff" on hover: inflate the rect a bit
            draw_rect = rect.inflate(8, 6) if i == self._hover_i else rect

            # if out of stock, tint background
            has_any = self.inv.count(item) > 0
            base_col = (245,245,250) if has_any else (230,230,235)

            pygame.draw.rect(screen, base_col, draw_rect, border_radius=8)
            pygame.draw.rect(screen, (70,90,130), draw_rect, width=2, border_radius=8)

            # color swatch
            sw = pygame.Rect(draw_rect.x+8, draw_rect.y+8, 20, 20)
            pygame.draw.rect(screen, item.color, sw, border_radius=4)
            pygame.draw.rect(screen, (60,60,80), sw, width=1, border_radius=4)

            # label + count
            label = self.small_font.render(item.name, True, (30,40,70))
            screen.blit(label, (draw_rect.x+34, draw_rect.y+6))
            cnt = self.inv.count(item)
            count_txt = self.small_font.render(f"x{cnt}", True, (30,40,70))
            screen.blit(count_txt, (draw_rect.x+34, draw_rect.y+22))

            # out-of-stock overlay (light hatch)
            if not has_any:
                overlay = pygame.Surface((draw_rect.w, draw_rect.h), pygame.SRCALPHA)
                overlay.fill((0,0,0,40))
                screen.blit(overlay, draw_rect.topleft)

    # Used for Drawing Room Name and Instructions
    def _draw_title_right(self, text: str, x_margin=20, y=14, color=(25,35,60)):
        lbl = self.title_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

    def _draw_hint_right(self, text: str, x_margin=20, y=48, color=(40,50,80)):
        lbl = self.small_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)


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

    # Used for drawing room name and instructions
    def _draw_title_right(self, text: str, x_margin=20, y=14, color=(25,35,60)):
        lbl = self.title_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

    def _draw_hint_right(self, text: str, x_margin=20, y=48, color=(40,50,80)):
        lbl = self.small_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)
