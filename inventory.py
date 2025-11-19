# inventory.py
from dataclasses import dataclass
import pygame

@dataclass
class ItemDef:
    name: str
    nutrition: float   # how much hunger to restore (0..1)
    color: tuple       # used for the slot swatch
    price: int         # price for each item
    kind: str = "food" # Can either be food or toy

APPLE  = ItemDef("Apple",  nutrition=0.20, color=(250,120,120), price=3, kind='food')
COOKIE = ItemDef("Cookie", nutrition=0.12, color=(230,190,120), price=2, kind='food')
PIZZA  = ItemDef("Pizza", nutrition=0.3, color=(255,180,180), price=5, kind='food')
BALL   = ItemDef("Ball", nutrition=0.0, color=(255,120,120), price=5, kind='toy')

ITEMS = [APPLE, COOKIE, PIZZA, BALL]  # order in the hotbar

class Inventory:
    def __init__(self):
        # starting amounts (tweak as you like)
        self.counts = {
                       APPLE.name: 3, 
                       COOKIE.name: 5,
                       PIZZA.name: 2,
                       BALL.name: 2}
        
    def count(self, item):
        return self.counts.get(item.name, 0)

    def can_take(self, item: ItemDef) -> bool:
        return self.count(item) > 0

    def consume(self, item: ItemDef) -> bool:
        """Use 1 of the item. Returns True if success."""
        c = self.count(item) # 3
        if self.can_take(item): # True
            self.counts[item.name] = c - 1 # 3 - 1
            return True
        return False
    
    def give(self, item, n = 1):
        self.counts[item.name] = self.count(item) + n

    def clear(self):
        self.counts.clear()


