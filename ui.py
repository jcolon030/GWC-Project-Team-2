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
        on_click_item = None
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

        self._slots = [] # contains tuple[pygame.Rect, ItemDef] == [(Rect, APPLE), (Rect, PIZZA), (Rect, BALL)]
        self._hover_i = None
        self._rebuild_slots()

    # ---------- events ----------
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._hover_i = None
            for i, (rect, _) in enumerate(self._slots): # 0, (Rect, APPLE)
                if rect.collidepoint((mx, my)):
                    self._hover_i = i
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._hover_i is not None and self.on_click_item:
                _, item = self._slots[self._hover_i] # self._slots = []; self._slots[0]
                if self.inv.count(item) > 0:
                    # Let caller decide what to do when clicking the item
                    self.on_click_item(item)

    # ---------- draw ----------
    def draw(self):
        x0, y0 = self.origin
        total_w = len(self.items) * (self.slot_w + self.pad) - self.pad
        strip = pygame.Rect(x0 - 10, y0 - 8, total_w + 20, self.slot_h + 16)
        pygame.draw.rect(self.screen, (238, 240, 245), strip, border_radius=10)
        pygame.draw.rect(self.screen, (70, 90, 130), strip, width=2, border_radius=10)

        for i, (rect, item) in enumerate(self._slots): # 1, (Rect, APPLE)   2, (Rect, BANANA)
            draw_rect = rect.inflate(8, 6) if i == self._hover_i else rect
            has_any = self.inv.count(item) > 0
            base_col = (245, 245, 250) if has_any else (230, 230, 235)

            pygame.draw.rect(self.screen, base_col, draw_rect, border_radius=8)
            pygame.draw.rect(self.screen, (70, 90, 130), draw_rect, width=2, border_radius=8)

            sw = pygame.Rect(draw_rect.x + 8, draw_rect.y + 8, 20, 20)
            pygame.draw.rect(self.screen, item.color, sw, border_radius=4)
            pygame.draw.rect(self.screen, (60, 60, 80), sw, width=1, border_radius=4)

            label = self.small_font.render(item.name, True, (30, 40, 70))
            self.screen.blit(label, (draw_rect.x + 34, draw_rect.y + 6))

            cnt = self.inv.count(item)
            count_txt = self.small_font.render(f"x{cnt}", True, (30, 40, 70))
            self.screen.blit(count_txt, (draw_rect.x + 34, draw_rect.y + 22))

            if not has_any:
                overlay = pygame.Surface((draw_rect.w, draw_rect.h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 40))
                self.screen.blit(overlay, draw_rect.topleft)

    # ---------- layout ----------
    def _rebuild_slots(self):
        self._slots.clear()
        x0, y0 = self.origin
        for i, item in enumerate(self.items): # 0, APPLE  1, BANANA 2, PIZZA 3, BALL
            x = x0 + i * (self.slot_w + self.pad)
            rect = pygame.Rect(x, y0, self.slot_w, self.slot_h)
            self._slots.append((rect, item))
