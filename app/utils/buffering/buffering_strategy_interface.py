# Path: app/utils/buffering/buffering_strategy_interface.py

from abc import ABC, abstractmethod


class BufferingStrategyInterface(ABC):
    @abstractmethod
    def buffer_data(self, data: bytes) -> None:
        pass

    @abstractmethod
    def get_buffered_data(self) -> bytes:
        pass

    @abstractmethod
    def clear_buffer(self) -> None:
        pass