# ============================================
# UPGRADES.PY - Moduł ulepszeń
# Donut Clicker Alpha 0.1.2
# ============================================
"""Upgrades module.

Provides building and upgrade definitions, classes, and helper
functions to manage buildings, upgrades, and their state.
"""

from typing import Dict, Optional

# ============================================
# ŚCIEŻKI DO TEKSTUR BUDYNKÓW (100x100px)
# ============================================
BUILDING_TEXTURES = {
    "eater": None,              # Ścieżka do ikony Eater
    "eater_premium": None,      # Ścieżka do ikony Eater Premium
    "donut_house": None,        # Ścieżka do ikony Donut House
    "donut_eating_hall": None   # Ścieżka do ikony Donut Eating Hall
}

# ============================================
# ŚCIEŻKI DO TEKSTUR ULEPSZEŃ (100x100px)
# ============================================
UPGRADE_TEXTURES = {
    "eating_power": None,   # Ścieżka do ikony Eating Power
    "store": None,          # Ścieżka do ikony Store
    "gastro_pill": None     # Ścieżka do ikony Gastro Pill
}


class Building:
    """Klasa reprezentująca budynek generujący pączki"""
    def __init__(self, id, name, base_cost, dps, max_count, cost_multiplier=1.05):
        self.id = id
        self.name = name
        self.base_cost = base_cost
        self.dps = dps
        self.max_count = max_count
        self.cost_multiplier = cost_multiplier
        self.count = 0
    
    def get_cost(self):
        """Oblicza koszt następnego budynku"""
        cost = int(self.base_cost * (self.cost_multiplier ** self.count))
        # Redukcja kosztu dla Eater (specjalna formuła)
        if self.id == "eater" and cost > 500:
            return int(500 + (cost - 500) * 0.25)
        return cost
    
    def can_buy(self, points):
        """Sprawdza czy można kupić następny budynek"""
        return self.count < self.max_count and points >= self.get_cost()
    
    def buy(self, points):
        """Kupuje budynek jeśli możliwe"""
        if self.can_buy(points):
            cost = self.get_cost()
            self.count += 1
            return cost
        return 0
    
    def get_total_dps(self):
        """Zwraca całkowity DPS z tego budynku"""
        return self.count * self.dps


