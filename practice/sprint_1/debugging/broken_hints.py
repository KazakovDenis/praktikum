from typing import Optional, List


class Matrix:
    """
    Код нашего коллеги аналитика
    Очень медленный и тяжелый для восприятия. Ваша задача сделать его быстрее и проще для понимания.
    """
    def __init__(self):
        self.matrix = [[None]]

    def matrix_scale(self, matrix: List[List[Optional[object]]], scale_up: bool) -> List[List[Optional[object]]]:
        """
        Функция отвечает за создание увеличенной или уменьшенной матрицы.
        Режим работы зависит от параметра scale_up. На выходе получаем расширенную матрицу.
        :param matrix: исходная матрица
        :param scale_up: если True, то увеличиваем матрицу, иначе уменьшаем
        :return: измененная матрица
        """
        former_size = len(matrix)
        size = former_size + 1 if scale_up else former_size - 1
        new_matrix = [[None for _ in range(size)] for _ in range(size)]
        linear_matrix = [None for _ in range(size ** 2)]

        # Раскладываем элементы матрицы к "плоскому" массиву
        row = 0
        column = 0
        for index in range(len(linear_matrix)):
            item = matrix[row][column]
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

    def find_first_none_position(self, matrix) -> (int, int):
        """
        Находим позицию в матрице первого None элемента. По сути он обозначает конец данных матрицы.
        """
        for row in range(len(matrix)):
            for column in range(len(matrix)):
                if matrix[row][column] is None:
                    return row, column

    def find_last_not_none_position(self, matrix):
        """
        Находим позицию последнего не None элемента матрицы.
        """
        for row in range(len(matrix) - 1, -1, -1):
            for column in range(len(matrix) - 1, -1, -1):
                if matrix[row][column] is not None:
                    return row, column

    def add_item(self, element: Optional = None):
        """
        Добавляем новый элемент в матрицу.
        Если элемент не умещается в (size - 1) ** 2, то расширить матрицу.
        """
        if element is None:
            return

        size = len(self.matrix)
        last_row, last_column = self.find_first_none_position(self.matrix)

        if last_row * size + last_column >= (size - 1) ** 2:
            self.matrix = self.matrix_scale(self.matrix, scale_up=True)
            last_row, last_column = self.find_first_none_position(self.matrix)

        self.matrix[last_row][last_column] = element

    def pop(self):
        """
        Удалить последний значащий элемент из массива.
        Если значащих элементов меньше (size - 1) * (size - 2) уменьшить матрицу.
        """
        size = len(self.matrix)
        if size == 1:
            raise IndexError()

        last_row, last_column = self.find_last_not_none_position(self.matrix)
        value = self.matrix[last_row][last_column]
        self.matrix[last_row][last_column] = None

        if last_row * size + last_column <= (size - 1) * (size - 2):
            self.matrix = self.matrix_scale(self.matrix, scale_up=False)

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
