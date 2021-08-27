from tower_defense.constants import *


def hasAllUnlocked(info) -> bool:
    """Returns True if all maps in info.PBs are unlocked. Returns False otherwise."""
    for score in info.PBs.values():
        if score is None or score == LOCKED:
            return False

    return True


def updateDict(d: dict, l: list) -> dict:
    """Re-order the items in d based on the items in l and deletes redundant items."""

    newDict = {}
    oldDict = d.copy()

    keys = list(oldDict.keys())
    values = list(oldDict.values())

    for item in l:
        try:
            index = keys.index(item)
            newDict[keys[index]] = values[index]
        except ValueError:
            continue

    return newDict
