from abc import ABC, abstractmethod
from typing import Dict


class Modifier(ABC):
    @abstractmethod
    def modify(self, environ: Dict[str, str]):
        pass


class ModifierApplier(ABC):
    @abstractmethod
    def apply(self, modifier: Modifier):
        pass
