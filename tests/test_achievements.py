import ast
from pathlib import Path

import achievements


def test_achievement_unlocks_only_once():
    item = achievements.Achievement("test_achievement", "Test", "Earn 3 donuts", 3)

    assert item.check_unlock(1) is False
    assert item.check_unlock(3) is True
    assert item.check_unlock(100) is False
    assert item.unlocked is True


def test_main_load_game_restores_saved_achievement_state():
    source = Path("Main.py").read_text(encoding="utf-8")
    tree = ast.parse(source)

    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "load_game":
            body = ast.get_source_segment(source, node)
            assert "achievements.load_achievements(achievement_data)" in body
            break
    else:
        raise AssertionError("load_game() does not restore saved achievement state")
