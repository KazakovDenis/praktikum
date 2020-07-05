from cProfile import run as profile
from typing import Optional


class Matrix:
    """
    Код нашего коллеги аналитика
    Очень медленный и тяжелый для восприятия. Ваша задача сделать его быстрее и проще для понимания.
    """
    def __init__(self):
        self.matrix = []
        self.size = 1

    def add_item(self, element: Optional = None):
        """
        Добавляем новый элемент в матрицу.
        Если элемент не умещается в (size - 1) ** 2, то расширить матрицу.
        """
        if element is None:
            raise ValueError('Добавляемый элемент не может быть None')

        if len(self.matrix) >= (self.size - 1) ** 2:
            self.size += 1

        self.matrix.append(element)

    def pop(self):
        """
        Удалить последний значащий элемент из массива.
        Если значащих элементов меньше (size - 1) * (size - 2) уменьшить матрицу.
        """
        if self.size == 1:
            raise IndexError('Достигнут минимальный размер матрицы')

        if len(self.matrix) - 1 <= (self.size - 1) * (self.size - 2):
            self.size -= 1

        return self.matrix.pop()

    def __str__(self):
        """
        Метод должен выводить матрицу в виде:
        1 2 3\nNone None None\nNone None None
        То есть между элементами строки должны быть пробелы, а строки отделены \n
        """
        diff = self.size ** 2 - len(self.matrix)
        matrix = self.matrix + [None] * diff

        result = []
        for i in range(self.size):
            start = i * self.size
            end = (i + 1) * self.size
            row = ' '.join(map(lambda x: str(x), matrix[start:end]))
            result.append(row)
        return '\n'.join(result)


def main():
    code = """m = Matrix()\nfor i in range(1000):\n\tm.add_item(i)\nfor i in range(1000):\n\tm.pop()"""
    profile(code, sort=1)


if __name__ == '__main__':
    main()
