from abc import ABC, abstractmethod
from pathlib import Path

from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive


class DescribedPath(ABC):
    @property
    @abstractmethod
    def primitive(self) -> Path:
        pass

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        pass

    @abstractmethod
    def child(self, child_path_component: str) -> 'DescribedPath':
        pass

    @abstractmethod
    def parent(self) -> 'DescribedPath':
        """Gives a path with the last component removed"""
        pass
