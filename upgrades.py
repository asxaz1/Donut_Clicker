from typing import Dict, Optional

BUILDING_TEXTURES = {
    "eater": None,
    "eater_premium": None,
    "donut_house": None,
    "donut_eating_hall": None,
    "donut_co": None
}

UPGRADE_TEXTURES = {
    "eating_power": None,
    "store": None,
    "gastro_pill": None
}


class Building:
    def __init__(self, id, name, base_cost, dps, max_count, cost_multiplier=1.05):
        self.id = id
        self.name = name
        self.base_cost = base_cost
        self.dps = dps
        self.max_count = max_count
        self.cost_multiplier = cost_multiplier
        self.count = 0

    def get_cost(self):
        cost = int(self.base_cost * (self.cost_multiplier ** self.count))
        if self.id == "eater" and cost > 500:
            return int(500 + (cost - 500) * 0.25)
        return cost

    def can_buy(self, points):
        return self.count < self.max_count and points >= self.get_cost()

    def buy(self, points):
        if self.can_buy(points):
            cost = self.get_cost()
            self.count += 1
            return cost
        return 0

    def get_total_dps(self):
        return self.count * self.dps


class Upgrade:
    def __init__(self, id, name, description, cost, max_level=None):
        self.id = id
        self.name = name
        self.description = description
        self.cost = cost
        self.max_level = max_level
        self.level = 0
        self.unlocked = False

    def get_cost(self):
        if self.max_level is None:
            return int(self.cost * (1.08 ** self.level))
        else:
            return self.cost

    def can_buy(self, points):
        if self.max_level is not None and self.unlocked:
            return False
        return points >= self.get_cost()

    def buy(self, points):
        if self.can_buy(points):
            cost = self.get_cost()
            self.level += 1
            if self.max_level == 1:
                self.unlocked = True
            return cost
        return 0


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
    ),
    "donut_co": Building(
        id="donut_co",
        name="Donut Corporation",
        base_cost=1000000,
        dps=100.0,
        max_count=10,
        cost_multiplier=1.08
    )
}


UPGRADES = {
    "eating_power": Upgrade(
        id="eating_power",
        name="Eating Power",
        description="Zwięksa siłę kliknięcia o 1",
        cost=50,
        max_level=None
    ),
    "store": Upgrade(
        id="store",
        name="Store",
        description="Odblokuj sklep z nowymi budynkami",
        cost=500,
        max_level=1
    ),
    "gastro_pill": Upgrade(
        id="gastro_pill",
        name="Gastro Pill",
        description="Zwiększa pojemność żołądka (odblokowuje nowe budynki)",
        cost=1000,
        max_level=1
    )
}


def get_clicks_per_click(eating_power_level):
    return 1 + eating_power_level


def get_total_dps(buildings):
    total = 0
    for building in buildings.values():
        total += building.get_total_dps()
    return total


def save_buildings(buildings):
    return {
        building_id: building.count
        for building_id, building in buildings.items()
    }


def load_buildings(data):
    for building_id, count in data.items():
        if building_id in BUILDINGS:
            BUILDINGS[building_id].count = count


def save_upgrades(upgrades):
    return {
        upgrade_id: {
            "level": upgrade.level,
            "unlocked": upgrade.unlocked
        }
        for upgrade_id, upgrade in upgrades.items()
    }


def load_upgrades(data):
    for upgrade_id, upgrade_data in data.items():
        if upgrade_id in UPGRADES:
            UPGRADES[upgrade_id].level = upgrade_data.get("level", 0)
            UPGRADES[upgrade_id].unlocked = upgrade_data.get("unlocked", False)


def load_textures(load_icon_func) -> Dict[str, Optional[object]]:
    loaded: Dict[str, Optional[object]] = {}

    for building_id, path in BUILDING_TEXTURES.items():
        try:
            loaded[building_id] = load_icon_func(path)
        except Exception:
            loaded[building_id] = None

    for upgrade_id, path in UPGRADE_TEXTURES.items():
        try:
            loaded[upgrade_id] = load_icon_func(path)
        except Exception:
            loaded[upgrade_id] = None

    return loaded


def get_building_icon(loaded_textures, building_id):
    return loaded_textures.get(building_id)


def get_upgrade_icon(loaded_textures, upgrade_id):
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