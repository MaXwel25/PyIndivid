import random


def validate_params(func):
    def check(self, *args, **kwargs):
        if self.capital <= 0:
            raise ValueError(
                f"Капитал не может быть отрицательным или нулевым: {self.capital}"
            )

        if self.reputation <= 0 or self.reputation > 100:
            raise ValueError(
                f"Репутация должна быть в диапазоне 1-100: {self.reputation}"
            )

        if func.__name__ == "invest":
            investment_amount, risk = args
            if investment_amount <= 0:
                raise ValueError("Сумма инвестиции должна быть положительной")
            if risk <= 0 or risk >= 1:
                raise ValueError("Риск должен быть в диапазоне 0-1")
            if investment_amount > self.capital:
                raise ValueError("Недостаточно средств для инвестиции")

        elif func.__name__ == "divide":
            divisor = args[0]
            if divisor <= 0:
                raise ValueError("Делитель должен быть положительным числом")

        elif func.__name__ == "lobby_law":
            chance_of_success = args[0]
            if chance_of_success < 0 or chance_of_success > 1:
                raise ValueError("Шанс успеха должен быть в диапазоне 0-1")

        return func(self, *args, **kwargs)

    return check


class Businessman:
    def __init__(self, name, capital, reputation):
        self.name = name
        self.capital = capital
        self.reputation = reputation

    @validate_params
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

    @validate_params
    def divide(self, divisor):
        self.capital /= divisor
        self.reputation /= divisor

    def start_business(self, company_name):
        print(f"Starting business with {company_name}")

    def __str__(self):
        return (
            f"Бизнесмен {self.name}: капитал={self.capital:.2f}, "
            f"репутация={self.reputation}"
        )

    # методы сравнения
    def __lt__(self, other):
        if isinstance(other, Businessman):
            return self.capital < other.capital
        return NotImplemented

    def __eq__(self, other):
        if isinstance(other, Businessman):
            return (
                self.name == other.name
                and self.capital == other.capital
                and self.reputation == other.reputation
            )
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

    @validate_params
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


bm = Businessman("Инокентий", 10000, 80)
print(bm)
bm.start_business("S7airlines")
bm.invest(2000, 0.2)
print(bm)
bm.make_deal(5000)
print(bm)
bm.divide(2)
print(bm)

olig = Oligarch("Петр", 50000, 70, 100)
print(olig)
olig.lobby_law(0.8)
print(bm < olig)
