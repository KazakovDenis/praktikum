from math import ceil, sqrt
from pytest import fixture, main, mark, param, raises
from practice.sprint_1.debugging.broken_hints import Matrix


TYPES = 1, 1.0, 'string', {}, set(), bytes(), bytearray()
PARAMS = (param(item, id=type(item).__name__) for item in TYPES)


@fixture
def matrix():
    return Matrix()


@mark.parametrize('item', PARAMS)
def test_add_item_positive(matrix, item):
    matrix.add_item(item)
    assert str(matrix) == f'{item} None\nNone None'


def test_add_item_negative(matrix):
    with raises(ValueError):
        matrix.add_item(None)


@mark.parametrize('item', PARAMS)
def test_pop_positive(matrix, item):
    matrix.add_item(item)
    assert matrix.pop() == item


def test_pop_negative(matrix):
    with raises(IndexError):
        matrix.pop()


@mark.parametrize('size', (i ** 4 for i in range(10)))
def test_size(matrix, size):
    for i in range(size):
        matrix.add_item(1)
    assert matrix.size == ceil(sqrt(size) + 1)


if __name__ == '__main__':
    main()
