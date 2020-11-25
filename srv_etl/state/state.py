from typing import Any

from .storages import *


class State:
    """
    Класс для хранения состояния при работе с данным, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределенным хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self._storage = storage
        self._state = storage.retrieve_state()

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определенного ключа"""
        self._state[key] = value
        self._storage.save_state(self._state)

    def get_state(self, key: str) -> Any:
        """Получить состояние по определенному ключу"""
        return self._state.get(key)
