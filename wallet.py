class Wallet:
    def __init__(self, start_coins=10, income_every=5.0, income_amount=1):
        self.coins = start_coins
        self.income_every = income_every
        self.income_amount = income_amount
        self.timer = 0.0

    def can_afford(self, price):
        return self.coins >= price
    
    def spend(self, price):
        if self.coins >= price:
            self.coins -= price
            return True
        return False
    
    def add(self, amount):
        self.coins += amount

    def update(self, dt):
        self.timer += dt
        while self.timer >= self.income_every:
            self.timer -= self.income_every
            self.coins += self.income_amount
