# inventory.py
from dataclasses import dataclass

@dataclass
class ItemDef:
    name: str
    nutrition: float   # how much hunger to restore (0..1)
    color: tuple       # used for the slot swatch
    price: int

APPLE  = ItemDef("Apple",  0.20, (250,120,120), 1)
COOKIE = ItemDef("Cookie", 0.12, (230,190,120), 2)
PIZZA  = ItemDef("Pizza", 0.3,   (255,180,180), 3)

ITEMS = [APPLE, COOKIE, PIZZA]  # order in the hotbar 

class Inventory:
    def __init__(self):
        # starting amounts (tweak as you like)
        self.counts = {APPLE.name: 3, 
                       COOKIE.name: 5,
                       PIZZA.name: 2}

    def count(self, item: ItemDef) -> int:
        return self.counts.get(item.name, 0)

    def can_take(self, item: ItemDef) -> bool:
        return self.count(item) > 0

    def consume(self, item: ItemDef) -> bool:
        """Use 1 of the item. Returns True if success."""
        c = self.count(item)
        if self.can_take(item):
            self.counts[item.name] = c - 1
            return True
        return False
    def give(self, item: ItemDef, n):
        self.counts[item.name] = self.count(item) + n
