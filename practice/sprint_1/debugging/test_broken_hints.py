from pytest import fixture, main, mark, param, raises
from practice.sprint_1.debugging.broken_hints import Matrix


@fixture
def matrix():
    return Matrix()


@mark.parametrize(
    'item',
    [
        param(1, id='Int item'),
        param(1.0, id='Float item'),
        param('Str', id='Str item'),
        param({}, id='Dict item'),
        param(set(), id='Set item'),
        param(bytes(), id='Bytes item'),
        param(bytearray(), id='Bytearray item'),
    ]
)
def test_add_item_positive(item, matrix):
    matrix.add_item(item)
    assert str(matrix) == f'{item} None\nNone None'


@mark.parametrize(
    'item',
    [
        param(None, id='None item'),
        param(id='No item'),
    ]
)
def test_add_item_negative(item, matrix):
    with raises(ValueError):
        matrix.add_item()


if __name__ == '__main__':
    main()
