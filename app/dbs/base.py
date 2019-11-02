from abc import ABC, abstractmethod


class BaseDatabase(ABC):
    def __init__(self, *args, **kwargs):
        self.db = None

        self.init(*args, **kwargs)

    @abstractmethod
    def init(self, **kwargs):
        pass

    @abstractmethod
    def get_val(self, key, **kwargs):
        pass

    @abstractmethod
    def set_val(self, key, value, **kwargs):
        pass

    @abstractmethod
    def del_val(self, key, **kwargs):
        pass
