from abc import ABC, abstractmethod

class Device(ABC):
    @abstractmethod
    async def connect(self): ...

    @abstractmethod
    async def measure(self, channel: str) -> float: ...