class Upgrade:
    """Klasa reprezentująca ulepszenie"""
    def __init__(self, id, name, description, cost, max_level=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.max_level = max_level
        self.level = 0
        self.unlocked = False
    
    def get_cost(self):
        """Oblicza koszt następnego poziomu"""
        if self.max_level is None:
            # Nieskończone poziomy (jak Eating Power)
            return int(self.cost * (1.08 ** self.level))
        else:
            # Jednorazowe ulepszenie
            return self.cost
    
    def can_buy(self, points):
        """Sprawdza czy można kupić ulepszenie"""
        if self.max_level is not None and self.unlocked:
            return False
        return points >= self.get_cost()
    
    def buy(self, points):
        """Kupuje ulepszenie jeśli możliwe"""
        if self.can_buy(points):
            cost = self.get_cost()
            self.level += 1
            if self.max_level == 1:
                self.unlocked = True
            return cost
        return 0


# ============================================
# DEFINICJE BUDYNKÓW
# ============================================

BUILDINGS = {
    "eater": Building(
        id="eater",
        name="Eater",
        base_cost=100,
        dps=0.5,
        max_count=10,
        cost_multiplier=1.05
    ),
    "eater_premium": Building(
        id="eater_premium",
        name="Eater Premium",
        base_cost=1000,
        dps=2.5,
        max_count=10,
        cost_multiplier=1.08
    ),
    "donut_house": Building(
        id="donut_house",
        name="Donut House",
        base_cost=10000,
        dps=5.0,
        max_count=10,
        cost_multiplier=1.1
    ),
    "donut_eating_hall": Building(
        id="donut_eating_hall",
        name="Donut Eating Hall",
        base_cost=100000,
        dps=10.0,
        max_count=25,
        cost_multiplier=1.12
    )
}


# ============================================
# DEFINICJE ULEPSZEŃ
# ============================================

UPGRADES = {
    "eating_power": Upgrade(
        id="eating_power",
        name="Eating Power",
        description="Zwiększa siłę kliknięcia o 1",
        cost=50,
        max_level=None  # Nieskończone poziomy
    ),
    "store": Upgrade(
        id="store",
        name="Store",
        description="Odblokuj sklep z nowymi budynkami",
        cost=500,
        max_level=1  # Jednorazowe
    ),
    "gastro_pill": Upgrade(
        id="gastro_pill",
        name="Gastro Pill",
        description="Zwiększa pojemność żołądka (odblokowuje nowe budynki)",
        cost=1000,
        max_level=1  # Jednorazowe
    )
}


# ============================================
# FUNKCJE POMOCNICZE
# ============================================

def get_clicks_per_click(eating_power_level):
    """Oblicza siłę kliknięcia na podstawie poziomu Eating Power"""
    return 1 + eating_power_level


def get_total_dps(buildings):
    """Oblicza całkowity DPS ze wszystkich budynków"""
    total = 0
    for building in buildings.values():
        total += building.get_total_dps()
    return total


def save_buildings(buildings):
    """Przygotowuje dane budynków do zapisu JSON"""
    return {
        building_id: building.count
        for building_id, building in buildings.items()
    }


def load_buildings(data):
    """Wczytuje dane budynków z JSON"""
    for building_id, count in data.items():
        if building_id in BUILDINGS:
            BUILDINGS[building_id].count = count


def save_upgrades(upgrades):
    """Przygotowuje dane ulepszeń do zapisu JSON"""
    return {
        upgrade_id: {
            "level": upgrade.level,
            "unlocked": upgrade.unlocked
        }
        for upgrade_id, upgrade in upgrades.items()
    }


def load_upgrades(data):
    """Wczytuje dane ulepszeń z JSON"""
    for upgrade_id, upgrade_data in data.items():
        if upgrade_id in UPGRADES:
            UPGRADES[upgrade_id].level = upgrade_data.get("level", 0)
            UPGRADES[upgrade_id].unlocked = upgrade_data.get("unlocked", False)


# ============================================
# ŁADOWANIE TEKSTUR
# ============================================

def load_textures(load_icon_func) -> Dict[str, Optional[object]]:
    """
    Ładuje wszystkie tekstury budynków i ulepszeń.
    
    Args:
        load_icon_func: Funkcja do ładowania ikon (np. load_upgrade_icon z głównego pliku)
    
    Returns:
        dict: Słownik {id: załadowana_ikona}
    """
    loaded: Dict[str, Optional[object]] = {}
    
    # Ładuj tekstury budynków
    for building_id, path in BUILDING_TEXTURES.items():
        try:
            loaded[building_id] = load_icon_func(path)
        except Exception:
            loaded[building_id] = None
    
    # Ładuj tekstury ulepszeń
    for upgrade_id, path in UPGRADE_TEXTURES.items():
        try:
            loaded[upgrade_id] = load_icon_func(path)
        except Exception:
            loaded[upgrade_id] = None
    
    return loaded


def get_building_icon(loaded_textures, building_id):
    """Zwraca ikonę budynku lub None"""
    return loaded_textures.get(building_id)


def get_upgrade_icon(loaded_textures, upgrade_id):
    """Zwraca ikonę ulepszenia lub None"""
    return loaded_textures.get(upgrade_id)


__all__ = [
    "Building",
    "Upgrade",
    "BUILDINGS",
    "UPGRADES",
    "BUILDING_TEXTURES",
    "UPGRADE_TEXTURES",
    "get_total_dps",
    "save_buildings",
    "load_buildings",
    "save_upgrades",
    "load_upgrades",
    "load_textures",
    "get_building_icon",
    "get_upgrade_icon",
    "get_clicks_per_click",
]