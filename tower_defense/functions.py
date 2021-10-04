import pygame

from typing import overload

from tower_defense.constants import *


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


@overload
def removeCharset(s: str, charset: List[str]) -> str: ...
@overload
def removeCharset(s: str, charset: str) -> str: ...

def removeCharset(s, charset) -> str:
    """Remove all charaters in charset from s and returns the result."""
    for char in charset:
        s = s.replace(char, '')

    return s
