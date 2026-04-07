from typing import Dict, List, Optional

ACHIEVEMENT_TEXTURES = {
    "first_donut": None,
    "donut_collector": None,
    "donut_hoarder": None,
    "donut_master": None,
    "donut_legend": None,
    "donut_god": None,
    "donut_millionaire": None,
    "donut_billionaire": None,
    "donut_trillionaire": None
}


class Achievement:
    def __init__(self, id: str, name: str, description: str, requirement: int):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.requirement: int = int(requirement)
        self.unlocked: bool = False

    def check_unlock(self, total_donuts: int) -> bool:
        if not self.unlocked and int(total_donuts) >= self.requirement:
            self.unlocked = True
            return True
        return False


ACHIEVEMENTS: List[Achievement] = [
    Achievement(
        id="first_donut",
        name="First Donut",
        description="Earn 1 total donut",
        requirement=1
    ),
    Achievement(
        id="donut_collector",
        name="Donut Collector",
        description="Earn 100 total donuts",
        requirement=100
    ),
    Achievement(
        id="donut_hoarder",
        name="Donut Hoarder",
        description="Earn 1,000 total donuts",
        requirement=1000
    ),
    Achievement(
        id="donut_master",
        name="Donut Master",
        description="Earn 10,000 total donuts",
        requirement=10000
    ),
    Achievement(
        id="donut_legend",
        name="Donut Legend",
        description="Earn 100,000 total donuts",
        requirement=100000
    ),
    Achievement(
        id="donut_god",
        name="Donut God",
        description="Earn 1M total donuts",
        requirement=1000000
    ),
    Achievement(
        id="donut_millionaire",
        name="Donut Millionaire",
        description="Earn 10M total donuts",
        requirement=10000000
    ),
    Achievement(
        id="donut_billionaire",
        name="Donut Billionaire",
        description="Earn 1B total donuts",
        requirement=1000000000
    ),
    Achievement(
        id="donut_trillionaire",
        name="Donut Trillionaire",
        description="Earn 1T total donuts",
        requirement=1000000000000
    )
]


def check_achievements(total_donuts: int) -> List[Achievement]:
    newly_unlocked: List[Achievement] = []
    for achievement in ACHIEVEMENTS:
        if achievement.check_unlock(total_donuts):
            newly_unlocked.append(achievement)
    return newly_unlocked


def get_unlocked_count() -> int:
    return sum(1 for achievement in ACHIEVEMENTS if achievement.unlocked)


def save_achievements() -> Dict[str, bool]:
    return {achievement.id: achievement.unlocked for achievement in ACHIEVEMENTS}


def load_achievements(data: Dict[str, bool]) -> None:
    for achievement in ACHIEVEMENTS:
        if achievement.id in data:
            achievement.unlocked = bool(data[achievement.id])


def load_textures(load_icon_func) -> Dict[str, Optional[object]]:
    loaded: Dict[str, Optional[object]] = {}
    for achievement_id, path in ACHIEVEMENT_TEXTURES.items():
        try:
            loaded[achievement_id] = load_icon_func(path)
        except Exception:
            loaded[achievement_id] = None
    return loaded


def get_achievement_icon(loaded_textures, achievement_id):
    return loaded_textures.get(achievement_id)


__all__ = [
    "Achievement",
    "ACHIEVEMENTS",
    "check_achievements",
    "get_unlocked_count",
    "save_achievements",
    "load_achievements",
    "load_textures",
    "get_achievement_icon",
]