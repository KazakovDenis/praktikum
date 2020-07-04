from itertools import takewhile
from typing import Optional, List


MatrixType = List[List[Optional[object]]]


class Matrix:
    """
    Код нашего коллеги аналитика
    Очень медленный и тяжелый для восприятия. Ваша задача сделать его быстрее и проще для понимания.
    """
    cell = [None]

    def __init__(self):
        self.matrix = [self.cell]

    @property
    def size(self):
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
        self.matrix.append(self.cell * self.size)

        for row in self.matrix:
            row.append(None)

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
            all(self.matrix[self.size]) and
            all(tuple(zip(*self.matrix))[-1])
        ):
            return self._scale_down()
        else:
            raise ValueError('Невозможно уменьшить размер матрицы, есть непустые элементы')

    def _matrix_scale(self, scale_up: bool) -> MatrixType:
        """
        Функция отвечает за создание увеличенной или уменьшенной матрицы.
        Режим работы зависит от параметра scale_up. На выходе получаем расширенную матрицу.
        :param scale_up: если True, то увеличиваем матрицу, иначе уменьшаем
        :return: измененная матрица
        """
        former_size = len(self.matrix)
        size = former_size + 1 if scale_up else former_size - 1
        new_matrix = [[None for _ in range(size)] for _ in range(size)]
        linear_matrix = [None for _ in range(size ** 2)]

        # Раскладываем элементы матрицы к "плоскому" массиву
        row = 0
        column = 0
        for index in range(len(linear_matrix)):
            item = self.matrix[row][column]
            linear_matrix[index] = item

            column += 1
            if column == former_size:
                column = 0
                row += 1

            if row == former_size:
                break

        # Записываем элементы в новую матрицу
        iterator = iter(linear_matrix)
        try:
            for row in range(len(new_matrix)):
                for column in range(len(new_matrix)):
                    new_matrix[row][column] = next(iterator)

        except StopIteration:
            return new_matrix

        return new_matrix

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
            not_none = tuple(takewhile(lambda x: x is not None, row[::-1]))

            if not_none:
                col_number = len(row) - len(not_none)
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

        last_row, last_column = self.find_first_none_position()

        if last_row * self.size + last_column >= (self.size - 1) ** 2:
            self.matrix = self.matrix_scale(scale_up=True)
            last_row, last_column = self.find_first_none_position()

        self.matrix[last_row][last_column] = element

    def pop(self):
        """
        Удалить последний значащий элемент из массива.
        Если значащих элементов меньше (size - 1) * (size - 2) уменьшить матрицу.
        """
        if self.size == 1:
            raise IndexError()

        last_row, last_column = self.find_last_not_none_position()
        value = self.matrix[last_row][last_column]
        self.matrix[last_row][last_column] = None

        if last_row * self.size + last_column <= (self.size - 1) * (self.size - 2):
            self.matrix = self.matrix_scale(scale_up=False)

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
