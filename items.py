#====================================
# Itmems.py - moduł z klasami przedmiotów
#====================================

ITEMS_TEXTURES = {
    "classic_donut": None,
}

class Item:
    def __init__(self, id: str, name: str, cost: int, unlocked=False):
        self.id: str = id
        self.name: str = name
        self.cost: int = cost
        self.unlocked: bool = unlocked
        self.icon = None  # Załadowana ikona (obiekt Pygame)
    
    def buy(self):
        global dobucks
        if dobucks >= self.cost:
            dobucks -= self.cost
            self.unlocked = True
            return True
        return False
    

#==========================
# Definicje przedmiotów
#==========================

ITEMS = {
    "classic_donut":Item(
        id="classic_donut",
        name="Classic Donut",
        cost=0,
        unlocked=True,
    ),
}

#============================
# FUNKCJE POMOCNICZE
#============================


def load_icon(self, load_icon_func):
    """Ładuje ikonę przedmiotu za pomocą podanej funkcji."""
    if self.id in ITEMS_TEXTURES:
        self.icon = load_icon_func(ITEMS_TEXTURES[self.id])



__all__ = [
    "Item",
    "ITEMS",
    "ITEMS_TEXTURES",
    "load_icon",
]