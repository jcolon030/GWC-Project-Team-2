# scene.py
import pygame
from inventory import Inventory, ITEMS, ItemDef
from ui import Hotbar

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

        # --- UI ---
        self.hotbar = Hotbar(
            inventory=self.game.inv,
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
        if item.kind == "food":
            if self.game.inv.consume(item):
                if item.name == "Cookie":
                    self.game.pet.happiness = min(1.0, self.game.pet.happiness + 0.05)
                self.game.pet.feed(item.nutrition)

    # ---------- input ----------
    def handle_event(self, event):
        self.hotbar.handle_event(event)

    # ---------- logic ----------
    def update(self, dt: float):
        self.game.pet.update(dt)

    # ---------- drawing ----------
    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        self.draw_shadow()
        self.game.pet.draw(screen)

        self.hotbar.draw()

        # right-aligned labels
        self._draw_title_right("Living Room")
        self._draw_hint_right("Click an item to feed the pet")


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

class StoreScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (255, 237, 232)
        self.card_w, self.card_h = 160, 78
        self.pad = 14
        self.origin = (36, 320)
        self.cols = 3
        self.cards = []
        self.build_grid()
        self.stock = {it.name: 4 for it in ITEMS}
        self.hover_i = None

    def build_grid(self):
        self.cards.clear()
        x0, y0 = self.origin
        for i, card in enumerate(self.cards):
            r = i // self.cols
            c = i % self.cols
            x = x0 + c * (self.card_w + self.pad)
            y = y0 + r * (self.card_h + self.pad)
            rect = pygame.Rect(x, y, self.card_w, self.card_h)
            self.cards.append((rect, card))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_i = None
            for i, (rect, _) in enumerate (self.cards):
                if rect.collidepoint((mx,my)):
                    self.hover_i = i
                    break
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hover_i is not None:
                _, item = self.cards[self.hover_i]
                if self.stock.get(item.name) <= 0:
                    print("Out of Stock")
                    return
                if not self.game.wallet.can_afford(item.price):
                    print("Not enough money!")
                    return
                if self.game.wallet.spend(item.price):
                    self.game.inv.give(item, 1)
                    self.stock[item.name] = self.stock.get(item.name) - 1
                    print("Purchased!")

    def update(self, dt: float):
        self.game.pet.update(dt)

    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)

        # simple storefront shelving using shapes
        self._draw_shelves(screen)

        # cards
        self._draw_cards(screen)

        # scene HUD
        self._draw_title_right("Shop")
        self._draw_hint_right("Click a card to buy • Press L = Living, B = Bath")

    # ---------- helpers ----------
    def _draw_shelves(self, screen):
        # 3 horizontal shelves (rounded rectangles)
        shelf_col = (220, 230, 245)
        edge_col  = (70, 90, 130)
        y = self.origin[1] - 18
        for _ in range(2):
            shelf = pygame.Rect(20, y, SCREEN_WIDTH - 40, 10)
            pygame.draw.rect(screen, shelf_col, shelf, border_radius=6)
            pygame.draw.rect(screen, edge_col, shelf, width=2, border_radius=6)
            y += self.card_h + self.pad

    def _draw_cards(self, screen):
        for i, (rect, item) in enumerate(self.cards):
            stock = self.stock.get(item.name, 0)
            is_hover = (i == self._hover_i)

            card_rect = rect.inflate(8, 6) if is_hover else rect
            bg_col = (245, 248, 255) if stock > 0 else (234, 236, 240)

            # card background + border
            pygame.draw.rect(screen, bg_col, card_rect, border_radius=10)
            pygame.draw.rect(screen, (70, 90, 130), card_rect, width=2, border_radius=10)

            # color swatch “product”
            sw = pygame.Rect(card_rect.x + 10, card_rect.y + 12, 28, 28)
            pygame.draw.rect(screen, item.color, sw, border_radius=6)
            pygame.draw.rect(screen, (60, 60, 80), sw, width=2, border_radius=6)

            # name / price / stock
            name_lbl  = self.font.render(item.name, True, (30,40,70))
            price_lbl = self.small_font.render(f"🪙 {item.price}", True, (40,60,90))
            stock_lbl = self.small_font.render(f"Stock: {stock}", True, (50,60,90))

            screen.blit(name_lbl,  (card_rect.x + 48, card_rect.y + 8))
            screen.blit(price_lbl, (card_rect.x + 48, card_rect.y + 30))
            screen.blit(stock_lbl, (card_rect.x + 48, card_rect.y + 48))

            # gray overlay if out-of-stock
            if stock <= 0:
                overlay = pygame.Surface((card_rect.w, card_rect.h), pygame.SRCALPHA)
                overlay.fill((0,0,0,50))
                screen.blit(overlay, card_rect.topleft)