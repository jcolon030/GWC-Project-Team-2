class Wallet:
    def __init__(self, start_coins: int = 10, income_every: float = 5.0, income_amount: int = 1):
        self.coins = int(start_coins)
        self.income_every = float(income_every)
        self.income_amount = int(income_amount)
        self._timer = 0.0

    def can_afford(self, cost):
        return self.coins >= int(cost)

    def spend(self, cost):
        cost = int(cost)
        if self.coins >= cost:
            self.coins -= cost
            return True
        return False

    def add(self, amount):
        self.coins += int(amount)

    def update(self, dt):
        """Passive income every `income_every` seconds."""
        self._timer += dt
        while self._timer >= self.income_every:
            self._timer -= self.income_every
            self.coins += self.income_amount
