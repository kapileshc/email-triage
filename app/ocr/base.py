from abc import ABC, abstractmethod
from pathlib import Path


class OCREngine(ABC):
    @abstractmethod
    def extract(self, path: Path) -> str:
        raise NotImplementedError
