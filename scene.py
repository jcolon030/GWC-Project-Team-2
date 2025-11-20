import pygame
from inventory import Inventory, ITEMS, ItemDef
from toys import Ball
from ui import Hotbar

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480

# Parent Class, used to hold data persistent across all the child scenes
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

    # Used for Drawing Room Name and Instructions
    def _draw_title_right(self, text: str, x_margin=20, y=14, color=(255,255,255)):
        lbl = self.title_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

    def _draw_hint_right(self, text: str, x_margin=20, y=48, color=(255,255,255)):
        lbl = self.small_font.render(text, True, color)
        rect = lbl.get_rect(topright=(SCREEN_WIDTH - x_margin, y))
        self.screen.blit(lbl, rect)

    # Used for drawing hunger and happiness
    def draw_bar(self, x, y, w, h, value, label, color):
        value = max(0, min(1, value))
        bg_block = pygame.Rect(x-2, y-2, w + 5, h + 5)
        bg_rect = pygame.Rect(x, y, w, h)
        inner_rect = pygame.Rect(x + 3, y + 3, int((w - 6) * value), h - 6)

        # Draws rectangles to the screen
        pygame.draw.rect(self.game.screen, (255,255,255), bg_block, border_radius=6)
        pygame.draw.rect(self.game.screen, (60, 60, 80), bg_rect, 2, border_radius=6) # border
        pygame.draw.rect(self.game.screen, color, inner_rect, border_radius=6) # fill

        # label
        text = self.font.render(f"{label}: {int(value * 100)}%", True, (255,255,255))
        self.screen.blit(text, (x, y - 22)) # Renders text to screen

    def _draw_coin_hud(self, x=40, y=140):
        label = self.font.render(f"Coins: {self.game.wallet.coins}", True, (255,255,255))
        self.screen.blit(label, (x, y))

class LivingRoomScene(Scene):
    def __init__(self, game):
        super().__init__(game)

        self.bg = pygame.image.load("assets/living_room.png").convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.pet_anchor = (390, 290)

        self.toys = [] # should hold toy objects

        self.hotbar = Hotbar(
            inventory=self.game.inv,
            items=ITEMS,
            origin=(40, SCREEN_HEIGHT - 64),
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
                x = 300 + 40 * (len(self.toys) % 5)
                self.toys.append(Ball(item=item, pos=(x, 350)))


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
        screen.blit(self.bg, (0,0))
        self.game.pet.draw(screen, self.pet_anchor)  
        
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

        self.pet_anchor = (360, 360)

        self.bg = pygame.image.load("assets/bathroom.png").convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.shower_img = pygame.image.load("assets/shower_head.png").convert_alpha()
        self.shower_img = pygame.transform.scale(self.shower_img, (120, 120))

        # --- centered shower head ---
        cx = SCREEN_WIDTH // 2
        self.head_rect = pygame.Rect(0, 0, 40, 26)      # shower head
        self.head_rect.center = (cx - 68, 100)

        # droplet spawn origin (center-bottom of head)
        self.nozzle_center = (cx - 10, self.head_rect.bottom)

        # --- Shower button (toggle ON/OFF) ---
        self.spraying = False
        self.shower_btn = pygame.Rect(37, 170, 110, 36)

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
        screen.blit(self.bg, (0,0))
        
        self._draw_shower_button(screen)

        # pet
        self.game.pet.draw(screen, self.pet_anchor)

        # shower head
        screen.blit(self.shower_img, self.head_rect)

        # droplets
        self._draw_droplets(screen)

        # UI
        self._draw_title_right("Bathroom")
        self._draw_hint_right("Toggle the Shower button to spray")
        self.draw_bar(40, 40, 200, 20, self.game.pet.hunger, "Hunger", (255, 100, 100))
        self.draw_bar(40, 100, 200, 20, self.game.pet.happiness, "Happiness", (100, 180, 255))
        self._draw_coin_hud()


    # ---------- droplets ----------
    def _spawn_droplet(self):
        import random
        x = self.nozzle_center[0] + random.uniform(-10, 10)
        y = self.nozzle_center[1] + random.uniform(-3, 3)
        vy = random.uniform(300, 380)
        self.droplets.append({"x": x, "y": y, "vy": vy})

    def _update_droplets(self, dt: float):
        # get the pet rect for collision (use same anchor as draw)
        pet_rect = self.game.pet.get_rect(center=self.pet_anchor)
        pet_rect.y += 30

        alive = []
        for d in self.droplets:
            d["y"] += d["vy"] * dt

            pos = (d["x"], d["y"])

            # if droplet hits pet, "remove" it by NOT appending
            if pet_rect.collidepoint(pos):
                continue

            # if still on-screen, keep it
            if d["y"] < SCREEN_HEIGHT + 160:
                alive.append(d)

        self.droplets = alive


    # ---------- draw pieces ----------
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

        self.bg = pygame.image.load("assets/shopping.png").convert_alpha()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # grid layout
        self.card_w, self.card_h = 160, 78
        self.pad = 14
        self.origin = (20, 280)
        self.cols = 4

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

        self.ITEM_ICONS = {
            "apple" : self._load_icon('apple'),
            "berry": self._load_icon("strawberry"),
            "cookie" : self._load_icon('cookie'),
            "pizza" : self._load_icon('pizza'),
            "ball" : self._load_icon('ball')
        }

    def _load_icon(self, name, scale=(36,36)):
            img = pygame.image.load(f"assets/{name}.png").convert_alpha()
            img = pygame.transform.scale(img, scale)
            return img
    
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

        screen.blit(self.bg, (0,0))

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
        y = self.origin[1] - 12
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

            # icon
            icon = self.ITEM_ICONS.get(item.name.lower())
            if icon:
                self.screen.blit(icon, (card_rect.x + 6, card_rect.y + 6))
            else:
                pygame.draw.rect(self.screen, item.color, (card_rect.x+8, card_rect.y+8, 20, 20), border_radius=4)

            # name / price / stock
            name_lbl  = self.font.render(item.name, True, (30,40,70))
            price_lbl = self.small_font.render(f"${item.price}", True, (40,60,90))
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

        # background
        self.bg = pygame.image.load("assets/title.png").convert()
        self.bg = pygame.transform.scale(self.bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # button
        self.btn = pygame.Rect(0, 0, 180, 55)
        self.btn.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

        # colors
        self.btn_normal = (246, 232, 177)   # cream
        self.btn_hover  = (249, 243, 210)   # lighter cream
        self.btn_border = (107, 93, 71)
        self.text_col   = (50, 40, 30)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.btn.collidepoint(event.pos):
                self.game.change_scene("living")
                self.game.time_scale = 1.0
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.game.change_scene("living")
            self.game.time_scale = 1.0

    def draw(self, screen):
        screen.blit(self.bg, (0, 0))

        # button hover check
        mx, my = pygame.mouse.get_pos()
        hovered = self.btn.collidepoint((mx, my))
        color = self.btn_hover if hovered else self.btn_normal

        # draw button
        pygame.draw.rect(screen, color, self.btn, border_radius=12)
        pygame.draw.rect(screen, self.btn_border, self.btn, 2, border_radius=12)

        # text
        if self.game.continued == 0:
            lbl = self.font.render("Start", True, self.text_col)
            screen.blit(lbl, lbl.get_rect(center=self.btn.center))
        else:
            lbl = self.font.render("Continue", True, self.text_col)
            screen.blit(lbl, lbl.get_rect(center=self.btn.center))

