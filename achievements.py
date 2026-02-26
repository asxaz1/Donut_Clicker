# ============================================
# ACHIEVEMENTS.PY - Moduł osiągnięć
# Donut Clicker Alpha 0.1.2
# ============================================
"""Achievements module.

Provides a simple in-memory list of Achievement objects and
helper functions to check, load and save achievement state.
"""

from typing import Dict, List, Optional

# ============================================
# ŚCIEŻKI DO TEKSTUR OSIĄGNIĘĆ (100x100px)
# ============================================
ACHIEVEMENT_TEXTURES = {
    "first_donut": None,         # Ścieżka do ikony First Donut
    "donut_collector": None,     # Ścieżka do ikony Donut Collector
    "donut_hoarder": None,       # Ścieżka do ikony Donut Hoarder
    "donut_master": None,        # Ścieżka do ikony Donut Master
    "donut_legend": None,        # Ścieżka do ikony Donut Legend
    "donut_god": None,           # Ścieżka do ikony Donut God
    "donut_millionaire": None,   # Ścieżka do ikony Donut Millionaire
    "donut_billionaire": None,   # Ścieżka do ikony Donut Billionaire
    "donut_trillionaire": None   # Ścieżka do ikony Donut Trillionaire
}


class Achievement:
    """Represents a single achievement."""
    def __init__(self, id: str, name: str, description: str, requirement: int):
        self.id: str = id
        self.name: str = name
        self.description: str = description
        self.requirement: int = int(requirement)
        self.unlocked: bool = False

    def check_unlock(self, total_donuts: int) -> bool:
        """Return True if achievement was newly unlocked."""
        if not self.unlocked and int(total_donuts) >= self.requirement:
            self.unlocked = True
            return True
        return False


# ============================================
# DEFINICJE OSIĄGNIĘĆ
# ============================================

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
        description="Earn 1,000,000 total donuts",
        requirement=1000000
    ),
    Achievement(
        id="donut_millionaire",
        name="Donut Millionaire",
        description="Earn 10,000,000 total donuts",
        requirement=10000000
    ),
    Achievement(
        id="donut_billionaire",
        name="Donut Billionaire",
        description="Earn 1,000,000,000 total donuts",
        requirement=1000000000
    ),
    Achievement(
        id="donut_trillionaire",
        name="Donut Trillionaire",
        description="Earn 1,000,000,000,000 total donuts",
        requirement=1000000000000
    )
]


# ============================================
# FUNKCJE POMOCNICZE
# ============================================

def check_achievements(total_donuts: int) -> List[Achievement]:
    """Check all achievements against `total_donuts` and return newly unlocked list."""
    newly_unlocked: List[Achievement] = []
    for achievement in ACHIEVEMENTS:
        if achievement.check_unlock(total_donuts):
            newly_unlocked.append(achievement)
    return newly_unlocked


def get_unlocked_count() -> int:
    """Return number of unlocked achievements."""
    return sum(1 for achievement in ACHIEVEMENTS if achievement.unlocked)


def save_achievements() -> Dict[str, bool]:
    """Return a JSON-serializable mapping of achievement_id -> unlocked."""
    return {achievement.id: achievement.unlocked for achievement in ACHIEVEMENTS}


def load_achievements(data: Dict[str, bool]) -> None:
    """Load achievement unlocked flags from a mapping {id: bool}."""
    for achievement in ACHIEVEMENTS:
        if achievement.id in data:
            achievement.unlocked = bool(data[achievement.id])


# ============================================
# ŁADOWANIE TEKSTUR
# ============================================

def load_textures(load_icon_func) -> Dict[str, Optional[object]]:
    """
    Ładuje wszystkie tekstury osiągnięć.
    
    Args:
        load_icon_func: Funkcja do ładowania ikon (np. load_upgrade_icon z głównego pliku)
    
    Returns:
        dict: Słownik {achievement_id: załadowana_ikona}
    """
    loaded: Dict[str, Optional[object]] = {}
    for achievement_id, path in ACHIEVEMENT_TEXTURES.items():
        try:
            loaded[achievement_id] = load_icon_func(path)
        except Exception:
            loaded[achievement_id] = None
    return loaded


def get_achievement_icon(loaded_textures, achievement_id):
    """Zwraca ikonę osiągnięcia lub None"""
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