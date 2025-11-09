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

    # Used for drawing hunger and happiness
    def draw_bar(self, x, y, w, h, value, label, color):
        value = max(0, min(1, value))
        bg_rect = pygame.Rect(x, y, w, h)
        inner_rect = pygame.Rect(x + 3, y + 3, int((w - 6) * value), h - 6)

        # Draws rectangles to the screen
        pygame.draw.rect(self.game.screen, (60, 60, 80), bg_rect, 2, border_radius=6) # border
        pygame.draw.rect(self.game.screen, color, inner_rect, border_radius=6) # fill

        # label
        text = self.font.render(f"{label}: {int(value * 100)}%", True, (30, 30, 50))
        self.screen.blit(text, (x, y - 22)) # Renders text to screen

    def _draw_coin_hud(self, x=40, y=140):
        label = self.font.render(f"Coins: {self.game.wallet.coins}", True, (30,30,50))
        self.screen.blit(label, (x, y))

class LivingRoomScene(Scene):
    def __init__(self, game):
        super().__init__(game)
    
        self.bg_color = (247, 239, 218)

        self.toys = [] # should hold toy objects

        self.hotbar = Hotbar(
            inventory=self.game.inv,
            items=ITEMS,
            origin=(20, SCREEN_HEIGHT - 64),
            slot_w=85, slot_h=44, pad=10,
            font=self.font, small_font=self.small_font, screen=self.screen,
            on_click_item=self._on_click_item
        )

    def _on_click_item(self, item: ItemDef):
        if item.kind == "food":
            if self.game.inv.consume(item):
                if item.name == "Cookie":
                    self.game.pet.happiness = min(1.0, self.game.pet.happiness + 0.05)
                self.game.pet.feed(item.nutrition) # APPLE.nutrition = 0.02

        elif item.kind == "toy":
            if self.game.inv.consume(item):
                x = 260 + 40 * (len(self.toys) % 5)
                self.toys.append(Ball(item=item, pos=(x, 360)))


    def handle_event(self, event):
        self.hotbar.handle_event(event)

        # Handle specific toy events (ex. bouncing)
        for t in self.toys:
            t.handle_event(event)

    def update(self, dt):
        super().update(dt)

        # Updates active toys
        for t in self.toys:
            t.update(dt)
            t.resolve_rewards(self.game.pet) 

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.draw_shadow()
        self.game.pet.draw(screen)
        
        # UI
        self.hotbar.draw()
        self._draw_title_right("Living Room")
        self._draw_hint_right("Click an item to feed the pet")
        self.draw_bar(40, 40, 200, 20, self.game.pet.hunger, "Hunger", (255, 100, 100))
        self.draw_bar(40, 100, 200, 20, self.game.pet.happiness, "Happiness", (100, 180, 255))
        self._draw_coin_hud()

        # For Drawing Active Toys
        for t in self.toys:
            t.draw(screen)

class BathroomScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (220, 240, 255)

        # --- centered shower head ---
        cx = SCREEN_WIDTH // 2
        self.head_rect = pygame.Rect(0, 0, 40, 26)      # shower head
        self.head_rect.center = (cx, 92)
        self.arm_start = (cx - 120, 80)                 # arm comes in from left
        self.handle_rect = pygame.Rect(0, 0, 10, 18)    # little knob on right side
        self.handle_rect.midleft = (self.head_rect.right + 6, self.head_rect.centery)

        # droplet spawn origin (center-bottom of head)
        self.nozzle_center = (self.head_rect.centerx, self.head_rect.bottom - 2)

        # --- Shower button (toggle ON/OFF) ---
        self.spraying = False
        self.shower_btn = pygame.Rect(20, 170, 110, 36)

        # --- droplets (visual only) ---
        self.droplets = []            # list of dict(x, y, vy)
        self.spawn_rate = 60.0        # droplets per second when spraying
        self._spawn_accum = 0.0

        # gentle happiness gain while showering
        self.happy_rate = 0.01        # per second

    # ---------- input ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.shower_btn.collidepoint(event.pos):
                self.spraying = not self.spraying
 
    # ---------- logic ----------
    def update(self, dt: float):
        if self.spraying:
            # spawn droplets
            self._spawn_accum += self.spawn_rate * dt
            while self._spawn_accum >= 1.0:
                self._spawn_accum -= 1.0
                self._spawn_droplet()
            # happiness while showering
            self.game.pet.happiness = min(1.0, self.game.pet.happiness + self.happy_rate * dt)

        self._update_droplets(dt)

    # ---------- draw (order: wall → shower → pet → droplets → UI) ----------
    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)
        self._draw_shower(screen)

        # pet
        self.draw_shadow(y=SCREEN_HEIGHT//2 + 80, width=320, height=60, alpha=40)
        self.game.pet.draw(screen)

        # droplets
        self._draw_droplets(screen)

        # UI
        self._draw_title_right("Bathroom")
        self._draw_hint_right("Toggle the Shower button to spray")
        self._draw_shower_button(screen)
        self.draw_bar(40, 40, 200, 20, self.game.pet.hunger, "Hunger", (255, 100, 100))
        self.draw_bar(40, 100, 200, 20, self.game.pet.happiness, "Happiness", (100, 180, 255))
        self._draw_coin_hud()

    # ---------- droplets ----------
    def _spawn_droplet(self):
        import random
        x = self.nozzle_center[0] + random.uniform(-5, 5)
        y = self.nozzle_center[1] + random.uniform(-2, 2)
        vy = random.uniform(300, 380)
        self.droplets.append({"x": x, "y": y, "vy": vy})

    def _update_droplets(self, dt: float):
        alive = []
        for d in self.droplets:
            d["y"] += d["vy"] * dt
            if d["y"] < SCREEN_HEIGHT - 20:  # drop off-screen cleanup
                alive.append(d)
        self.droplets = alive

    # ---------- draw pieces ----------
    def _draw_shower(self, screen):
        arm_col = (90, 110, 140)
        pygame.draw.line(screen, arm_col, self.arm_start, (self.head_rect.left, self.head_rect.centery), 6)
        pygame.draw.rect(screen, (200, 210, 230), self.head_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 90, 110), self.head_rect, width=2, border_radius=8)
        pygame.draw.rect(screen, (190, 200, 210), self.handle_rect, border_radius=4)
        pygame.draw.rect(screen, (80, 90, 110), self.handle_rect, width=2, border_radius=4)

    def _draw_droplets(self, screen):
        for d in self.droplets:
            pygame.draw.circle(screen, (150, 190, 255), (int(d["x"]), int(d["y"])), 3)

    def _draw_shower_button(self, screen):
        bg = (140, 205, 255) if self.spraying else (200, 215, 235)
        pygame.draw.rect(screen, bg, self.shower_btn, border_radius=8)
        pygame.draw.rect(screen, (70, 90, 130), self.shower_btn, width=2, border_radius=8)
        lbl = self.font.render("Shower", True, (30, 40, 60))
        rect = lbl.get_rect(center=self.shower_btn.center)
        screen.blit(lbl, rect)

class SupermarketScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg_color = (235, 245, 255)

        # grid layout
        self.card_w, self.card_h = 160, 78
        self.pad = 14
        self.origin = (36, 280)
        self.cols = 3

        # build static card rects
        self._cards = [] # should contain list[tuple[pygame.Rect, ItemDef]]
        self._build_grid()

        # per-item stock (auto-updates on buy)
        self.stock = {it.name: 4 for it in ITEMS} # holds dict[str, int] which is the item name and its price

        # hover
        self._hover_i = None

        # tiny flash feedback when buying / blocked actions
        self._flash_text = ""
        self._flash_timer = 0.0
        self._flash_color = (30, 40, 70)

    # ---------- layout ----------
    def _build_grid(self):
        self._cards.clear()
        x0, y0 = self.origin
        for i, item in enumerate(ITEMS):
            r = i // self.cols
            c = i % self.cols
            x = x0 + c * (self.card_w + self.pad)
            y = y0 + r * (self.card_h + self.pad)
            self._cards.append((pygame.Rect(x, y, self.card_w, self.card_h), item))

    # ---------- input ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._hover_i = None
            for i, (rect, _) in enumerate(self._cards):
                if rect.collidepoint((mx, my)):
                    self._hover_i = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_i is not None:
                rect, item = self._cards[self._hover_i]
                name = item.name
                # checks
                if self.stock.get(name, 0) <= 0:
                    self._flash("Out of stock")
                    return
                if not self.game.wallet.can_afford(item.price):
                    self._flash("Not enough coins")
                    return
                # do purchase
                if self.game.wallet.spend(item.price):
                    self.game.inv.give(item, 1)
                    self.stock[name] = self.stock.get(name, 0) - 1
                    self._flash(f"Bought {name}")

    # ---------- logic ----------
    def update(self, dt: float):
        super().update(dt)  # pet decay + wallet passive income
        # flash lifetime
        if self._flash_timer > 0.0:
            self._flash_timer -= dt
            if self._flash_timer <= 0.0:
                self._flash_text = ""

    # ---------- drawing ----------
    def draw(self, screen: pygame.Surface):
        screen.fill(self.bg_color)

        # simple storefront shelving using shapes
        self._draw_shelves(screen)

        # cards
        self._draw_cards(screen)

        # scene HUD
        self._draw_title_right("Shop")
        self._draw_hint_right("Click a card to buy • Press L = Living, B = Bath")
        self.draw_bar(40, 40, 200, 20, self.game.pet.hunger, "Hunger", (255, 100, 100))
        self.draw_bar(40, 100, 200, 20, self.game.pet.happiness, "Happiness", (100, 180, 255))
        self._draw_coin_hud()

        # tiny flash feedback near bottom
        if self._flash_text:
            lbl = self.font.render(self._flash_text, True, self._flash_color)
            rect = lbl.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
            screen.blit(lbl, rect)

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
        for i, (rect, item) in enumerate(self._cards):
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

    def _flash(self, text: str, seconds: float = 1.3, color=(30,40,70)):
        self._flash_text = text
        self._flash_timer = seconds
        self._flash_color = color

class TitleScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.bg = pygame.image.load("assets/ball-1.png.png").convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.title_font = pygame.font.SysFont(None, 72)
        self.button = pygame.Rect(280, 340, 160, 60)
    def draw(self, screen):
        screen.blit(self.bg, (0,0))
        lbl = self.title_font.render("Virtual Pet", True, (50,60,80))
        screen.blit(lbl, (180, 140))
        pygame.draw.rect(screen, (180,200,240), self.button, border_radius=12)
        pygame.draw.rect(screen, (60,70,100), self.button, 2, border_radius=12)
        txt = self.font.render("Start", True, (30,40,70))
        screen.blit(txt, txt.get_rect(center=self.button.center))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.button.collidepoint(event.pos):
            self.game.change_scene("living")
