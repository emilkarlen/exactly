from abc import ABC, abstractmethod
from pathlib import Path

from exactly_lib.type_val_prims.path_describer import PathDescriberForPrimitive


class DescribedPath(ABC):
    @property
    @abstractmethod
    def primitive(self) -> Path:
        raise NotImplementedError('abstract method')

    @property
    @abstractmethod
    def describer(self) -> PathDescriberForPrimitive:
        raise NotImplementedError('abstract method')

    @abstractmethod
    def child(self, child_path_component: str) -> 'DescribedPath':
        raise NotImplementedError('abstract method')

    @abstractmethod
    def parent(self) -> 'DescribedPath':
        """Gives a path with the last component removed"""
        raise NotImplementedError('abstract method')
