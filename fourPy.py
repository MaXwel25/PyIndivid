import random

class Businessman:
    def __init__(self, name, capital, reputation):
        self.name = name
        self.capital = capital
        self.reputation = reputation 

    def invest(self, investment_amount, risk):
        success_probability = self.reputation / (risk * 10)
        success_probability = min(max(success_probability, 0), 1)
        if random.random() <= success_probability:
            profit = investment_amount * (1 - risk)
            self.capital += profit
            self._update_reputation(success=True)
            print(f"{self.name} успешно инвестировал и заработал {profit:.2f}.")
        else:
            loss = investment_amount * risk
            self.capital -= loss
            self._update_reputation(success=False)
            print(f"{self.name} потерял {loss:.2f} при инвестиции.")
    
    def make_deal(self, deal_size):
        self.capital += deal_size
        if self.capital > 1.5 * deal_size:
            self._update_reputation(success=True)
            print(f"{self.name} повысил репутацию благодаря сделке.")
    
    def divide(self, divisor):
        if divisor <= 0:
            raise ValueError("Divisor must be greater than zero.")
        self.capital /= divisor
        self.reputation /= divisor
    
    def start_business(self, company_name):
        print(f"Starting business with {company_name}")
    
    def __str__(self):
        return (f"Бизнесмен {self.name}: капитал={self.capital:.2f}, "
                f"репутация={self.reputation}")

    # методы сравнения
    def __lt__(self, other):
        if isinstance(other, Businessman):
            return self.capital < other.capital
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Businessman):
            return (self.name == other.name and
                    self.capital == other.capital and
                    self.reputation == other.reputation)
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Businessman):
            return self.capital > other.capital
        return NotImplemented

    def _update_reputation(self, success):
        if success:
            self.reputation = min(self.reputation + 1, 100)
        else:
            self.reputation = max(self.reputation - 1, 1)

class Oligarch(Businessman):
    def __init__(self, name, capital, reputation, influence):
        super().__init__(name, capital, reputation)
        self.influence = influence 
    
    def lobby_law(self, chance_of_success):
        success_chance = min(max(chance_of_success * self.influence / 100, 0), 1)
        if random.random() <= success_chance:
            profit = self.capital * 0.1  # тут 10%
            self.capital += profit
            print(f"{self.name} успешно пролоббировал закон и заработал {profit:.2f}.")
        else:
            print(f"{self.name} потерпел неудачу при лоббировании закона.")
    
    def __str__(self):
        parent_str = super().__str__()
        return f"{parent_str}, влияние={self.influence}"

if __name__ == "__main__":
    bm = Businessman("Иван", 10000, 70)
    print(bm)
    bm.start_business("TechStart")
    bm.invest(2000, 0.2)
    print(bm)
    bm.make_deal(5000)
    print(bm)
    bm.divide(2)
    print(bm)

    olig = Oligarch("Петр", 50000, 80, 90)
    print(olig)
    olig.lobby_law(0.8)
    print(olig)

    print(bm < olig)
