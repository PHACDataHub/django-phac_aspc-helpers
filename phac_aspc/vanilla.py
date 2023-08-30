"""
    Utilities for basic python stuff, e.g. data/string manipulation
"""
from collections import defaultdict


def group_by(iterable, key: callable):
    """
    like builtin groupby, but doesn't require sorted input
    returns a dict of lists
    """
    groups = defaultdict(list)
    for item in iterable:
        groups[key(item)].append(item)
    return groups


def flatten(iterable):
    """flattens an iterable of iterables into a single list"""
    return [item for sublist in iterable for item in sublist]


class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()
