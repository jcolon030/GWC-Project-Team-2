import pygame

class Hotbar:
    def __init__(
        self,
        inventory,
        items,
        origin=(20, 0),
        slot_w=85,
        slot_h=44,
        pad=10,
        font=None,
        small_font=None,
        screen=None,
        on_click_item=None,
        max_visible=3
    ):
        self.inv = inventory
        self.items = items
        self.origin = origin
        self.slot_w, self.slot_h = slot_w, slot_h
        self.pad = pad
        self.font = font
        self.small_font = small_font
        self.screen = screen
        self.on_click_item = on_click_item

        # paging
        self.max_visible = max_visible   # how many slots we draw at once
        self.offset = 0                  # index of first visible item

        self._slots = []   # [(Rect, ItemDef), ...] for VISIBLE slice only
        self._hover_i = None

        self.ITEM_ICONS = {
                "apple" : self._load_icon('apple'),
                "berry": self._load_icon("strawberry"),
                "cookie" : self._load_icon('cookie'),
                "pizza" : self._load_icon('pizza'),
                "ball" : self._load_icon('ball')
        }

        # arrow buttons (computed in draw, but keep rects here for clicks)
        self.left_arrow = None
        self.right_arrow = None

    # ---------- events ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._hover_i = None
            for i, (rect, _) in enumerate(self._slots):
                if rect.collidepoint((mx, my)):
                    self._hover_i = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # handle arrows first
            if self.left_arrow and self.left_arrow.collidepoint((mx, my)):
                self.offset = max(0, self.offset - 1)
                return

            if self.right_arrow and self.right_arrow.collidepoint((mx, my)):
                max_offset = max(0, len(self.items) - self.max_visible)
                self.offset = min(max_offset, self.offset + 1)
                return

            # then handle item clicks
            if self._hover_i is not None and self.on_click_item:
                _, item = self._slots[self._hover_i]
                if self.inv.count(item) > 0:
                    self.on_click_item(item)

    # ---------- draw ----------
    def draw(self):
        x0, y0 = self.origin

        # figure out which items are currently visible
        visible = self.items[self.offset:self.offset + self.max_visible]

        # background strip just around visible slots
        total_w = len(visible) * (self.slot_w + self.pad) - self.pad
        strip = pygame.Rect(x0 - 10, y0 - 8, total_w + 20, self.slot_h + 16)
        pygame.draw.rect(self.screen, (238, 240, 245), strip, border_radius=10)
        pygame.draw.rect(self.screen, (70, 90, 130), strip, width=2, border_radius=10)

        # build slots for visible slice
        self._slots = [] # (Rect, Item)
        for i, item in enumerate(visible): # visible = ITEMS; [1, Apple; 2, Banana; ]
            x = x0 + i * (self.slot_w + self.pad)
            rect = pygame.Rect(x, y0, self.slot_w, self.slot_h)
            self._slots.append((rect, item))

        # draw each visible slot
        for i, (rect, item) in enumerate(self._slots): # [1, (Rect, Apple); 2, (Rect, Banana)]
            draw_rect = rect.inflate(8, 6) if i == self._hover_i else rect
            has_any = self.inv.count(item) > 0
            base_col = (245, 245, 250) if has_any else (230, 230, 235)

            pygame.draw.rect(self.screen, base_col, draw_rect, border_radius=8)
            pygame.draw.rect(self.screen, (70, 90, 130), draw_rect, width=2, border_radius=8)

            # icon
            icon = self.ITEM_ICONS.get(item.name.lower())
            if icon:
                self.screen.blit(icon, (draw_rect.x + 6, draw_rect.y + 6))
            else:
                pygame.draw.rect(self.screen, item.color, (draw_rect.x+8, draw_rect.y+8, 20, 20), border_radius=4)

            # label
            label = self.small_font.render(item.name, True, (30, 40, 70))
            self.screen.blit(label, (draw_rect.x + 34, draw_rect.y + 6))

            # count
            cnt = self.inv.count(item)
            count_txt = self.small_font.render(f"x{cnt}", True, (30, 40, 70))
            self.screen.blit(count_txt, (draw_rect.x + 34, draw_rect.y + 22))

            # out-of-stock overlay
            if not has_any:
                overlay = pygame.Surface((draw_rect.w, draw_rect.h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 40))
                self.screen.blit(overlay, draw_rect.topleft)

        # draw arrows if needed
        self._draw_arrows()

    def _load_icon(self, name, scale=(24,24)):
                img = pygame.image.load(f"assets/{name}.png").convert_alpha()
                img = pygame.transform.scale(img, scale)
                return img

    # ---------- arrows ----------
    def _draw_arrows(self):
        x0, y0 = self.origin

        # only show arrows if we actually have more than max_visible items
        if len(self.items) <= self.max_visible:
            self.left_arrow = None
            self.right_arrow = None
            return

        # left arrow to the left of hotbar
        self.left_arrow = pygame.Rect(x0 - 33, y0 + 8, 20, 28)
        pygame.draw.rect(self.screen, (230, 230, 240), self.left_arrow, border_radius=4)
        pygame.draw.rect(self.screen, (70, 70, 90), self.left_arrow, 1, border_radius=4)
        la = self.small_font.render("<", True, (50, 50, 70))
        self.screen.blit(la, la.get_rect(center=self.left_arrow.center))

        # right arrow to the right of visible strip
        visible = self.items[self.offset:self.offset + self.max_visible]
        total_w = len(visible) * (self.slot_w + self.pad) - self.pad
        right_x = x0 + total_w + 12
        self.right_arrow = pygame.Rect(right_x, y0 + 8, 20, 28)
        pygame.draw.rect(self.screen, (230, 230, 240), self.right_arrow, border_radius=4)
        pygame.draw.rect(self.screen, (70, 70, 90), self.right_arrow, 1, border_radius=4)
        ra = self.small_font.render(">", True, (50, 50, 70))
        self.screen.blit(ra, ra.get_rect(center=self.right_arrow.center))
