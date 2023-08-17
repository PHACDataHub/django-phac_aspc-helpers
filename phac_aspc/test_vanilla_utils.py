from .vanilla import group_by, flatten

def test_group_by():
    assert group_by([1, 2, 3, 4, 5, 6], lambda x: x % 2) == {0: [2, 4, 6], 1: [1, 3, 5]}
    assert group_by( (1, 2, 3, 4, 5, 6), lambda x: x % 2) == {0: [2, 4, 6], 1: [1, 3, 5]}

def test_flatten():
    assert flatten( [ [1], [2,3], [4,5,6] ] ) == [1, 2, 3, 4, 5, 6]
    assert flatten( ( [1], [2,3], (4,5,6) ) ) == [1, 2, 3, 4, 5, 6]