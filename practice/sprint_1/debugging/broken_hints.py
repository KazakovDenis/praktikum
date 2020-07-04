from itertools import takewhile
from typing import Optional, List, Any


MatrixType = List[List[Optional[object]]]


class Matrix:
    """
    Код нашего коллеги аналитика
    Очень медленный и тяжелый для восприятия. Ваша задача сделать его быстрее и проще для понимания.
    """

    def __init__(self):
        self.matrix = [[None]]

    @property
    def size(self) -> int:
        return len(self.matrix)

    def _scale_down(self) -> MatrixType:
        """Уменьшает размер матрицы"""
        tmp = map(
            lambda row: row[:-1], self.matrix[:-1]
        )
        self.matrix = list(tmp)
        return self.matrix

    def _scale_up(self) -> MatrixType:
        """Увеличивает размер матрицы"""
        tmp = self.matrix.copy()
        tmp.append([None] * self.size)

        for row in tmp:
            row.append(None)

        self.matrix = tmp
        return self.matrix

    def matrix_scale(self, scale_up: bool) -> MatrixType:
        """
        Функция отвечает за создание увеличенной или уменьшенной матрицы.
        Режим работы зависит от параметра scale_up. На выходе получаем расширенную матрицу.
        :param scale_up: если True, то увеличиваем матрицу, иначе уменьшаем
        :return: измененная матрица
        """
        if scale_up:
            return self._scale_up()

        # проверяем, что значения в последних строках / столбцах is None
        if not (
            any(self.matrix[-1]) and
            any(map(lambda row: row[-1], self.matrix))
        ):
            return self._scale_down()
        else:
            raise ValueError('Невозможно уменьшить размер матрицы, есть непустые элементы')

    def find_first_none_position(self) -> (int, int):
        """
        Находим позицию в матрице первого None элемента. По сути он обозначает конец данных матрицы.
        """
        for row_number, row in enumerate(self.matrix):
            try:
                return row_number, row.index(None)
            except ValueError:
                continue

        return 0, 0

    def find_last_not_none_position(self) -> (int, int):
        """
        Находим позицию последнего не None элемента матрицы.
        """
        row_number = self.size - 1

        for row in self.matrix[::-1]:
            not_none = list(takewhile(lambda x: x is None, row[::-1]))

            if not_none != row:
                col_number = len(row) - len(not_none) - 1
                return row_number, col_number

            row_number -= 1

        return 0, 0

    def add_item(self, element: Optional = None):
        """
        Добавляем новый элемент в матрицу.
        Если элемент не умещается в (size - 1) ** 2, то расширить матрицу.
        """
        if element is None:
            return

        row, col = self.find_first_none_position()

        if row * self.size + col >= (self.size - 1) ** 2:
            self.matrix_scale(scale_up=True)
            row, col = self.find_first_none_position()

        self.matrix[row][col] = element

    def pop(self) -> Any:
        """
        Удалить последний значащий элемент из массива.
        Если значащих элементов меньше (size - 1) * (size - 2) уменьшить матрицу.
        """
        if self.size == 1:
            raise IndexError('Достигнут минимальный размер матрицы')

        row, col = self.find_last_not_none_position()

        value = self.matrix[row][col]
        self.matrix[row][col] = None

        try:
            self.matrix_scale(scale_up=False)
        except ValueError as msg:
            print(msg)

        return value

    def __repr__(self):
        """
        Метод должен выводить матрицу в виде:
        1 2 3\nNone None None\nNone None None
        То есть между элементами строки должны быть пробелы, а строки отделены \n
        """
        result = map(lambda row: ' '.join(map(str, row)), self.matrix)
        return '\n'.join(result)


if __name__ == '__main__':
    pass
