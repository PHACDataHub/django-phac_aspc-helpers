from collections import defaultdict


def group_by(iterable, key: callable):
    groups = defaultdict(list)
    for item in iterable:
        groups[key(item)].append(item)
    return groups


def flatten(iterable):
    return [item for sublist in iterable for item in sublist]
