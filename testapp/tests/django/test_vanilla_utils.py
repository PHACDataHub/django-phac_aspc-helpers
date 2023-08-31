from phac_aspc.vanilla import group_by, flatten, classproperty


def test_group_by():
    assert group_by([1, 2, 3, 4, 5, 6], lambda x: x % 2) == {0: [2, 4, 6], 1: [1, 3, 5]}
    assert group_by((1, 2, 3, 4, 5, 6), lambda x: x % 2) == {0: [2, 4, 6], 1: [1, 3, 5]}


def test_flatten():
    assert flatten([[1], [2, 3], [4, 5, 6]]) == [1, 2, 3, 4, 5, 6]
    assert flatten(([1], [2, 3], (4, 5, 6))) == [1, 2, 3, 4, 5, 6]


def test_class_property():
    class MyClass:
        @classproperty
        def my_class_property(cls):  # pylint: disable=no-self-argument
            return 1

    class MyChildClass:
        @classproperty
        def my_class_property(cls):  # pylint: disable=no-self-argument
            return 2

    # pylint: disable=comparison-with-callable
    assert MyClass.my_class_property == 1
    # pylint: disable=comparison-with-callable
    assert MyChildClass.my_class_property == 2
