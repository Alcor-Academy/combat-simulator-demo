from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    name: str
    hp: int
    attack_power: int

    def __post_init__(self) -> None:
        if not self.name or self.name.strip() == "":
            raise ValueError("Name cannot be empty")
        if self.hp < 0:
            raise ValueError("HP must be non-negative")
        if self.attack_power <= 0:
            raise ValueError("Attack power must be positive")

    @property
    def agility(self) -> int:
        return self.hp + self.attack_power

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def receive_damage(self, amount: int) -> "Character":
        new_hp = max(0, self.hp - amount)  # Floor at 0
        return Character(name=self.name, hp=new_hp, attack_power=self.attack_power)
