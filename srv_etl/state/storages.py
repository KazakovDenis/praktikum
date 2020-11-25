import abc
import json
import os

import redis


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""


class JsonFileStorage(BaseStorage):

    def __init__(self, file_path: str = ''):
        self.file_path = self.__create_file(file_path)

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        with open(self.file_path, 'w') as file:
            json.dump(state, file, indent=2)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        with open(self.file_path, 'r') as file:
            state = json.load(file)
        return state or {}

    @staticmethod
    def __create_file(path: str) -> str:
        """Создать файл-хранилище"""
        if not os.path.exists(path):
            with open(path, 'x') as f:
                json.dump({}, f)
        return path


class RedisStorage(BaseStorage):

    def __init__(self, redis_conn: redis.Redis):
        self._redis = redis_conn
        self._state = self.retrieve_state()

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        s = json.dumps(state)
        self._redis.set('state', s)

    def retrieve_state(self) -> dict:
        """Загрузить состояние из постоянного хранилища"""
        state = self._redis.get('state')
        if state:
            return json.loads(state)
        return {}
