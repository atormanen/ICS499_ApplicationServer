from abc import abstractmethod
from typing import Protocol, runtime_checkable


@runtime_checkable
class ThreadController(Protocol):
    @property
    @abstractmethod
    def error(self) -> BaseException:
        raise NotImplementedError

    @error.setter
    @abstractmethod
    def error(self, value):
        raise NotImplementedError

    @property
    @abstractmethod
    def should_stay_alive(self):
        raise NotImplementedError

    @should_stay_alive.setter
    @abstractmethod
    def should_stay_alive(self, value):
        raise NotImplementedError

    @abstractmethod
    def _wait_until_no_longer_should_stay_alive(self):
        raise NotImplementedError
