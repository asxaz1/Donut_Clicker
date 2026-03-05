#====================================
# Itmems.py - moduł z klasami przedmiotów
#====================================

ITEMS_TEXTURES = {
    "classic_donut": None,
}

class Item:
    def __init__(self, id: str, name: str, description: str, unlocked=False):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.unlocked: bool = unlocked
        self.icon = None  # Załadowana ikona (obiekt Pygame)

    def load_icon(self, load_icon_func):
        """Ładuje ikonę przedmiotu za pomocą podanej funkcji."""
        if self.id in ITEMS_TEXTURES:
            self.icon = load_icon_func(ITEMS_TEXTURES[self.id])
    
    