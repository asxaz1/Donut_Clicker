from typing import Dict, List, Optional


ITEMS_TEXTURES = {
    "classic_donut": None,
    "chocolate_donut": None,
    "strawberry_donut": None,
    "sprinkles_donut": None,
}


class Item:
    def __init__(self, id: str, name: str, cost: int, description: str = "", unlocked=False):
        self.id: str = id
        self.name: str = name
        self.cost: int = cost
        self.description: str = description
        self.unlocked: bool = unlocked
        self.icon = None

    def buy(self, do_bucks: int) -> tuple[bool, int]:
        if do_bucks >= self.cost:
            do_bucks -= self.cost
            self.unlocked = True
            return True, do_bucks
        return False, do_bucks


ITEMS = {
    "classic_donut": Item(
        id="classic_donut",
        name="Classic Donut",
        cost=0,
        description="Your first donut!",
        unlocked=True,
    ),
    "chocolate_donut": Item(
        id="chocolate_donut",
        name="Chocolate Donut",
        cost=10,
        description="A delicious chocolate treat",
        unlocked=False,
    ),
    "strawberry_donut": Item(
        id="strawberry_donut",
        name="Strawberry Donut",
        cost=25,
        description="Sweet strawberry flavor",
        unlocked=False,
    ),
    "sprinkles_donut": Item(
        id="sprinkles_donut",
        name="Sprinkles Donut",
        cost=50,
        description="Colorful sprinkles on top",
        unlocked=False,
    ),
}


def load_icon(self, load_icon_func):
    if self.id in ITEMS_TEXTURES:
        self.icon = load_icon_func(ITEMS_TEXTURES[self.id])


__all__ = [
    "Item",
    "ITEMS",
    "ITEMS_TEXTURES",
    "load_icon",
]

class Item:
    def __init__(self, id: str, name: str, cost: int, description: str = "", unlocked=False):
        self.id: str = id
        self.name: str = name
        self.cost: int = cost
        self.description: str = description
        self.unlocked: bool = unlocked
        self.icon = None

    def buy(self, do_bucks: int) -> tuple[bool, int]:
        if do_bucks >= self.cost:
            do_bucks -= self.cost
            self.unlocked = True
            return True, do_bucks
        return False, do_bucks


ITEMS = {
    "classic_donut": Item(
        id="classic_donut",
        name="Classic Donut",
        cost=0,
        description="Your first donut!",
        unlocked=True,
    ),
    "chocolate_donut": Item(
        id="chocolate_donut",
        name="Chocolate Donut",
        cost=10,
        description="A delicious chocolate treat",
        unlocked=False,
    ),
    "strawberry_donut": Item(
        id="strawberry_donut",
        name="Strawberry Donut",
        cost=25,
        description="Sweet strawberry flavor",
        unlocked=False,
    ),
    "sprinkles_donut": Item(
        id="sprinkles_donut",
        name="Sprinkles Donut",
        cost=50,
        description="Colorful sprinkles on top",
        unlocked=False,
    ),
}


def load_icon(self, load_icon_func):
    if self.id in ITEMS_TEXTURES:
        self.icon = load_icon_func(ITEMS_TEXTURES[self.id])



__all__ = [
    "Item",
    "ITEMS",
    "ITEMS_TEXTURES",
    "load_icon",
]